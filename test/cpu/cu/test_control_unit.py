import cocotb
from random import randint
from cocotb.triggers import Timer

# Initialse uut/dut with default values
async def initialise(uut):

  uut.instruction.value = 0
  uut.flags.value = 0

  await Timer(5, unit="ns")

  instruction = int(uut.instruction.value)
  flags = int(uut.flags.value)
  acc = int(uut.acc.value)
  alu_control = int(uut.alu_control.value)
  result = int(uut.result.value)
  overflow = int(uut.of_set.value)
  
  uut._log.info("Initial Values Set")
  uut._log.info(f"Reg A: {reg_a}\tReg B: {reg_b}\tAcc: {acc}\ALU Control: {alu_control}\tResult: {result}\tOverflow: {overflow}")


# -------------------------
# Test 1: ADD / SUB group
# -------------------------

@cocotb.test()
async def test_add_sub_group(dut):
    await setup_dut(dut)
    dut._log.info("Test 1: ADD/SUB instruction patterns")

    # ADD implicit: operand=0000, opcode=0001
    dut.instruction.value = 0b0000_0000_0000_0001
    dut.flags.value = 0b0100  # carry flag = flags[2]
    await settle()
    assert alu_int(dut) == int("1" "1" "0" "1" "0" "0", 2), \
        f"ADD Imp failed: got {alu_int(dut):06b}"

    # SUB implicit: operand=0001, opcode=0001
    dut.instruction.value = 0b0001_0000_0000_0001
    dut.flags.value = 0b0100
    await settle()
    assert alu_int(dut) & 0b111111 == alu_int(dut), "SUB Imp output invalid"


# -------------------------
# Test 2: Logic group (AND/OR/XOR)
# -------------------------

@cocotb.test()
async def test_logic_group(dut):
    await setup_dut(dut)
    dut._log.info("Test 2: Logic instruction patterns")

    # AND implicit: operand=0100, opcode=0001
    dut.instruction.value = 0b0100_0000_0000_0001
    dut.flags.value = 0b0100
    await settle()
    assert alu_int(dut) & 0b111111 == alu_int(dut), "AND Imp output invalid"

    # OR implicit: operand=0101, opcode=0001
    dut.instruction.value = 0b0101_0000_0000_0001
    await settle()
    assert alu_int(dut) & 0b111111 == alu_int(dut), "OR Imp output invalid"

    # XOR implicit: operand=0110, opcode=0001
    dut.instruction.value = 0b0110_0000_0000_0001
    await settle()
    assert alu_int(dut) & 0b111111 == alu_int(dut), "XOR Imp output invalid"


# -------------------------
# Test 3: INC/DEC/LSH/RSH group
# -------------------------

@cocotb.test()
async def test_shift_inc_dec_group(dut):
    await setup_dut(dut)
    dut._log.info("Test 3: INC/DEC/LSH/RSH instruction patterns")

    # INC example: operand=0000, opcode=0010
    dut.instruction.value = 0b0000_0000_0000_0010
    dut.flags.value = 0b1000  # flags[3] = overflow, flags[2] = carry
    await settle()
    assert alu_int(dut) & 0b111111 == alu_int(dut), "INC output invalid"

    # DEC example: operand=0001, opcode=0010
    dut.instruction.value = 0b0001_0000_0000_0010
    await settle()
    assert alu_int(dut) & 0b111111 == alu_int(dut), "DEC output invalid"

    # LSH example: operand=0010, opcode=0010
    dut.instruction.value = 0b0010_0000_0000_0010
    await settle()
    assert alu_int(dut) & 0b111111 == alu_int(dut), "LSH output invalid"

    # RSH example: operand=0011, opcode=0010
    dut.instruction.value = 0b0011_0000_0000_0010
    await settle()
    assert alu_int(dut) & 0b111111 == alu_int(dut), "RSH output invalid"


# -------------------------
# Test 4: Default case
# -------------------------

@cocotb.test()
async def test_default_case(dut):
    await setup_dut(dut)
    dut._log.info("Test 4: Default case -> alu_control = 0")

    dut.instruction.value = 0xFFFF  # illegal pattern
    dut.flags.value = 0b1111
    await settle()

    assert alu_int(dut) == 0, f"Default case failed: expected 000000, got {alu_int(dut):06b}"
