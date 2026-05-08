# Cocotb Makefile for interconnect -> SPI path test
# Run with: make -B

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Cocotb embeds Python via a simulator plugin. If PYTHONHOME points at a venv,
# Python may fail to find the stdlib (e.g. `encodings`). Force PYTHONHOME to the
# base interpreter prefix and clear PYTHONPATH for reproducible runs.
export PYTHONHOME := $(shell python3 -c 'import sys; print(sys.base_prefix)')
export PYTHONPATH :=

SRC_DIR := $(abspath $(PWD)/../../src)
MODEL_DIR := $(abspath $(PWD)/../../model)

# Verilog sources
VERILOG_SOURCES += $(PWD)/intercon_tb.v

# Interconnect
VERILOG_SOURCES += $(SRC_DIR)/intercon/wb8_to_wb32.v
VERILOG_SOURCES += $(SRC_DIR)/intercon/wb_intercon.v
VERILOG_SOURCES += $(SRC_DIR)/intercon/wb_mux.v
VERILOG_SOURCES += $(SRC_DIR)/intercon/wb_data_resize.v
VERILOG_SOURCES += $(SRC_DIR)/intercon/intercon_ss.v

# SPI memory controller + regbank + core
VERILOG_SOURCES += $(SRC_DIR)/spi/wb_spi_mem_ctrl.v
VERILOG_SOURCES += $(SRC_DIR)/spi/wb_spi_mem_ctrl_regs.v
VERILOG_SOURCES += $(SRC_DIR)/spi/spi_mem_ctrl_core.v

# SPI RAM behavioral model
VERILOG_SOURCES += $(MODEL_DIR)/spi_ram_model.v

# RAM memory subsystem
VERILOG_SOURCES += $(SRC_DIR)/mem/sram_1rw.v
VERILOG_SOURCES += $(SRC_DIR)/mem/wb_ram_ctrl.v
VERILOG_SOURCES += $(SRC_DIR)/mem/memory_ss.v

# Include paths for wishbone headers
COMPILE_ARGS += -I$(SRC_DIR)/intercon

# iverilog language level
ifeq ($(SIM),icarus)
COMPILE_ARGS += -g2012
endif

TOPLEVEL := intercon_tb
COCOTB_TEST_MODULES := test_intercon_spi,test_intercon_ram

include $(shell cocotb-config --makefiles)/Makefile.sim
