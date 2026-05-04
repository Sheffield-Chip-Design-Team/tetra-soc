import cocotb 
from cocotb.triggers import Timer, RisingEdge, FallingEdge


# JTAG instruction encodings
# These match the localparams in jtag_tap.v
IR_IDCODE = 0x1
IR_DBG_CMD = 0x2
IR_DBG_STATUS = 0x3
IR_BYPASS = 0xF

# Debug command encodings
# These match the command values expected by dbg_unit.v
DBG_HALT = 0x01
DBG_RESUME = 0x02
DBG_STEP = 0x03

async def jtag_clock(dut, tms, tdi=0):
    """
    Drive one JTAG TCK cycle.
    
    TMS controls the TAP state transition
    TDI is the serial data input.
    
    The TAP samples TMS/TDI on the rising edge of TCK.
    TDO updates on the falling edge of TCK.
    """

    dut.tms.value = tms
    dut.tdi.value = tdi

    await Timer(1, unit="ns")
    dut.tck.value = 1
    await Timer(1, unit="ns")

    dut.tck.value = 0
    await Timer(1, unit="ns")



async def reset_tap(dut):
    """
    Reset the JTAG TAP into TEST_LOGIC_RESET, then move to RUN_TEST_IDLE.
    """

    dut.tck.value = 0
    dut.tms.value = 1
    dut.tdi.value = 0
    dut.trst_n.value = 0
    dut.dbg_status.value = 0

    # Hold reset for a few TCK cycles
    for _ in range(3):
        await jtag_clock(dut, tms=1, tdi=0)

    # Release reset
    dut.trst_n.value = 1

    # Keep TMS high for a few cycles to guarantee TEST_LOGIC_RESET
    for _ in range(5):
        await jtag_clock(dut, tms=1, tdi=0)

    # Move from TEST_LOGIC_RESET to RUN_TEST_IDLE
    await jtag_clock(dut, tms=0, tdi=0)



async def shift_ir(dut, instruction, width=4):
    """
    Shift a JTAG instruction into the instruction register.
    
    JTAG shifts LSB-first, so instruction bit 0 is shifted first.
    """

    # Current state should be RUN_TEST_IDLE

    # RUN_TEST_IDLE -> SELECT_DR_SCAN
    await jtag_clock(dut, tms=1)

    # SELECT_DR_SCAN -> SELECT_IR_SCAN
    await jtag_clock(dut, tms=1)

    # SELECT_IR_SCAN -> CAPTURE_IR
    await jtag_clock(dut, tms=0)

    # CAPTURE_IR -> SHIFT_IR
    await jtag_clock(dut, tms=0)

    # Shift instruction bits LSB-first
    for bit_index in range(width):
        bit = (instruction >> bit_index) & 1

        # Last bit exits SHIFT_IR
        is_last_bit = bit_index == width - 1
        await jtag_clock(dut, tms=1 if is_last_bit else 0, tdi=bit)

    # EXIT1_IR -> UPDATE_IR
    await jtag_clock(dut, tms=1)

    # UPDATE_IR -> RUN_TEST_IDLE
    # The actual ir_current update happens during this clock in this design
    await jtag_clock(dut, tms=0)



async def shift_dr(dut, data, width):
    """
    Shift data through the selected data register.
    
    JTAG shifts LSB-first, so data bit 0 is shifted first.
    """

    # Current state should be RUN_TEST_IDLE

    # RUN_TEST_IDLE -> SELECT_DR_SCAN
    await jtag_clock(dut, tms=1)

    # SELECT_DR_SCAN -> CAPTURE_DR
    await jtag_clock(dut, tms=0)

    # CAPTURE_DR -> SHIFT_DR
    await jtag_clock(dut, tms=0)

    # Shift data bits LSB-first
    for bit_index in range(width):
        bit = (data >> bit_index) & 1

        # Last bit exits SHIFT_DR
        is_last_bit = bit_index == width - 1
        await jtag_clock(dut, tms=1 if is_last_bit else 0, tdi=bit)

    # EXIT1_DR -> UPDATE_DR
    await jtag_clock(dut, tms=1)

    # UPDATE_DR -> RUN_TEST_IDLE
    # The actual dbg_cmd/dbg_cmd_valid update happens during this clock in this design
    await jtag_clock(dut, tms=0)



async def send_debug_command_via_jtag(dut, cmd):
    """
    Select the DBG_CMD JTAG instruction, then shift an 8-bit debug command
    """

    await shift_ir(dut, IR_DBG_CMD, width=4)
    await shift_dr(dut, cmd, width=8)

    # Small delay so outputs are stable after UPDATE_DR
    await Timer(1, unit="ns")



@cocotb.test()
async def test_jtag_tap_debug_command_path(dut):
    """
    Unit test for src/cpu/jtag_tap.v.
    
    This test checks that a command shifted through the JTAG TAP appears on:
    
    dbg_cmd
    dbg_cmd_valid
    
    It does not test dbg_unit.v yet.
    It only proves the JTAG TAP can receive debug commands.
    """

    await reset_tap(dut)

    # -------------------------------------------------------------------
    # Test 1: Shift HALT command through JTAG
    # -------------------------------------------------------------------
    await send_debug_command_via_jtag(dut, DBG_HALT)

    assert dut.dbg_cmd.value == DBG_HALT, (
        f"Expected dbg_cmd = 0x{DBG_HALT:02x}, got {int(dut.dbg_cmd.value):#04x}"
    )

    assert dut.dbg_cmd_valid.value == 1, (
        "dbg_cmd_valid was not asserted after HALT command"
    )

    # dbg_cmd_valid should be a one-TCK-cycle pulse
    await jtag_clock(dut, tms=0)

    assert dut.dbg_cmd_valid.value == 0, (
        "dbg_cmd_valid did not return low after one TCK cycle"
    )

    # -------------------------------------------------------------------
    # Test 2: shift RESUME command through JTAG
    # -------------------------------------------------------------------
    await send_debug_command_via_jtag(dut, DBG_RESUME)

    assert dut.dbg_cmd.value == DBG_RESUME, (
        f"Expected dbg_cmd = 0x{DBG_RESUME:02x}, got {int(dut.dbg_cmd.value):#04x}"
    )

    assert dut.dbg_cmd_valid.value == 1, (
        "dbg_cmd_valid was not asserted after RESUME command"
    )

    await jtag_clock(dut, tms=0)

    assert dut.dbg_cmd_valid.value == 0, (
        "dbg_cmd_valid did not return low after one TCK cycle"
    )

    # -------------------------------------------------------------------
    # Test 3: shift STEP command through JTAG
    # -------------------------------------------------------------------
    await send_debug_command_via_jtag(dut, DBG_STEP)

    assert dut.dbg_cmd.value == DBG_STEP, (
        f"Expected dbg_cmd = 0x{DBG_STEP:02x}, got {int(dut.dbg_cmd.value):#04x}"
    )

    assert dut.dbg_cmd_valid.value == 1, (
        "dbg_cmd_valid was not asserted after STEP command"
    )

    await jtag_clock(dut, tms=0)

    assert dut.dbg_cmd_valid.value == 0, (
        "dbg_cmd_valid did not return low after one TCK cycle"
    )