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
  uut._log.info("No Overflow:")
  
  uut.reg_a_val.value = 5
  uut.reg_b_val.value = 7
  uut.alu_control.value = 1

  await Timer(5, unit="ns")

  op_pass = False
  reg_a = int(uut.reg_a_val.value)
  reg_b = int(uut.reg_b_val.value)
  result = int(uut.result.value)
  overflow = int(uut.overflow.value)


  if (result == reg_a + reg_b) and (overflow == 0):
    op_pass = True
  
  uut._log.info(
    f"Reg A: {reg_a}, Reg B: {reg_b}, Result: {result}, Overflow: {overflow}, Test Result: {op_pass}"
    )
  
  uut._log.info("With Overflow")

  uut.reg_a_val.value = 12
  uut.reg_b_val.value = 7

  await Timer(5, unit="ns")

  op_pass = False
  reg_a = int(uut.reg_a_val.value)
  reg_b = int(uut.reg_b_val.value)
  result = int(uut.result.value)
  overflow = int(uut.overflow.value)

  if (result == (reg_a + reg_b) - 16) and (overflow == 1):
    op_pass = True

  uut._log.info(
    f"Reg A: {reg_a}, Reg B: {reg_b}, Result: {result}, Overflow: {overflow}, Test Result: {op_pass}"
    )

  # TODO - add checks for expected output values

  uut._log.info("Test Complete!")