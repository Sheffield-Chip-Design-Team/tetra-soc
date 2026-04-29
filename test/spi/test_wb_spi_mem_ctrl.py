import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

async def wb_write(dut, addr, data):
    dut.wb_addr_i.value = addr
    dut.wb_wdata_i.value = data
    dut.wb_we_i.value = 1
    dut.wb_stb_i.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    dut.wb_stb_i.value = 0
    dut.wb_we_i.value = 0

@cocotb.test()
async def test_configure_and_start_spi_read(dut):
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.wb_addr_i.value = 0
    dut.wb_wdata_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_stb_i.value = 0
    dut.miso.value = 0

    for _ in range(4):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Set max fetch bytes to 255
    await wb_write(dut, 0x08, 0x4)
    
    # enable both interrupts
    await wb_write(dut, 0x14, 0x03)

    # configure block fetch mode + start transfer
    await wb_write(dut, 0x00, 0x03)

    for _ in range(600):
        await RisingEdge(dut.clk)
