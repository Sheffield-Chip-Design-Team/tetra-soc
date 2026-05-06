import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

async def wb_write(dut, addr, data):
    dut.wb_adr_i.value = addr
    dut.wb_dat_i.value = data
    dut.wb_we_i.value = 1
    dut.wb_stb_i.value = 1
    dut.wb_cyc_i.value = 1
    await RisingEdge(dut.clk)
    # wait for ack
    while not dut.wb_ack_o.value:
        await RisingEdge(dut.clk)
    dut.wb_stb_i.value = 0
    dut.wb_cyc_i.value = 0
    dut.wb_we_i.value = 0
    await RisingEdge(dut.clk)

async def wb_read(dut, addr):
    dut.wb_adr_i.value = addr
    dut.wb_we_i.value = 0
    dut.wb_stb_i.value = 1
    dut.wb_cyc_i.value = 1
    await RisingEdge(dut.clk)
    # wait for ack
    while not dut.wb_ack_o.value:
        await RisingEdge(dut.clk)
    data = dut.wb_dat_o.value
    dut.wb_stb_i.value = 0
    dut.wb_cyc_i.value = 0
    await RisingEdge(dut.clk)
    return data

@cocotb.test()
async def test_ram_read_write(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Initialize
    dut.rst_n.value = 0
    dut.wb_adr_i.value = 0
    dut.wb_dat_i.value = 0
    dut.wb_we_i.value = 0
    dut.wb_stb_i.value = 0
    dut.wb_cyc_i.value = 0

    # Reset
    for _ in range(4):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Test writing to RAM
    test_data = [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0]
    start_addr = 0x4000

    dut._log.info(f"Writing {len(test_data)} bytes to RAM starting at 0x{start_addr:04X}")
    for i, data in enumerate(test_data):
        await wb_write(dut, start_addr + i, data)

    # Test reading from RAM
    dut._log.info("Reading back from RAM to verify")
    for i, expected_data in enumerate(test_data):
        read_data = await wb_read(dut, start_addr + i)
        assert read_data == expected_data, f"Data mismatch at 0x{start_addr+i:04X}: Expected 0x{expected_data:02X}, got 0x{read_data.integer:02X}"
        
    dut._log.info("RAM read/write test passed successfully!")
