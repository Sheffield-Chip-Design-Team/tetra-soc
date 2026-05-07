import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


CTI_CLASSIC = 0b000
CTI_INCREMENTING_BURST = 0b010
CTI_END_OF_BURST = 0b111
BTE_LINEAR = 0b00


async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.wb_addr_i.value = 0
    dut.wb_wdata_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_cti_i.value = CTI_CLASSIC
    dut.wb_bte_i.value = BTE_LINEAR

    for _ in range(3):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1

    for _ in range(2):
        await RisingEdge(dut.clk)


async def wb_write(dut, addr, data, cti=CTI_CLASSIC):
    dut.wb_addr_i.value = addr
    dut.wb_wdata_i.value = data
    dut.wb_we_i.value = 1
    dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1
    dut.wb_cti_i.value = cti
    dut.wb_bte_i.value = BTE_LINEAR

    await Timer(1, unit="ns")
    assert int(dut.wb_ack_o.value) == 0, "Write ACK should be registered, not combinational"
    assert int(dut.wb_err_o.value) == 0, "Write ERR should be registered, not combinational"

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.wb_ack_o.value) == 1, (
        f"Wishbone write did not ACK after clock at addr 0x{addr:04X}"
    )
    assert int(dut.wb_err_o.value) == 0, (
        f"Wishbone write unexpectedly errored at addr 0x{addr:04X}"
    )

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_cti_i.value = CTI_CLASSIC

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def wb_read(dut, addr, cti=CTI_CLASSIC):
    dut.wb_addr_i.value = addr
    dut.wb_wdata_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1
    dut.wb_cti_i.value = cti
    dut.wb_bte_i.value = BTE_LINEAR

    await Timer(1, unit="ns")
    assert int(dut.wb_ack_o.value) == 0, "Read ACK should be registered, not combinational"
    assert int(dut.wb_err_o.value) == 0, "Read ERR should be registered, not combinational"

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.wb_ack_o.value) == 1, (
        f"Wishbone read did not ACK after clock at addr 0x{addr:04X}"
    )
    assert int(dut.wb_err_o.value) == 0, (
        f"Wishbone read unexpectedly errored at addr 0x{addr:04X}"
    )

    data = int(dut.wb_rdata_o.value)

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_cti_i.value = CTI_CLASSIC

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    return data


async def wb_invalid_access(dut, addr, write=False, data=0):
    dut.wb_addr_i.value = addr
    dut.wb_wdata_i.value = data
    dut.wb_we_i.value = 1 if write else 0
    dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1
    dut.wb_cti_i.value = CTI_CLASSIC
    dut.wb_bte_i.value = BTE_LINEAR

    await Timer(1, unit="ns")
    assert int(dut.wb_ack_o.value) == 0, "Invalid access ACK should be registered"
    assert int(dut.wb_err_o.value) == 0, "Invalid access ERR should be registered"

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.wb_ack_o.value) == 0, (
        f"Out-of-range access should not ACK at addr 0x{addr:04X}"
    )
    assert int(dut.wb_err_o.value) == 1, (
        f"Out-of-range access should assert ERR at addr 0x{addr:04X}"
    )

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_we_i.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def wb_burst_write(dut, start_addr, values):
    dut.wb_we_i.value = 1
    dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1
    dut.wb_bte_i.value = BTE_LINEAR

    for index, data in enumerate(values):
        addr = start_addr + index
        is_last = index == len(values) - 1

        dut.wb_addr_i.value = addr
        dut.wb_wdata_i.value = data
        dut.wb_cti_i.value = CTI_END_OF_BURST if is_last else CTI_INCREMENTING_BURST

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        assert int(dut.wb_ack_o.value) == 1, (
            f"Burst write did not ACK at addr 0x{addr:04X}"
        )
        assert int(dut.wb_err_o.value) == 0, (
            f"Burst write errored at addr 0x{addr:04X}"
        )

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_cti_i.value = CTI_CLASSIC

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def wb_burst_read(dut, start_addr, length):
    values = []

    dut.wb_we_i.value = 0
    dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1
    dut.wb_bte_i.value = BTE_LINEAR

    for index in range(length):
        addr = start_addr + index
        is_last = index == length - 1

        dut.wb_addr_i.value = addr
        dut.wb_wdata_i.value = 0
        dut.wb_cti_i.value = CTI_END_OF_BURST if is_last else CTI_INCREMENTING_BURST

        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        assert int(dut.wb_ack_o.value) == 1, (
            f"Burst read did not ACK at addr 0x{addr:04X}"
        )
        assert int(dut.wb_err_o.value) == 0, (
            f"Burst read errored at addr 0x{addr:04X}"
        )

        values.append(int(dut.wb_rdata_o.value))

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_cti_i.value = CTI_CLASSIC

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    return values


@cocotb.test()
async def test_reset_idle(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    assert int(dut.wb_ack_o.value) == 0, "ACK should be low when bus is idle"
    assert int(dut.wb_err_o.value) == 0, "ERR should be low when bus is idle"


@cocotb.test()
async def test_read_response_is_clocked(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await wb_write(dut, 0x0004, 0x3C)

    dut.wb_addr_i.value = 0x0004
    dut.wb_wdata_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1
    dut.wb_cti_i.value = CTI_CLASSIC
    dut.wb_bte_i.value = BTE_LINEAR

    await Timer(1, unit="ns")
    assert int(dut.wb_ack_o.value) == 0, "Read ACK should not be combinational"

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.wb_ack_o.value) == 1, "Read ACK should assert after clock edge"
    assert int(dut.wb_rdata_o.value) == 0x3C, "Clocked read returned wrong data"

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0

    await RisingEdge(dut.clk)


@cocotb.test()
async def test_single_write_read(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await wb_write(dut, 0x0010, 0xAB)
    got = await wb_read(dut, 0x0010)

    assert got == 0xAB, (
        f"Single readback failed: got 0x{got:02X}, expected 0xAB"
    )


@cocotb.test()
async def test_multiple_addresses(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_vectors = {
        0x0000: 0x12,
        0x0001: 0x34,
        0x007F: 0x56,
        0x0080: 0x78,
        0x00FF: 0x9A,
    }

    for addr, data in test_vectors.items():
        await wb_write(dut, addr, data)

    for addr, expected in test_vectors.items():
        got = await wb_read(dut, addr)
        assert got == expected, (
            f"RAM mismatch at addr 0x{addr:04X}: "
            f"got 0x{got:02X}, expected 0x{expected:02X}"
        )


@cocotb.test()
async def test_overwrite_same_address(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await wb_write(dut, 0x0022, 0x11)
    got_first = await wb_read(dut, 0x0022)
    assert got_first == 0x11

    await wb_write(dut, 0x0022, 0xEE)
    got_second = await wb_read(dut, 0x0022)

    assert got_second == 0xEE, (
        f"Overwrite failed: got 0x{got_second:02X}, expected 0xEE"
    )


@cocotb.test()
async def test_burst_write_read(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    values = [0xA1, 0xB2, 0xC3, 0xD4]
    await wb_burst_write(dut, 0x0030, values)

    got_values = await wb_burst_read(dut, 0x0030, len(values))

    assert got_values == values, (
        f"Burst readback failed: got {got_values}, expected {values}"
    )


@cocotb.test()
async def test_out_of_range_read_error(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await wb_invalid_access(dut, 0x0100, write=False)


@cocotb.test()
async def test_out_of_range_write_error_and_no_wrap(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await wb_write(dut, 0x0000, 0x55)
    await wb_invalid_access(dut, 0x0100, write=True, data=0xAA)

    got = await wb_read(dut, 0x0000)
    assert got == 0x55, (
        f"Invalid write wrapped into RAM[0x00]: got 0x{got:02X}"
    )


@cocotb.test()
async def test_idle_no_ack_no_err(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_we_i.value = 0

    await Timer(1, unit="ns")

    assert int(dut.wb_ack_o.value) == 0, "ACK should remain low with no bus request"
    assert int(dut.wb_err_o.value) == 0, "ERR should remain low with no bus request"
