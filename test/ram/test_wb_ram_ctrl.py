import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.wb_addr_i.value = 0
    dut.wb_wdata_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0

    for _ in range(3):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1

    for _ in range(2):
        await RisingEdge(dut.clk)


async def wb_write(dut, addr, data):
    dut.wb_addr_i.value = addr
    dut.wb_wdata_i.value = data
    dut.wb_we_i.value = 1
    dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1

    await Timer(1, unit="ns")

    assert int(dut.wb_ack_o.value) == 1, (
        f"Wishbone write did not ACK at addr 0x{addr:02X}"
    )

    await RisingEdge(dut.clk)

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_we_i.value = 0

    await RisingEdge(dut.clk)


async def wb_read(dut, addr):
    dut.wb_addr_i.value = addr
    dut.wb_wdata_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1

    await Timer(1, unit="ns")

    assert int(dut.wb_ack_o.value) == 1, (
        f"Wishbone read did not ACK at addr 0x{addr:02X}"
    )

    data = int(dut.wb_rdata_o.value)

    await RisingEdge(dut.clk)

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0

    await RisingEdge(dut.clk)

    return data


@cocotb.test()
async def test_reset_idle(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    assert int(dut.wb_ack_o.value) == 0, "ACK should be low when bus is idle"


@cocotb.test()
async def test_single_write_read(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    await wb_write(dut, 0x10, 0xAB)
    got = await wb_read(dut, 0x10)

    assert got == 0xAB, (
        f"Single readback failed: got 0x{got:02X}, expected 0xAB"
    )


@cocotb.test()
async def test_multiple_addresses(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    test_vectors = {
        0x00: 0x12,
        0x01: 0x34,
        0x7F: 0x56,
        0x80: 0x78,
        0xFF: 0x9A,
    }

    for addr, data in test_vectors.items():
        await wb_write(dut, addr, data)

    for addr, expected in test_vectors.items():
        got = await wb_read(dut, addr)
        assert got == expected, (
            f"RAM mismatch at addr 0x{addr:02X}: "
            f"got 0x{got:02X}, expected 0x{expected:02X}"
        )


@cocotb.test()
async def test_overwrite_same_address(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    await wb_write(dut, 0x22, 0x11)
    got_first = await wb_read(dut, 0x22)
    assert got_first == 0x11, (
        f"Initial write failed: got 0x{got_first:02X}, expected 0x11"
    )

    await wb_write(dut, 0x22, 0xEE)
    got_second = await wb_read(dut, 0x22)

    assert got_second == 0xEE, (
        f"Overwrite failed: got 0x{got_second:02X}, expected 0xEE"
    )


@cocotb.test()
async def test_idle_no_ack(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_dut(dut)

    dut.wb_cyc_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_we_i.value = 0

    await Timer(1, unit="ns")

    assert int(dut.wb_ack_o.value) == 0, "ACK should remain low with no bus request"
