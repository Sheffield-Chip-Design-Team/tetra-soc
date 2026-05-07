// =======================================================================
// Module:      SPI Memory Controller
// Project:     Tetra-SoC, by SHaRC
// Description: Reads one byte from 23LC512-style SPI RAM.
//              Uses command 0x03 + 16-bit address.
// =======================================================================

// TODO - integrate the logic into THIS top module instead of instantiating a separate one

module wb_spi_m_top (
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

  wire irq_unused;
  wire _unused_parity = ^{1'b0, irq_unused, wb_sel_i, wb_cti_i, wb_bte_i, wb_adr_i[31:5]};

  wb_spi_mem_ctrl u (
    .clk      (clk),
    .rst_n    (rst_n),

    .wb_addr_i (wb_adr_i[4:0]),
    .wb_wdata_i(wb_dat_i),
    .wb_we_i   (wb_we_i),
    .wb_stb_i  (wb_cyc_i & wb_stb_i),
    .wb_rdata_o(wb_rdt_o),
    .wb_ack_o  (wb_ack_o),
    .irq_o     (irq_unused),

    .cs_n      (cs_n),
    .sck       (sck),
    .mosi      (mosi),
    .miso      (miso)
  );

  assign wb_err_o = _unused_parity ^ _unused_parity;
  assign wb_rty_o = 1'b0;

endmodule
