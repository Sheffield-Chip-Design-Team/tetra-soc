`default_nettype none
`timescale 1ns/1ps

module intercon_tb;
  // Dump waves
  initial begin
    $dumpfile("intercon_tb.fst");
    $dumpvars(0, intercon_tb);
    #1;
  end

  // Clock / reset
  reg sys_clk;
  reg sys_rst_n;

  initial begin
    sys_clk = 1'b0;
    forever #5 sys_clk = ~sys_clk; // 100 MHz
  end

  initial begin
    sys_rst_n = 1'b0;
    repeat (5) @(posedge sys_clk);
    sys_rst_n = 1'b1;
  end

  // -----------------------------
  // CPU Wishbone 8-bit slave bus
  // -----------------------------
  reg  [31:0] wb_cpu_s_adr_i;
  reg   [7:0] wb_cpu_s_dat_i;
  reg         wb_cpu_s_we_i;
  reg         wb_cpu_s_cyc_i;
  reg         wb_cpu_s_stb_i;
  reg   [2:0] wb_cpu_s_cti_i;
  reg   [1:0] wb_cpu_s_bte_i;

  wire  [7:0] wb_cpu_s_dat_o;
  wire        wb_cpu_s_ack_o;
  wire        wb_cpu_s_err_o;
  wire        wb_cpu_s_rty_o;

  initial begin
    wb_cpu_s_adr_i = 32'h0;
    wb_cpu_s_dat_i = 8'h00;
    wb_cpu_s_we_i  = 1'b0;
    wb_cpu_s_cyc_i = 1'b0;
    wb_cpu_s_stb_i = 1'b0;
    wb_cpu_s_cti_i = 3'b000; // classic
    wb_cpu_s_bte_i = 2'b00;
  end

  // -----------------------------
  // ROM port (unused in this test)
  // -----------------------------
  wire [31:0] wb_rom_adr_o;
  wire  [7:0] wb_rom_dat_o;
  wire  [3:0] wb_rom_sel_o;
  wire        wb_rom_we_o;
  wire        wb_rom_cyc_o;
  wire        wb_rom_stb_o;
  wire  [2:0] wb_rom_cti_o;
  wire  [1:0] wb_rom_bte_o;
  wire  [7:0] wb_rom_rdt_i = 8'h00;
  wire        wb_rom_ack_i = 1'b0;
  wire        wb_rom_err_i = 1'b0;
  wire        wb_rom_rty_i = 1'b0;

  // -----------------------------
  // RAM port (unused in this test)
  // -----------------------------
  wire [31:0] wb_ram_adr_o;
  wire  [7:0] wb_ram_dat_o;
  wire  [3:0] wb_ram_sel_o;
  wire        wb_ram_we_o;
  wire        wb_ram_cyc_o;
  wire        wb_ram_stb_o;
  wire  [2:0] wb_ram_cti_o;
  wire  [1:0] wb_ram_bte_o;
  wire  [7:0] wb_ram_rdt_i = 8'h00;
  wire        wb_ram_ack_i = 1'b0;
  wire        wb_ram_err_i = 1'b0;
  wire        wb_ram_rty_i = 1'b0;

  // --------------------------------
  // EXT flash port (unused in this test)
  // --------------------------------
  wire [31:0] wb_ext_flash_adr_o;
  wire  [7:0] wb_ext_flash_dat_o;
  wire  [3:0] wb_ext_flash_sel_o;
  wire        wb_ext_flash_we_o;
  wire        wb_ext_flash_cyc_o;
  wire        wb_ext_flash_stb_o;
  wire  [2:0] wb_ext_flash_cti_o;
  wire  [1:0] wb_ext_flash_bte_o;
  wire  [7:0] wb_ext_flash_rdt_i = 8'h00;
  wire        wb_ext_flash_ack_i = 1'b0;
  wire        wb_ext_flash_err_i = 1'b0;
  wire        wb_ext_flash_rty_i = 1'b0;

  // --------------------------------
  // UART port (unused in this test)
  // --------------------------------
  wire [31:0] wb_uart_adr_o;
  wire  [7:0] wb_uart_dat_o;
  wire  [3:0] wb_uart_sel_o;
  wire        wb_uart_we_o;
  wire        wb_uart_cyc_o;
  wire        wb_uart_stb_o;
  wire  [2:0] wb_uart_cti_o;
  wire  [1:0] wb_uart_bte_o;
  wire  [7:0] wb_uart_rdt_i = 8'h00;
  wire        wb_uart_ack_i = 1'b0;
  wire        wb_uart_err_i = 1'b0;
  wire        wb_uart_rty_i = 1'b0;

  // -----------------------------
  // SPI-m port (connected)
  // -----------------------------
  wire [31:0] wb_spi_m_adr_o;
  wire  [7:0] wb_spi_m_dat_o;
  wire  [3:0] wb_spi_m_sel_o;
  wire        wb_spi_m_we_o;
  wire        wb_spi_m_cyc_o;
  wire        wb_spi_m_stb_o;
  wire  [2:0] wb_spi_m_cti_o;
  wire  [1:0] wb_spi_m_bte_o;
  wire  [7:0] wb_spi_m_rdt_i;
  wire        wb_spi_m_ack_i;
  wire        wb_spi_m_err_i;
  wire        wb_spi_m_rty_i;

  // SPI pins (exported for cocotb visibility)
  wire spi_cs_n;
  wire spi_sck;
  wire spi_mosi;
  wire spi_miso;

  // Adapt full Wishbone peripheral signals to the simple wb_spi_mem_ctrl port set
  wb_spi_mem_ctrl_wb u_spi (
    .clk            (sys_clk),
    .rst_n          (sys_rst_n),

    .wb_adr_i       (wb_spi_m_adr_o),
    .wb_dat_i       (wb_spi_m_dat_o),
    .wb_sel_i       (wb_spi_m_sel_o),
    .wb_we_i        (wb_spi_m_we_o),
    .wb_cyc_i       (wb_spi_m_cyc_o),
    .wb_stb_i       (wb_spi_m_stb_o),
    .wb_cti_i       (wb_spi_m_cti_o),
    .wb_bte_i       (wb_spi_m_bte_o),

    .wb_rdt_o       (wb_spi_m_rdt_i),
    .wb_ack_o       (wb_spi_m_ack_i),
    .wb_err_o       (wb_spi_m_err_i),
    .wb_rty_o       (wb_spi_m_rty_i),

    .cs_n           (spi_cs_n),
    .sck            (spi_sck),
    .mosi           (spi_mosi),
    .miso           (spi_miso)
  );

  // SPI RAM behavioral model
  spi_ram_model #(.MEM_BYTES(256)) u_spi_ram (
    .cs_n (spi_cs_n),
    .sck  (spi_sck),
    .mosi (spi_mosi),
    .miso (spi_miso)
  );

  // Deterministic contents for the RAM model
  integer i;
  initial begin
    // wait until after time 0 so hierarchical reference is valid
    #1;
    for (i = 0; i < 256; i = i + 1) begin
      u_spi_ram.mem[i] = i[7:0];
    end
  end

  // -----------------------------
  // DUT: interconnect
  // -----------------------------
  intercon_ss dut (
    .sys_clk              (sys_clk),
    .sys_rst_n            (sys_rst_n),

    .wb_cpu_s_adr_i       (wb_cpu_s_adr_i),
    .wb_cpu_s_dat_i       (wb_cpu_s_dat_i),
    .wb_cpu_s_we_i        (wb_cpu_s_we_i),
    .wb_cpu_s_cyc_i       (wb_cpu_s_cyc_i),
    .wb_cpu_s_stb_i       (wb_cpu_s_stb_i),
    .wb_cpu_s_cti_i       (wb_cpu_s_cti_i),
    .wb_cpu_s_bte_i       (wb_cpu_s_bte_i),
    .wb_cpu_s_dat_o       (wb_cpu_s_dat_o),
    .wb_cpu_s_ack_o       (wb_cpu_s_ack_o),
    .wb_cpu_s_err_o       (wb_cpu_s_err_o),
    .wb_cpu_s_rty_o       (wb_cpu_s_rty_o),

    .wb_rom_adr_o         (wb_rom_adr_o),
    .wb_rom_dat_o         (wb_rom_dat_o),
    .wb_rom_sel_o         (wb_rom_sel_o),
    .wb_rom_we_o          (wb_rom_we_o),
    .wb_rom_cyc_o         (wb_rom_cyc_o),
    .wb_rom_stb_o         (wb_rom_stb_o),
    .wb_rom_cti_o         (wb_rom_cti_o),
    .wb_rom_bte_o         (wb_rom_bte_o),
    .wb_rom_rdt_i         (wb_rom_rdt_i),
    .wb_rom_ack_i         (wb_rom_ack_i),
    .wb_rom_err_i         (wb_rom_err_i),
    .wb_rom_rty_i         (wb_rom_rty_i),

    .wb_ext_flash_adr_o   (wb_ext_flash_adr_o),
    .wb_ext_flash_dat_o   (wb_ext_flash_dat_o),
    .wb_ext_flash_sel_o   (wb_ext_flash_sel_o),
    .wb_ext_flash_we_o    (wb_ext_flash_we_o),
    .wb_ext_flash_cyc_o   (wb_ext_flash_cyc_o),
    .wb_ext_flash_stb_o   (wb_ext_flash_stb_o),
    .wb_ext_flash_cti_o   (wb_ext_flash_cti_o),
    .wb_ext_flash_bte_o   (wb_ext_flash_bte_o),
    .wb_ext_flash_rdt_i   (wb_ext_flash_rdt_i),
    .wb_ext_flash_ack_i   (wb_ext_flash_ack_i),
    .wb_ext_flash_err_i   (wb_ext_flash_err_i),
    .wb_ext_flash_rty_i   (wb_ext_flash_rty_i),

    .wb_spi_m_adr_o       (wb_spi_m_adr_o),
    .wb_spi_m_dat_o       (wb_spi_m_dat_o),
    .wb_spi_m_sel_o       (wb_spi_m_sel_o),
    .wb_spi_m_we_o        (wb_spi_m_we_o),
    .wb_spi_m_cyc_o       (wb_spi_m_cyc_o),
    .wb_spi_m_stb_o       (wb_spi_m_stb_o),
    .wb_spi_m_cti_o       (wb_spi_m_cti_o),
    .wb_spi_m_bte_o       (wb_spi_m_bte_o),
    .wb_spi_m_rdt_i       (wb_spi_m_rdt_i),
    .wb_spi_m_ack_i       (wb_spi_m_ack_i),
    .wb_spi_m_err_i       (wb_spi_m_err_i),
    .wb_spi_m_rty_i       (wb_spi_m_rty_i),

    .wb_uart_adr_o        (wb_uart_adr_o),
    .wb_uart_dat_o        (wb_uart_dat_o),
    .wb_uart_sel_o        (wb_uart_sel_o),
    .wb_uart_we_o         (wb_uart_we_o),
    .wb_uart_cyc_o        (wb_uart_cyc_o),
    .wb_uart_stb_o        (wb_uart_stb_o),
    .wb_uart_cti_o        (wb_uart_cti_o),
    .wb_uart_bte_o        (wb_uart_bte_o),
    .wb_uart_rdt_i        (wb_uart_rdt_i),
    .wb_uart_ack_i        (wb_uart_ack_i),
    .wb_uart_err_i        (wb_uart_err_i),
    .wb_uart_rty_i        (wb_uart_rty_i),

    .wb_ram_adr_o         (wb_ram_adr_o),
    .wb_ram_dat_o         (wb_ram_dat_o),
    .wb_ram_sel_o         (wb_ram_sel_o),
    .wb_ram_we_o          (wb_ram_we_o),
    .wb_ram_cyc_o         (wb_ram_cyc_o),
    .wb_ram_stb_o         (wb_ram_stb_o),
    .wb_ram_cti_o         (wb_ram_cti_o),
    .wb_ram_bte_o         (wb_ram_bte_o),
    .wb_ram_rdt_i         (wb_ram_rdt_i),
    .wb_ram_ack_i         (wb_ram_ack_i),
    .wb_ram_err_i         (wb_ram_err_i),
    .wb_ram_rty_i         (wb_ram_rty_i)
  );

endmodule

// -----------------------------------------------------------------------------
// Full Wishbone (8-bit data) peripheral wrapper for wb_spi_mem_ctrl
// -----------------------------------------------------------------------------
module wb_spi_mem_ctrl_wb (
  input  wire        clk,
  input  wire        rst_n,

  input  wire [31:0] wb_adr_i,
  input  wire  [7:0] wb_dat_i,
  input  wire  [3:0] wb_sel_i,
  input  wire        wb_we_i,
  input  wire        wb_cyc_i,
  input  wire        wb_stb_i,
  input  wire  [2:0] wb_cti_i,
  input  wire  [1:0] wb_bte_i,

  output wire  [7:0] wb_rdt_o,
  output wire        wb_ack_o,
  output wire        wb_err_o,
  output wire        wb_rty_o,

  output wire        cs_n,
  output wire        sck,
  output wire        mosi,
  input  wire        miso
);
  // Unused in this simple adapter
  wire _unused = &{1'b0, wb_sel_i, wb_cti_i, wb_bte_i, wb_adr_i[31:5]};

  wb_spi_mem_ctrl u (
    .clk      (clk),
    .rst_n    (rst_n),

    .wb_addr_i (wb_adr_i[4:0]),
    .wb_wdata_i(wb_dat_i),
    .wb_we_i   (wb_we_i),
    .wb_stb_i  (wb_cyc_i & wb_stb_i),
    .wb_rdata_o(wb_rdt_o),
    .wb_ack_o  (wb_ack_o),
    .irq_o     (),

    .cs_n      (cs_n),
    .sck       (sck),
    .mosi      (mosi),
    .miso      (miso)
  );

  assign wb_err_o = 1'b0;
  assign wb_rty_o = 1'b0;

endmodule
