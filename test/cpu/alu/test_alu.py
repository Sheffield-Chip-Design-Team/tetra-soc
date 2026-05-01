import cocotb
from random import randint
from cocotb.triggers import Timer

@cocotb.test()
async def test_alu_combinational(uut):
  # set random input values
  uut.reg_a_val.value = 0
  uut._log.info(f"Setting reg_a_val to {uut.reg_a_val.value}")

  uut.reg_b_val.value = 0
  uut._log.info(f"Setting reg_b_val to {uut.reg_b_val.value}")

  uut.acc.value = 0
  uut._log.info(f"Setting acc to {uut.acc.value}")

  uut.alu_control.value = 0
  uut._log.info(f"Setting alu_control to {uut.alu_control.value}")

  await Timer(randint(1,10), unit="ns")

  uut._log.info("Initial Values Set")
  uut._log.info("***************************************************")
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
      overflow = int(uut.overflow.value)

      if (
        (not i + j > 15 and 
        overflow == 1 and
        i + j - 16 == result)
        and
        (not i + j == result and
         overflow == 0)
        ):
        op_pass = False
        test_pass = False
      
      uut._log.info(
        f"Reg A: {reg_a}\tReg B: {reg_b}\tResult: {result}\tOverflow: {overflow}\tOperation Result: {op_pass}"
        )
      
  uut.alu_control.value = 0

  await Timer(5, unit="ns")
      
  uut._log.info("***************************************************")
  uut._log.info(f"ADD testing finished.\tPassed:\t{test_pass}")

  # TODO - add checks for expected output values

  uut._log.info("Test Complete!")
