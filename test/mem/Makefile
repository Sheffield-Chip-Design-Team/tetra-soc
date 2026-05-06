# Makefile

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/../../src/mem/sram_1rw.v
VERILOG_SOURCES += $(PWD)/../../src/mem/wb_ram_ctrl.v
VERILOG_SOURCES += $(PWD)/mem_tb.v

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = mem_tb

# MODULE is the basename of the Python test file
MODULE = test_wb_mem

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
