import cocotb
from random import randint
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
import os

async def reset(uut, reset_duration=randint(1,10)):
    # assert reset
    uut._log.info("Resetting Module")
    uut.rst.value = 1
    await ClockCycles(uut.clk, reset_duration)
    uut.rst.value = 0

@cocotb.test()
async def test_alu_sanity(uut):
    # start clock
    clock = Clock(uut.clk, 40, units="ns")
    cocotb.start_soon(clock.start())
    await ClockCycles(uut.clk, 1)

    # reset the module
    await reset(uut)
    await RisingEdge(uut.clk)

    # continue test ...
    await ClockCycles(uut.clk, 100)
    uut._log.info("Test Complete!")

    