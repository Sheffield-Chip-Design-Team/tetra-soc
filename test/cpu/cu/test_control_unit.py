import cocotb
from cocotb.triggers import Timer




# Reminder of bit structure for my sanity as I make this:
# Feel free to delete once everythings complete but pls keep until then.

# ALU control:


# [5] ALU ENABLE
# [4] CARRY or Borrow flag
# [3] LOGIC bit (1 for logic, 0 for arithmetic or shift)
# [2] Arithemtic bit (1 for add/sub, 0 for logic or shift)
# [1] XOR OR SHIFT depending on what other bits are high
# [0] SUB, OR, DEC, RSH depending on what other bits are high

# Flags reg:

# [3]  Borrow 
# [2] carry 
# [1] Underflow
# [0] Overflow 

# -------------------------
# Helper functions
# -------------------------

def alu_int(dut):
    return int(dut.alu_control.value)


async def setup_dut(dut):
    dut.instruction.value = 0
    dut.flags.value = 0
    await Timer(10, unit="ns")

# -------------------------
# Test 1: ADD / SUB group
# -------------------------

async def test_add_sub(dut):    

    dut._log.info("Starting ADD / SUB control test")

    dut.instruction.value = 0x01    # Tests the case that the instruction is implicit add
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"Add Imp: {dut.alu_control.value}")

    dut.instruction.value = 0x11    # Tests the case that the instruction is implicit sub
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"Sub Imp: {dut.alu_control.value}")

    dut.instruction.value = 0x81    # Tests the case that the instruction is immediate add
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"Add Imm: {dut.alu_control.value}")

    dut.instruction.value = 0x91    # Tests the case that the instruction is immediate sub
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"Sub Imm: {dut.alu_control.value}")

    dut.instruction.value = 0x00    # Resets instruction value.
    await Timer(5, unit="ns")      # Allows logic to propegate


# ----------------------------
# Test 2: AND / OR / XOR group
# ----------------------------


async def test_logical(dut):    
    dut._log.info("Starting logical (And Or XOR) control tests")
    # AND TESTS - Immediate and Implicit
    dut.instruction.value = 0x41    # Tests for implicit AND
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"AND Imp: {dut.alu_control.value}")

    dut.instruction.value = 0xC1    # Tests for immediate AND
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"AND Imm: {dut.alu_control.value}")

    # OR TESTS - Immediate and Implicit
    dut.instruction.value = 0x51    # Tests for implicit OR
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"OR Imp: {dut.alu_control.value}")

    dut.instruction.value = 0xD1    # Tests for immediate OR
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"OR Imm: {dut.alu_control.value}")

    # XOR TESTS - Immediate and Implicit
    dut.instruction.value = 0x61    # Tests for implicit XOR
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"XOR Imp: {dut.alu_control.value}")

    dut.instruction.value = 0xE1    # Tests for immediate XOR
    await Timer(5, unit="ns")      # Allows logic to propegate
    dut._log.info(f"XOR Imm: {dut.alu_control.value}")





@cocotb.test()

async def test_default_case(dut):
    await setup_dut(dut)
    dut._log.info("Test 4: Default case -> alu_control = 0")


    ## The following are the tests for the add and sub operations with fluctuations of carry and borrow.
    
    await test_add_sub(dut)     # Run test for add and sub operations
    dut.flags.value = 0b1000
    await Timer(5, unit="ns")
    dut._log.info("Test 5: Default case -> flag -> Borrow only set to high")
    await test_add_sub(dut)     # Run test for add and sub operations with flags
    dut.flags.value = 0b0100
    await Timer(5, unit="ns")
    dut._log.info("Test 6: Default case -> flag -> Carry only set to high")
    await test_add_sub(dut)     # Run test for add and sub operations with flags
    dut.flags.value = 0b1100
    await Timer(5, unit="ns")
    dut._log.info("Test 7: Default case -> flag -> Borrow and Carry set to high")
    await test_add_sub(dut)     # Run test for add and sub operations with flags

    ## The following are the tests for the logical operations with fluctuations of carry and borrow.

    await test_logical(dut)     # Run test for logical operations
    dut.flags.value = 0b1000
    await Timer(5, unit="ns")
    dut._log.info("Test 8: Default case -> flag -> Borrow only set to high")
    await test_logical(dut)     # Run test for logical operations with flags
    dut.flags.value = 0b0100
    await Timer(5, unit="ns")
    dut._log.info("Test 9: Default case -> flag -> Carry only set to high")
    await test_logical(dut)     # Run test for logical operations with flags
    dut.flags.value = 0b1100
    await Timer(5, unit="ns")
    dut._log.info("Test 10: Default case -> flag -> Borrow and Carry set to high")
    await test_logical(dut)     # Run test for logical operations with flags  



# ALU control:

# [5] ALU ENABLE
# [4] CARRY or Borrow flag
# [3] LOGIC bit (1 for logic, 0 for arithmetic or shift)
# [2] Arithemtic bit (1 for add/sub, 0 for logic or shift)
# [1] XOR OR SHIFT depending on what other bits are high
# [0] SUB, OR, DEC, RSH depending on what other bits are high

# Flags reg:

# [3]  Borrow 
# [2] carry 
# [1] Underflow
# [0] Overflow 

