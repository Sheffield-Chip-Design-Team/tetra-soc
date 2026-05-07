import cocotb
from cocotb.triggers import Timer

###################################################
## Copy and paste code into test_control_unit.py ##
###################################################

# -------------------------
# Helper functions
# -------------------------

def alu_int(dut):
    return int(dut.alu_control.value)

async def settle():
    # Matches your timing style: allow combinational logic to settle
    await Timer(1, units="ns")

async def setup_dut(dut):
    dut.instruction.value = 0
    dut.flags.value = 0
    await settle()

# -------------------------
# Test 1: ADD / SUB group
# -------------------------

async def test_add_sub(dut):        ## This is the format you should be using, thomas:

    dut._log.info("Starting ADD / SUB control test")

    dut.instruction.value = 0x01    # Tests the case that the instruction is implicit add
    await Timer(5, units="ns")      # Allows logic to propegate
    dut._log.info(f"Add Imp: {dut.alu_control.Value}")

    dut.instruction.value = 0x11    # Tests the case that the instruction is implicit add
    await Timer(5, units="ns")      # Allows logic to propegate
    dut._log.info(f"Sub Imp: {dut.alu_control.Value}")

    dut.instruction.value = 0x81    # Tests the case that the instruction is implicit add
    await Timer(5, units="ns")      # Allows logic to propegate
    dut._log.info(f"Add Imm: {dut.alu_control.Value}")

    dut.instruction.value = 0x91    # Tests the case that the instruction is implicit add
    await Timer(5, units="ns")      # Allows logic to propegate
    dut._log.info(f"Sub Imm: {dut.alu_control.Value}")
    
    dut.instruction.value = 0x00    # Resets instruction value.
    await Timer(5, units="ns")      # Allows logic to propegate

@cocotb.test()
async def test_default_case(dut):
    await setup_dut(dut)
    dut._log.info("Test 4: Default case -> alu_control = 0")
    
    await test_add_sub(dut)

    assert alu_int(dut) == 0, f"Default case failed: expected 000000, got {alu_int(dut):06b}"
