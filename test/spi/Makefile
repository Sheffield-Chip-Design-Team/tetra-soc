# Makefile for the Wishbone SPI register block cocotb test

SIM ?= icarus
FST ?= -fst
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../../src

VERILOG_SOURCES += $(SRC_DIR)/spi/spi_mem_ctrl_core.v
VERILOG_SOURCES += $(SRC_DIR)/spi/wb_spi_mem_ctrl_regs.v
VERILOG_SOURCES += $(SRC_DIR)/spi/wb_spi_mem_ctrl.v
VERILOG_SOURCES += $(SRC_DIR)/spi/wb_spi_m_top.v
VERILOG_SOURCES += $(SRC_DIR)/../model/spi_ram_model.v
VERILOG_SOURCES += $(PWD)/spi_tb.v

TOPLEVEL = spi_tb
COCOTB_TEST_MODULES = test_wb_spi_mem_ctrl

include $(shell cocotb-config --makefiles)/Makefile.sim
