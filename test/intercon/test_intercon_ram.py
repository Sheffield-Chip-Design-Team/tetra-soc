import cocotb
from cocotb.triggers import RisingEdge, Timer

CTI_CLASSIC = 0
BTE_LINEAR = 0

# RAM is mapped at 0x8000 in the interconnect memory map.
# The RAM window is 4KiB: 0x8000 - 0x8FFF.
RAM_BASE = 0x0000_8000


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

    async def write(self, addr: int, data: int, timeout_cycles: int = 80):
        self.dut.wb_cpu_s_adr_i.value = addr & 0xFFFFFFFF
        self.dut.wb_cpu_s_dat_i.value = data & 0xFF
        self.dut.wb_cpu_s_we_i.value = 1
        self.dut.wb_cpu_s_cti_i.value = CTI_CLASSIC
        self.dut.wb_cpu_s_bte_i.value = BTE_LINEAR
        self.dut.wb_cpu_s_cyc_i.value = 1
        self.dut.wb_cpu_s_stb_i.value = 1

        for _ in range(timeout_cycles):
            await RisingEdge(self.clk)

            if int(self.dut.wb_cpu_s_err_o.value) == 1:
                raise AssertionError(f"WB write error @0x{addr:08X}")

            if int(self.dut.wb_cpu_s_ack_o.value) == 1:
                break
        else:
            raise AssertionError(f"WB write timeout @0x{addr:08X}")

        self.dut.wb_cpu_s_cyc_i.value = 0
        self.dut.wb_cpu_s_stb_i.value = 0
        self.dut.wb_cpu_s_we_i.value = 0
        await RisingEdge(self.clk)

    async def read(self, addr: int, timeout_cycles: int = 80) -> int:
        self.dut.wb_cpu_s_adr_i.value = addr & 0xFFFFFFFF
        self.dut.wb_cpu_s_we_i.value = 0
        self.dut.wb_cpu_s_cti_i.value = CTI_CLASSIC
        self.dut.wb_cpu_s_bte_i.value = BTE_LINEAR
        self.dut.wb_cpu_s_cyc_i.value = 1
        self.dut.wb_cpu_s_stb_i.value = 1

        for _ in range(timeout_cycles):
            await RisingEdge(self.clk)

            if int(self.dut.wb_cpu_s_err_o.value) == 1:
                raise AssertionError(f"WB read error @0x{addr:08X}")

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


async def wait_reset_deasserted(dut, cycles: int = 30):
    for _ in range(cycles):
        await RisingEdge(dut.sys_clk)
        if int(dut.sys_rst_n.value) == 1:
            await Timer(1, unit="ns")
            return
    raise AssertionError("Reset did not deassert")


@cocotb.test()
async def test_cpu_to_ram_single_write_read(dut):
    """CPU-side Wishbone write/read reaches RAM through the interconnect."""

    wb = Wb8CpuSlaveDriver(dut)
    await wb.reset_bus()
    await wait_reset_deasserted(dut)

    addr = RAM_BASE
    expected = 0xA5

    await wb.write(addr, expected)
    got = await wb.read(addr)

    assert got == expected, (
        f"CPU-side RAM readback failed @0x{addr:08X}: "
        f"got 0x{got:02X}, expected 0x{expected:02X}"
    )


@cocotb.test()
async def test_cpu_to_ram_multiple_addresses(dut):
    """Check multiple CPU-side RAM accesses through intercon_ss."""

    wb = Wb8CpuSlaveDriver(dut)
    await wb.reset_bus()
    await wait_reset_deasserted(dut)

    vectors = {
        RAM_BASE + 0x00: 0x12,
        RAM_BASE + 0x01: 0x34,
        RAM_BASE + 0x02: 0x56,
        RAM_BASE + 0x10: 0x9A,
    }

    for addr, data in vectors.items():
        await wb.write(addr, data)

    for addr, expected in vectors.items():
        got = await wb.read(addr)
        assert got == expected, (
            f"RAM mismatch @0x{addr:08X}: "
            f"got 0x{got:02X}, expected 0x{expected:02X}"
        )


@cocotb.test()
async def test_cpu_to_ram_port_is_selected(dut):
    """Check that RAM-mapped CPU access selects the RAM interconnect port."""

    wb = Wb8CpuSlaveDriver(dut)
    await wb.reset_bus()
    await wait_reset_deasserted(dut)

    addr = RAM_BASE + 0x20

    dut.wb_cpu_s_adr_i.value = addr
    dut.wb_cpu_s_dat_i.value = 0xC3
    dut.wb_cpu_s_we_i.value = 1
    dut.wb_cpu_s_cti_i.value = CTI_CLASSIC
    dut.wb_cpu_s_bte_i.value = BTE_LINEAR
    dut.wb_cpu_s_cyc_i.value = 1
    dut.wb_cpu_s_stb_i.value = 1

    seen_ram_cycle = False
    seen_ram_write = False
    seen_ram_data = False

    for _ in range(80):
        await RisingEdge(dut.sys_clk)

        if int(dut.wb_ram_cyc_o.value) == 1 and int(dut.wb_ram_stb_o.value) == 1:
            seen_ram_cycle = True

            if int(dut.wb_ram_we_o.value) == 1:
                seen_ram_write = True

            if int(dut.wb_ram_dat_o.value) == 0xC3:
                seen_ram_data = True

        if int(dut.wb_cpu_s_ack_o.value) == 1:
            break
    else:
        raise AssertionError("CPU-side ack not seen for RAM write")

    dut.wb_cpu_s_cyc_i.value = 0
    dut.wb_cpu_s_stb_i.value = 0
    dut.wb_cpu_s_we_i.value = 0

    await RisingEdge(dut.sys_clk)

    assert seen_ram_cycle, "RAM port was not selected for RAM-mapped CPU access"
    assert seen_ram_write, "RAM port did not see a write transaction"
    assert seen_ram_data, "RAM port did not see the expected write data"
