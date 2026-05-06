import cocotb
from random import randint
from cocotb.triggers import Timer

async def initialise(uut):

  uut.reg_a_val.value = 0
  uut.reg_b_val.value = 0
  uut.acc.value = 0
  uut.alu_control.value = 0

  await Timer(5, unit="ns")

  reg_a = int(uut.reg_a_val.value)
  reg_b = int(uut.reg_b_val.value)
  acc = int(uut.acc.value)
  alu_control = int(uut.alu_control.value)
  result = int(uut.result.value)
  overflow = int(uut.of_set.value)
  
  uut._log.info("Initial Values Set")
  uut._log.info(f"Reg A: {reg_a}\tReg B: {reg_b}\tAcc: {acc}\ALU Control: {alu_control}\tResult: {result}\tOverflow: {overflow}")

async def test_add(uut):
  uut._log.info("Testing ADD operation:")
  
  op_pass = False
  test_pass = True

  uut.alu_control.value = 1

  for i in range(0,16):
    for j in range(0,16):
      op_pass = True

      uut.reg_a_val.value = i
      uut.reg_b_val.value = j

      await Timer(5, unit="ns")

      reg_a = int(uut.reg_a_val.value)
      reg_b = int(uut.reg_b_val.value)
      result = int(uut.result.value)
      overflow = int(uut.of_set.value)

      if (
        not (
          i + j > 15 and 
          overflow == 1 and
          i + j - 16 == result
          )
        and not (
          i + j == result and
          overflow == 0
          )
        ):
          op_pass = False
          test_pass = False
      
    # Commented out log below to keep terminal output tidy. Uncomment to 

      #uut._log.info(
      #  f"Reg A: {reg_a}\tReg B: {reg_b}\tResult: {result}\tOverflow: {overflow}\tPass: {op_pass}"
      #  )
      
  uut.reg_a_val.value = 0
  uut.reg_b_val.value = 0
  uut.acc.value = 0
  uut.alu_control.value = 0

  await Timer(5, unit="ns")
      
  uut._log.info("***************************************************")
  uut._log.info(f"ADD testing finished.\tPassed:\t{test_pass}")

async def test_sub(uut):
  uut._log.info("Testing SUB operation:")
  
  op_pass = False
  test_pass = True

  uut.alu_control.value = 2

  for i in range(0,16):
    for j in range(0,16):
      op_pass = True

      uut.reg_a_val.value = i
      uut.reg_b_val.value = j

      await Timer(5, unit="ns")

      reg_a = int(uut.reg_a_val.value)
      reg_b = int(uut.reg_b_val.value)
      result = int(uut.result.value)

      if (
        not (
          i - j < 0 and 
          i - j + 16 == result
          )
        and not (
          i - j == result
          )
        ):
          op_pass = False
          test_pass = False

      uut._log.info(
        f"Reg A: {reg_a}\tReg B: {reg_b}\tResult: {result}\tPass: {op_pass}"
        )
      
  uut.reg_a_val.value = 0
  uut.reg_b_val.value = 0
  uut.acc.value = 0
  uut.alu_control.value = 0

  await Timer(5, unit="ns")
      
  uut._log.info("***************************************************")
  uut._log.info(f"SUB testing finished.\tPassed:\t{test_pass}")

@cocotb.test()
async def test_alu_combinational(uut):
  await initialise(uut)
  uut._log.info("***************************************************")
  await test_add(uut)
  uut._log.info("***************************************************")
  await test_sub(uut)
  uut._log.info("***************************************************")

  # TODO - add checks for expected output values

  uut._log.info("Test Complete!")
