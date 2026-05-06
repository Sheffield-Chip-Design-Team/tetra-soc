// =======================================================================
// Module:      Interconnect
// Project:     Tetra-SoC, by SHaRC
// Description: Interconnect module for routing signals between components.
// =======================================================================

module intercon_ss (
  input wire         sys_clk,
  input wire         sys_rst_n,
  // CPU Wishbone Slave Interface
  input wire [31:0]  wb_cpu_s_adr_i,
  input wire [7:0]   wb_cpu_s_dat_i,
  input wire         wb_cpu_s_we_i,
  input wire         wb_cpu_s_cyc_i,
  input wire         wb_cpu_s_stb_i,
  input wire  [2:0]  wb_cpu_s_cti_i,
  input wire  [1:0]  wb_cpu_s_bte_i,
  output wire [7:0]  wb_cpu_s_dat_o,
  output wire        wb_cpu_s_ack_o,
  output wire        wb_cpu_s_err_o,
  output wire        wb_cpu_s_rty_o,

  // Wishbone peripheral interfaces (8-bit slaves)
  output wire [31:0] wb_rom_adr_o,
  output wire  [7:0] wb_rom_dat_o,
  output wire  [3:0] wb_rom_sel_o,
  output wire        wb_rom_we_o,
  output wire        wb_rom_cyc_o,
  output wire        wb_rom_stb_o,
  output wire  [2:0] wb_rom_cti_o,
  output wire  [1:0] wb_rom_bte_o,
  input  wire  [7:0] wb_rom_rdt_i,
  input  wire        wb_rom_ack_i,
  input  wire        wb_rom_err_i,
  input  wire        wb_rom_rty_i,

  output wire [31:0] wb_ext_flash_adr_o,
  output wire  [7:0] wb_ext_flash_dat_o,
  output wire  [3:0] wb_ext_flash_sel_o,
  output wire        wb_ext_flash_we_o,
  output wire        wb_ext_flash_cyc_o,
  output wire        wb_ext_flash_stb_o,
  output wire  [2:0] wb_ext_flash_cti_o,
  output wire  [1:0] wb_ext_flash_bte_o,
  input  wire  [7:0] wb_ext_flash_rdt_i,
  input  wire        wb_ext_flash_ack_i,
  input  wire        wb_ext_flash_err_i,
  input  wire        wb_ext_flash_rty_i,

  output wire [31:0] wb_spi_m_adr_o,
  output wire  [7:0] wb_spi_m_dat_o,
  output wire  [3:0] wb_spi_m_sel_o,
  output wire        wb_spi_m_we_o,
  output wire        wb_spi_m_cyc_o,
  output wire        wb_spi_m_stb_o,
  output wire  [2:0] wb_spi_m_cti_o,
  output wire  [1:0] wb_spi_m_bte_o,
  input  wire  [7:0] wb_spi_m_rdt_i,
  input  wire        wb_spi_m_ack_i,
  input  wire        wb_spi_m_err_i,
  input  wire        wb_spi_m_rty_i,

  output wire [31:0] wb_uart_adr_o,
  output wire  [7:0] wb_uart_dat_o,
  output wire  [3:0] wb_uart_sel_o,
  output wire        wb_uart_we_o,
  output wire        wb_uart_cyc_o,
  output wire        wb_uart_stb_o,
  output wire  [2:0] wb_uart_cti_o,
  output wire  [1:0] wb_uart_bte_o,
  input  wire  [7:0] wb_uart_rdt_i,
  input  wire        wb_uart_ack_i,
  input  wire        wb_uart_err_i,
  input  wire        wb_uart_rty_i,

  output wire [31:0] wb_ram_adr_o,
  output wire  [7:0] wb_ram_dat_o,
  output wire  [3:0] wb_ram_sel_o,
  output wire        wb_ram_we_o,
  output wire        wb_ram_cyc_o,
  output wire        wb_ram_stb_o,
  output wire  [2:0] wb_ram_cti_o,
  output wire  [1:0] wb_ram_bte_o,
  input  wire  [7:0] wb_ram_rdt_i,
  input  wire        wb_ram_ack_i,
  input  wire        wb_ram_err_i,
  input  wire        wb_ram_rty_i
);
  
// ----------------------------------------------------------------------
// Internal signals
// ----------------------------------------------------------------------
  
  wire        wb_rst_i;
  assign wb_rst_i = ~sys_rst_n;

  // 32-bit Wishbone master from the CPU-side 8->32 bridge into the interconnect
  wire [31:0] wb_cpu_m_adr;
  wire [31:0] wb_cpu_m_dat;
  wire  [3:0] wb_cpu_m_sel;
  wire        wb_cpu_m_we;
  wire        wb_cpu_m_cyc;
  wire        wb_cpu_m_stb;
  wire  [2:0] wb_cpu_m_cti;
  wire  [1:0] wb_cpu_m_bte;
  wire [31:0] wb_cpu_m_rdt;
  wire        wb_cpu_m_ack;
  wire        wb_cpu_m_err;
  wire        wb_cpu_m_rty;

// ----------------------------------------------------------------------
// Intercon Instantiations
// ----------------------------------------------------------------------

wb8_to_wb32 #(
  .AW           (32),
  .endian       ("little")
) u_wb8_to_wb32 (
  .wb_clk_i     (sys_clk),
  .wb_rst_i     (wb_rst_i),
  .wbs_adr_i    (wb_cpu_s_adr_i),

  // 8-bit Wishbone slave
  .wbs_dat_i    (wb_cpu_s_dat_i),
  .wbs_we_i     (wb_cpu_s_we_i),
  .wbs_cyc_i    (wb_cpu_s_cyc_i),
  .wbs_stb_i    (wb_cpu_s_stb_i),
  .wbs_cti_i    (wb_cpu_s_cti_i),
  .wbs_bte_i    (wb_cpu_s_bte_i),
  .wbs_dat_o    (wb_cpu_s_dat_o),
  .wbs_ack_o    (wb_cpu_s_ack_o),
  .wbs_err_o    (wb_cpu_s_err_o),
  .wbs_rty_o    (wb_cpu_s_rty_o),

  // 32-bit Wishbone master (downstream to intercon)
  .wbm_adr_o    (wb_cpu_m_adr),
  .wbm_dat_o    (wb_cpu_m_dat),
  .wbm_sel_o    (wb_cpu_m_sel),
  .wbm_we_o     (wb_cpu_m_we),
  .wbm_cyc_o    (wb_cpu_m_cyc),
  .wbm_stb_o    (wb_cpu_m_stb),
  .wbm_cti_o    (wb_cpu_m_cti),
  .wbm_bte_o    (wb_cpu_m_bte),
  .wbm_dat_i    (wb_cpu_m_rdt),
  .wbm_ack_i    (wb_cpu_m_ack),
  .wbm_err_i    (wb_cpu_m_err),
  .wbm_rty_i    (wb_cpu_m_rty)
);

wb_intercon u_wb_intercon
   (.wb_clk_i           (sys_clk),
    .wb_rst_i           (wb_rst_i),
    .wb_cpu_adr_i       (wb_cpu_m_adr),
    .wb_cpu_dat_i       (wb_cpu_m_dat),
    .wb_cpu_sel_i       (wb_cpu_m_sel),
    .wb_cpu_we_i        (wb_cpu_m_we),
    .wb_cpu_cyc_i       (wb_cpu_m_cyc),
    .wb_cpu_stb_i       (wb_cpu_m_stb),
    .wb_cpu_cti_i       (wb_cpu_m_cti),
    .wb_cpu_bte_i       (wb_cpu_m_bte),
    .wb_cpu_rdt_o       (wb_cpu_m_rdt),
    .wb_cpu_ack_o       (wb_cpu_m_ack),
    .wb_cpu_err_o       (wb_cpu_m_err),
    .wb_cpu_rty_o       (wb_cpu_m_rty),

    .wb_rom_adr_o       (wb_rom_adr_o),
    .wb_rom_dat_o       (wb_rom_dat_o),
    .wb_rom_sel_o       (wb_rom_sel_o),
    .wb_rom_we_o        (wb_rom_we_o),
    .wb_rom_cyc_o       (wb_rom_cyc_o),
    .wb_rom_stb_o       (wb_rom_stb_o),
    .wb_rom_cti_o       (wb_rom_cti_o),
    .wb_rom_bte_o       (wb_rom_bte_o),
    .wb_rom_rdt_i       (wb_rom_rdt_i),
    .wb_rom_ack_i       (wb_rom_ack_i),
    .wb_rom_err_i       (wb_rom_err_i),
    .wb_rom_rty_i       (wb_rom_rty_i),

    .wb_ext_flash_adr_o (wb_ext_flash_adr_o),
    .wb_ext_flash_dat_o (wb_ext_flash_dat_o),
    .wb_ext_flash_sel_o (wb_ext_flash_sel_o),
    .wb_ext_flash_we_o  (wb_ext_flash_we_o),
    .wb_ext_flash_cyc_o (wb_ext_flash_cyc_o),
    .wb_ext_flash_stb_o (wb_ext_flash_stb_o),
    .wb_ext_flash_cti_o (wb_ext_flash_cti_o),
    .wb_ext_flash_bte_o (wb_ext_flash_bte_o),
    .wb_ext_flash_rdt_i (wb_ext_flash_rdt_i),
    .wb_ext_flash_ack_i (wb_ext_flash_ack_i),
    .wb_ext_flash_err_i (wb_ext_flash_err_i),
    .wb_ext_flash_rty_i (wb_ext_flash_rty_i),

    .wb_spi_m_adr_o     (wb_spi_m_adr_o),
    .wb_spi_m_dat_o     (wb_spi_m_dat_o),
    .wb_spi_m_sel_o     (wb_spi_m_sel_o),
    .wb_spi_m_we_o      (wb_spi_m_we_o),
    .wb_spi_m_cyc_o     (wb_spi_m_cyc_o),
    .wb_spi_m_stb_o     (wb_spi_m_stb_o),
    .wb_spi_m_cti_o     (wb_spi_m_cti_o),
    .wb_spi_m_bte_o     (wb_spi_m_bte_o),
    .wb_spi_m_rdt_i     (wb_spi_m_rdt_i),
    .wb_spi_m_ack_i     (wb_spi_m_ack_i),
    .wb_spi_m_err_i     (wb_spi_m_err_i),
    .wb_spi_m_rty_i     (wb_spi_m_rty_i),

    .wb_uart_adr_o      (wb_uart_adr_o),
    .wb_uart_dat_o      (wb_uart_dat_o),
    .wb_uart_sel_o      (wb_uart_sel_o),
    .wb_uart_we_o       (wb_uart_we_o),
    .wb_uart_cyc_o      (wb_uart_cyc_o),
    .wb_uart_stb_o      (wb_uart_stb_o),
    .wb_uart_cti_o      (wb_uart_cti_o),
    .wb_uart_bte_o      (wb_uart_bte_o),
    .wb_uart_rdt_i      (wb_uart_rdt_i),
    .wb_uart_ack_i      (wb_uart_ack_i),
    .wb_uart_err_i      (wb_uart_err_i),
    .wb_uart_rty_i      (wb_uart_rty_i),

    .wb_ram_adr_o       (wb_ram_adr_o),
    .wb_ram_dat_o       (wb_ram_dat_o),
    .wb_ram_sel_o       (wb_ram_sel_o),
    .wb_ram_we_o        (wb_ram_we_o),
    .wb_ram_cyc_o       (wb_ram_cyc_o),
    .wb_ram_stb_o       (wb_ram_stb_o),
    .wb_ram_cti_o       (wb_ram_cti_o),
    .wb_ram_bte_o       (wb_ram_bte_o),
    .wb_ram_rdt_i       (wb_ram_rdt_i),
    .wb_ram_ack_i       (wb_ram_ack_i),
    .wb_ram_err_i       (wb_ram_err_i),
    .wb_ram_rty_i       (wb_ram_rty_i)
  );

endmodule
