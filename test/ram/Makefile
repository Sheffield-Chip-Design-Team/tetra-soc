SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PWD := $(shell pwd)

VERILOG_SOURCES += $(PWD)/../../src/mem/sram_1rw.v
VERILOG_SOURCES += $(PWD)/../../src/mem/wb_ram_ctrl.v
VERILOG_SOURCES += $(PWD)/ram_tb.v

TOPLEVEL = ram_tb
COCOTB_TEST_MODULES = test_wb_ram_ctrl

WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim
