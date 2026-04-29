import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

# Functionality to test

# IQRs, block fetch and sequential fetch modes
# Find Invalid Configurations/Protect against them in hardware
# Edge Cases (e.g. max fetch size = 1, max fetch size = 255, etc.)
# Test read/write of all registers, including reserved bits (should be ignored on write, read as 0)
# Test reset behavior (e.g. max fetch size should reset to default value, etc.)
# Test error conditions ( no response from spi flasg, etc.) and that they are properly reported via status register and/or interrupts
# Test SPI interface timing 
# Test 1wc behavior of status flags

# SPI register offsets
SPI_CRTL       = 0x00
SPI_STATUS     = 0x04
MAX_FETCH_SIZE = 0x08
BYTES_FETCHED  = 0x0C
IRQ_EN         = 0x14

async def wb_write(dut, addr, data):
    dut.wb_addr_i.value = addr
    dut.wb_wdata_i.value = data
    dut.wb_we_i.value = 1
    dut.wb_stb_i.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.wb_stb_i.value = 0
    dut.wb_we_i.value = 0

@cocotb.test()
async def test_configure_and_start_spi_read(dut):
    clock = Clock(dut.clk, 10, unit="ns")
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
    await wb_write(dut, MAX_FETCH_SIZE, 0x4)
    
    # enable both interrupts
    await wb_write(dut, IRQ_EN, 0x03)

    # configure block fetch mode + start transfer
    await wb_write(dut, SPI_CRTL, 0x1)

    for _ in range(600):
        await RisingEdge(dut.clk)
