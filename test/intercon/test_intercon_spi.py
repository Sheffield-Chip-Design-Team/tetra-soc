import cocotb
from cocotb.triggers import RisingEdge, Timer

CTI_CLASSIC = 0
BTE_LINEAR = 0

class Wb8CpuSlaveDriver:
    def __init__(self, dut):
        self.dut = dut
        self.clk = dut.sys_clk

    async def reset_bus(self):
        self.dut.wb_cpu_s_adr_i.value = 0
        self.dut.wb_cpu_s_dat_i.value = 0
        self.dut.wb_cpu_s_we_i.value = 0
        self.dut.wb_cpu_s_cyc_i.value = 0
        self.dut.wb_cpu_s_stb_i.value = 0
        self.dut.wb_cpu_s_cti_i.value = CTI_CLASSIC
        self.dut.wb_cpu_s_bte_i.value = BTE_LINEAR
        await RisingEdge(self.clk)

    async def write(self, addr: int, data: int, timeout_cycles: int = 50):
        self.dut.wb_cpu_s_adr_i.value = addr & 0xFFFFFFFF
        self.dut.wb_cpu_s_dat_i.value = data & 0xFF
        self.dut.wb_cpu_s_we_i.value = 1
        self.dut.wb_cpu_s_cti_i.value = CTI_CLASSIC
        self.dut.wb_cpu_s_bte_i.value = BTE_LINEAR
        self.dut.wb_cpu_s_cyc_i.value = 1
        self.dut.wb_cpu_s_stb_i.value = 1

        for _ in range(timeout_cycles):
            await RisingEdge(self.clk)
            if int(self.dut.wb_cpu_s_ack_o.value) == 1:
                break
        else:
            raise AssertionError(f"WB write timeout @0x{addr:08X}")

        # Deassert
        self.dut.wb_cpu_s_cyc_i.value = 0
        self.dut.wb_cpu_s_stb_i.value = 0
        self.dut.wb_cpu_s_we_i.value = 0
        await RisingEdge(self.clk)

    async def read(self, addr: int, timeout_cycles: int = 50) -> int:
        self.dut.wb_cpu_s_adr_i.value = addr & 0xFFFFFFFF
        self.dut.wb_cpu_s_we_i.value = 0
        self.dut.wb_cpu_s_cti_i.value = CTI_CLASSIC
        self.dut.wb_cpu_s_bte_i.value = BTE_LINEAR
        self.dut.wb_cpu_s_cyc_i.value = 1
        self.dut.wb_cpu_s_stb_i.value = 1

        for _ in range(timeout_cycles):
            await RisingEdge(self.clk)
            if int(self.dut.wb_cpu_s_ack_o.value) == 1:
                val = self.dut.wb_cpu_s_dat_o.value
                assert val.is_resolvable, f"Read data X/Z @0x{addr:08X}: {val}"
                data = int(val) & 0xFF
                break
        else:
            raise AssertionError(f"WB read timeout @0x{addr:08X}")

        self.dut.wb_cpu_s_cyc_i.value = 0
        self.dut.wb_cpu_s_stb_i.value = 0
        await RisingEdge(self.clk)
        return data


async def wait_reset_deasserted(dut, cycles: int = 20):
    for _ in range(cycles):
        await RisingEdge(dut.sys_clk)
        if int(dut.sys_rst_n.value) == 1:
            return
    raise AssertionError("Reset did not deassert")


@cocotb.test()
async def test_cpu_to_spi_m_write_and_ack(dut):
    """Verify CPU WB8 transactions reach the SPI-m peripheral port."""

    wb = Wb8CpuSlaveDriver(dut)
    await wb.reset_bus()

    await wait_reset_deasserted(dut)
    await Timer(1, unit="ns")

    # Write MAX_FETCH_SIZE (addr 0x08 in SPI register map)
    await wb.write(0x0000_0008, 0x01)

    # The interconnect maps SPI-m at base 0x0000_0000; verify bus activity for SPI_CTRL write
    # We'll observe the SPI-m port during the write.
    seen = {
        "cycle": False,
        "we": False,
        "dat": False,
        "adr": False,
    }

    # Start a write to SPI_CTRL (addr 0x00): start pulse=1, fetch_mode=0
    dut.wb_cpu_s_adr_i.value = 0x0000_0000
    dut.wb_cpu_s_dat_i.value = 0x01
    dut.wb_cpu_s_we_i.value = 1
    dut.wb_cpu_s_cti_i.value = CTI_CLASSIC
    dut.wb_cpu_s_bte_i.value = BTE_LINEAR
    dut.wb_cpu_s_cyc_i.value = 1
    dut.wb_cpu_s_stb_i.value = 1

    for _ in range(50):
        await RisingEdge(dut.sys_clk)

        if int(dut.wb_spi_m_cyc_o.value) == 1 and int(dut.wb_spi_m_stb_o.value) == 1:
            seen["cycle"] = True
            if int(dut.wb_spi_m_we_o.value) == 1:
                seen["we"] = True
            if int(dut.wb_spi_m_dat_o.value) == 0x01:
                seen["dat"] = True
            if int(dut.wb_spi_m_adr_o.value) & 0x1F == 0x00:
                seen["adr"] = True

        if int(dut.wb_cpu_s_ack_o.value) == 1:
            break
    else:
        raise AssertionError("CPU-side ack not seen for SPI_CTRL write")

    # Deassert
    dut.wb_cpu_s_cyc_i.value = 0
    dut.wb_cpu_s_stb_i.value = 0
    dut.wb_cpu_s_we_i.value = 0
    await RisingEdge(dut.sys_clk)

    assert all(seen.values()), f"Did not observe expected SPI-m bus write: {seen}"


@cocotb.test()
async def test_spi_transaction_starts(dut):
    """Kick the SPI controller via the interconnect and check CS_n goes low."""

    wb = Wb8CpuSlaveDriver(dut)
    await wb.reset_bus()
    await wait_reset_deasserted(dut)

    # Set MAX_FETCH_SIZE = 16 (addr 0x08)
    await wb.write(0x0000_0008, 0x10)

    # Start single fetch (SPI_CTRL addr 0x00, bit0=start pulse, bit1=fetch_mode)
    await wb.write(0x0000_0000, 0x01)

    # CS_n should go low at least once shortly after
    cs_low = False
    for _ in range(200):
        await RisingEdge(dut.sys_clk)
        val = dut.spi_cs_n.value
        if val.is_resolvable and int(val) == 0:
            cs_low = True
            break

    assert cs_low, "SPI CS_n never went low (SPI transaction didn't start)"

    # Optional: SPI_STATUS busy bit should eventually return to 0
    # SPI_STATUS at 0x04: bit0=busy
    for _ in range(500):
        status = await wb.read(0x0000_0004)
        busy = status & 0x01
        if busy == 0:
            return
        await RisingEdge(dut.sys_clk)

    raise AssertionError("SPI controller stayed busy too long")
    
