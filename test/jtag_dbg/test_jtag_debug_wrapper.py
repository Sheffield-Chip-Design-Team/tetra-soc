import cocotb 
from cocotb.triggers import Timer



# JTAG instruction encodings
# These match jtag_tap.v
IR_DBG_CMD = 0x2

# Debug command encodings
# These match dbg_unit.v
DBG_HALT = 0x01
DBG_RESUME = 0x02
DBG_STEP = 0x03



async def jtag_clock(dut, tms, tdi=0):
    """
    Drive one JTAG TCK cycle.
    
    The TAP samples TMS and TDI on the rising edge of TCK.
    TDO updates on the falling edge, but this test mainly checks outputs
    from the debug command path, not TDO readback.
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
    Reset the JTAG TAP and move it into RUN_TEST_IDLE
    """

    dut.tck.value = 0
    dut.tms.value = 1
    dut.tdi.value = 0
    dut.trst_n.value = 0
    dut.dbg_status.value = 0

    # Hold reset for a few JTAG clocks
    for _ in range(3):
        await jtag_clock(dut, tms=1, tdi=0)

    # Release active-low reset
    dut.trst_n.value = 1

    # Keep TMS high for several cycles to force TEST_LOGIC_RESET
    for _ in range(5):
        await jtag_clock(dut, tms=1, tdi=0)

    # Move from TEST_LOGIC_RESET to RUN_TEST_IDLE
    await jtag_clock(dut, tms=0, tdi=0)



async def shift_ir(dut, instruction, width=4):
    """
    Shift a JTAG instruction into the instruction register.
    
    JTAG shifts LSB-first, so bit 0 is shifted first.
    """

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
        is_last_bit = bit_index == width - 1

        # On the last bit, TMS=1 exits SHIFT_IR to EXIT1_IR
        await jtag_clock(dut, tms=1 if is_last_bit else 0, tdi=bit)

    # EXIT1_IR -> UPDATE_IR
    await jtag_clock(dut, tms=1)

    # UPDATE_IR -> RUN_TEST_IDLE
    await jtag_clock(dut, tms=0)



async def shift_dr(dut, data, width):
    """
    Shift data through the currently selected data register.
    
    JTAG shifts LSB-first, so bit 0 is shifted first.
    """

    # RUN_TEST_IDLE -> SELECT_DR_SCAN
    await jtag_clock(dut, tms=1)

    # SELECT_DR_SCAN -> CAPTURE_DR
    await jtag_clock(dut, tms=0)

    # CAPTURE_DR -> SHIFT_DR
    await jtag_clock(dut, tms=0)

    # Shift data bits LSB-first
    for bit_index in range(width):
        bit = (data >> bit_index) & 1
        is_last_bit = bit_index == width - 1

        # On the last bit, TMS=1 exits SHIFT_DR to EXIT1_DR
        await jtag_clock(dut, tms=1 if is_last_bit else 0, tdi=bit)

    # EXIT1_DR -> UPDATE_DR
    await jtag_clock(dut, tms=1)

    # UPDATE_DR -> RUN_TEST_IDLE
    await jtag_clock(dut, tms=0)

    # Small delay for wrapper outputs to settle
    await Timer(1, unit="ns")



async def send_debug_command_via_jtag(dut, cmd):
    """
    Select the DBG_CMD JTAG instruction and shift an 8-bit debug command.
    """

    await shift_ir(dut, IR_DBG_CMD, width=4)
    await shift_dr(dut, cmd, width=8)



async def check_request_pulse(dut, cmd, expected_signal_name):
    """
    Send one JTAG debug command and check that the correct debug request pulses.
    
    Example:
    cmd = DBG_HALT
    expected_signal_name = "halt_req"
    
    Expected:
    halt_req = 1
    resume_req = 0
    step_req = 0
    """

    await send_debug_command_via_jtag(dut, cmd)

    await jtag_clock(dut, tms=0)

    expected_signal = getattr(dut, expected_signal_name)

    assert expected_signal.value == 1, (
        f"{expected_signal_name} was not asserted for JTAG command 0x{cmd:02x}"
    )

    for signal_name in ["halt_req", "resume_req", "step_req"]:
        signal = getattr(dut, signal_name)

        if signal_name != expected_signal_name:
            assert signal.value == 0, (
                f"{signal_name} was incorrectly asserted for JTAG command 0x{cmd:02x}"
            )
    
    # Requests should be one-TCK-cycle pulse
    await jtag_clock(dut, tms=0)

    assert expected_signal.value == 0, (
        f"{expected_signal_name} did not return low after one TCK cycle"
    )



@cocotb.test()
async def test_jtag_command_to_debug_request(dut):
    """
    Integration test for:

    jtag_tap.v -> dbg_unit.v

    This checks:
    - JTAG command 0x01 produces halt_req
    - JTAG command 0x02 produces resume_req
    - JTAG command 0x03 produces step_req

    This still does not test CPU halt/step/resume behaviour.
    It only tests the debug front-end chain.
    """

    await reset_tap(dut)

    await check_request_pulse(dut, DBG_HALT, "halt_req")
    await check_request_pulse(dut, DBG_RESUME, "resume_req")
    await check_request_pulse(dut, DBG_STEP, "step_req")