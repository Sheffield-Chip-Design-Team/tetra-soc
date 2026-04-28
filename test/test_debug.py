import cocotb
from cocotb.clock import Clock 
from cocotb.triggers import RisingEdge, Timer


# Debug command encodings that match the localparams used inside debug.v
DBG_NOP = 0x00
DBG_HALT = 0x01
DBG_RESUME = 0x02
DBG_STEP = 0x03


async def reset_dut(dut):

    """ 

    Reset the debug module into a known starting state.

    During reset:
    - rst_n is held low
    - no command is being sent
    - dbg_cmd is cleared to NOP
    """

    dut.rst_n.value = 0
    dut.dbg_cmd.value = 0
    dut.dbg_cmd_valid.value = 0

    # Hold reset for two clock cycles to ensure reset
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Release reset and wait one more clock edge before testing
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Small delay allows registered outputs to settle after clock edge
    await Timer(1, units="ns")


async def send_cmd(dut, cmd):

    """
    Send one debug command into debug.v

    dbg_cmd_valid is held high for one clock cycle.
    debug.v should sample dbg_cmd on the rising clock edge and produce 
    the corresponding one-cycle request pulse.
    """

    dut.dbg_cmd.value = cmd
    dut.dbg_cmd_valid.value = 1

    # Command is sampled by debug.v on this rising edge
    await RisingEdge(dut.clk)

    # Small delay so outputs can be checked after clock edge
    await Timer(1, units="ns")

    # Clear command inputs after one cycle
    dut.dbg_cmd_valid.value = 0
    dut.dbg_cmd.value = 0


async def check_one_cycle_pulse(dut, cmd, expected_signal_name):
    """
    Send a command and check that only the expected request output pulses.

    Example:
    - cmd = DBG_HALT
    - expected_signal_name = "halt_req"

    The test checks:
    1. the expected signal goes high
    2. the other request signals stay low
    3. the expected signal returns low after one clock cycle
    """

    await send_cmd(dut, cmd)
    
    expected_signal = getattr(dut, expected_signal_name)

    # The correct requesteed output should assert
    assert expected_signal.value == 1, (
        f"{expected_signal_name} was not asserted for command {cmd:#04x}"
    )

    # The other request outputs should not assert
    for signal_name in ["halt_req", "resume_req", "step_req"]:
        signal = getattr(dut, signal_name)

        if signal_name != expected_signal_name:
            assert signal.value == 0, (
                f"{signal_name} was incorrectly asserted for command {cmd:#04x}"
            )

    # On the next clock edge, the request pulse should return low
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert expected_signal.value == 0, (
        f"{expected_signal_name} did not return low after one cycle"
    )


@cocotb.test()
async def test_debug_command_decoder(dut):
    """
    Unit test for debug.v.

    This test checks that debug.v correctly decodes simple debug commands:

    - DBG_HALT should pulse halt_req
    - DBG_RESUME should pulse resume_req
    - DBG_STEP should pulse step_req
    - NOP/unknown commands should not assert any request

    This does not test whether the CPU actually halts or steps yet.
    It only tests the command decoder block.
    """

    # Start a 10ns period clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Put DUT into a known state before applying commands
    await reset_dut(dut)

    # Check valid debug commands
    await check_one_cycle_pulse(dut, DBG_HALT, "halt_req")
    await check_one_cycle_pulse(dut, DBG_RESUME, "resume_req")
    await check_one_cycle_pulse(dut, DBG_STEP, "step_req")

    # Check that NOP and unknown commands do not accidentally trigger requests
    for cmd in [DBG_NOP, 0xFF, 0xAA]:
        await send_cmd(dut, cmd)

        assert dut.halt_req.value == 0, f"Command {cmd:#04x} incorrectly asserted halt_req"
        assert dut.resume_req.value == 0, f"Command {cmd:#04x} incorrectly asserted resume_req"
        assert dut.step_req.value == 0, f"Command {cmd:#04x} incorrectly asserted step_req"

        await RisingEdge(dut.clk)
        await Timer(1, units="ns")