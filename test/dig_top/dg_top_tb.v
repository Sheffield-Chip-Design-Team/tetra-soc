`default_nettype none
`timescale 1ns/1ps

module dg_top_tb;
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
  // (exposed for cocotb; forced onto dig_top internal CPU WB master nets)
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
  // Peripherals / debug pins
  // -----------------------------
  wire spi_cs_n;
  wire spi_sck;
  wire spi_mosi;
  wire spi_miso;

  reg jtag_tck;
  reg jtag_tms;
  reg jtag_tdi;
  wire jtag_tdo;

  reg uart_rx;
  wire uart_tx;

  wire vga_hsync;
  wire vga_vsync;
  wire [1:0] vga_rr;
  wire [1:0] vga_gg;
  wire [1:0] vga_bb;

  // Hold CPU halted during these bus-level tests.
  // dig_top maps {halt,resume,step} = dbg_addr_in[2:0]
  reg  [15:0] dbg_addr_in;
  reg  [7:0]  dbg_data_in;
  wire [15:0] dbg_addr_out;
  wire [7:0]  dbg_data_out;

  initial begin
    jtag_tck = 1'b0;
    jtag_tms = 1'b0;
    jtag_tdi = 1'b0;
    uart_rx  = 1'b1;

    dbg_addr_in = 16'h0004; // halt=1, resume=0, step=0
    dbg_data_in = 8'h00;
  end

  // -----------------------------
  // DUT
  // -----------------------------
  dig_top u_dig_top (
    .clk         (sys_clk),
    .rst_n       (sys_rst_n),

    .jtag_tck    (jtag_tck),
    .jtag_tms    (jtag_tms),
    .jtag_tdi    (jtag_tdi),
    .jtag_tdo    (jtag_tdo),

    .spi_cs_n    (spi_cs_n),
    .spi_sck     (spi_sck),
    .spi_mosi    (spi_mosi),
    .spi_miso    (spi_miso),

    .uart_rx     (uart_rx),
    .uart_tx     (uart_tx),

    .vga_hsync   (vga_hsync),
    .vga_vsync   (vga_vsync),
    .vga_rr      (vga_rr),
    .vga_gg      (vga_gg),
    .vga_bb      (vga_bb),

    .dbg_addr_in (dbg_addr_in),
    .dbg_data_in (dbg_data_in),
    .dbg_addr_out(dbg_addr_out),
    .dbg_data_out(dbg_data_out)
  );

  // -----------------------------
  // SPI RAM behavioral model
  // -----------------------------
  spi_ram_model #(.MEM_BYTES(256)) u_spi_ram (
    .cs_n (spi_cs_n),
    .sck  (spi_sck),
    .mosi (spi_mosi),
    .miso (spi_miso)
  );

  // -----------------------------
  // Expose dig_top internal buses to cocotb
  // -----------------------------

  // Force the interconnect CPU-side bus from tb regs.
  // NOTE: u_dig_top ties wb_cpu_m_adr_o[31:16] to 0, so we drive low bits only.
  initial begin
    force u_dig_top.wb_cpu_m_adr_o[15:0] = wb_cpu_s_adr_i[15:0];
    force u_dig_top.wb_cpu_m_dat_o       = wb_cpu_s_dat_i;
    force u_dig_top.wb_cpu_m_we_o        = wb_cpu_s_we_i;
    force u_dig_top.wb_cpu_m_cyc_o       = wb_cpu_s_cyc_i;
    force u_dig_top.wb_cpu_m_stb_o       = wb_cpu_s_stb_i;
    force u_dig_top.wb_cpu_m_cti_o       = wb_cpu_s_cti_i;
    force u_dig_top.wb_cpu_m_bte_o       = wb_cpu_s_bte_i;
  end

  // Readback/handshake signals
  assign wb_cpu_s_dat_o = u_dig_top.wb_cpu_m_dat_i;
  assign wb_cpu_s_ack_o = u_dig_top.wb_cpu_m_ack_i;
  assign wb_cpu_s_err_o = u_dig_top.u_intercon_ss.wb_cpu_s_err_o;
  assign wb_cpu_s_rty_o = u_dig_top.u_intercon_ss.wb_cpu_s_rty_o;

  // Interconnect ports observed by the tests
  wire [31:0] wb_ram_adr_o;
  wire  [7:0] wb_ram_dat_o;
  wire  [3:0] wb_ram_sel_o;
  wire        wb_ram_we_o;
  wire        wb_ram_cyc_o;
  wire        wb_ram_stb_o;

  wire [31:0] wb_spi_m_adr_o;
  wire  [7:0] wb_spi_m_dat_o;
  wire        wb_spi_m_we_o;
  wire        wb_spi_m_cyc_o;
  wire        wb_spi_m_stb_o;

  assign wb_ram_adr_o   = u_dig_top.wb_ram_adr_o;
  assign wb_ram_dat_o   = u_dig_top.wb_ram_dat_o;
  assign wb_ram_sel_o   = u_dig_top.wb_ram_sel_o;
  assign wb_ram_we_o    = u_dig_top.wb_ram_we_o;
  assign wb_ram_cyc_o   = u_dig_top.wb_ram_cyc_o;
  assign wb_ram_stb_o   = u_dig_top.wb_ram_stb_o;

  assign wb_spi_m_adr_o = u_dig_top.wb_spi_m_adr_o;
  assign wb_spi_m_dat_o = u_dig_top.wb_spi_m_dat_o;
  assign wb_spi_m_we_o  = u_dig_top.wb_spi_m_we_o;
  assign wb_spi_m_cyc_o = u_dig_top.wb_spi_m_cyc_o;
  assign wb_spi_m_stb_o = u_dig_top.wb_spi_m_stb_o;

endmodule

`default_nettype wire
