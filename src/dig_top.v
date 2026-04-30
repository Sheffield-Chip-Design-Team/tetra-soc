// =======================================================================
// Module:      Digital Top Level
// Project:     Tetra-SoC, by SHaRC
// Description: Top-level digital module integrating all SoC components.
// =======================================================================

module dig_top (
    input  wire       clk,  
    input  wire       rst_n,

    // JTAG Debug interface
    input wire        jtag_tck,   // ui_in
    input wire        jtag_tms,   // ui_in
    input wire        jtag_tdi,   // ui_in
    output wire       jtag_tdo,   // uo_out

    // SPI Memory Interface
    output wire       spi_cs_n,   // uio_out
    output wire       spi_sck,    // uio_out
    output wire       spi_mosi,   // uio_out
    input  wire       spi_miso,   // uio_in

    // UART interface
    input wire        uart_rx,    // uio_in
    output wire       uart_tx,    // uio_out

    // VGA interface
    output wire       vga_hsync,  // uo_out
    output wire       vga_vsync,  // uo_out
    output wire [1:0] vga_rr,     // uo_out
    output wire [1:0] vga_gg,     // uo_out
    output wire [1:0] vga_bb      // uo_out
);

// -----------------------------------------------------------------------------
// Internal Signals
// -----------------------------------------------------------------------------

  // CPU Wishbone 8-bit slave bus
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

  // ROM port (unused)
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

  // RAM port (unused)
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

  // UART port (unused in this test)
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

  // SPI-m port (connected)
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

// -----------------------------------------------------------------------------
// CPU
// -----------------------------------------------------------------------------



// -----------------------------------------------------------------------------
// Interconnect
// -----------------------------------------------------------------------------

    intercon_ss u_intercon_ss (
        .sys_clk               (clk),
        .sys_rst_n             (rst_n),

        // CPU Wishbone Slave Interface
        .wb_cpu_s_adr_i        (wb_cpu_s_adr_i),
        .wb_cpu_s_dat_i        (wb_cpu_s_dat_i),
        .wb_cpu_s_we_i         (wb_cpu_s_we_i),
        .wb_cpu_s_cyc_i        (wb_cpu_s_cyc_i),
        .wb_cpu_s_stb_i        (wb_cpu_s_stb_i),
        .wb_cpu_s_cti_i        (wb_cpu_s_cti_i),
        .wb_cpu_s_bte_i        (wb_cpu_s_bte_i),
        .wb_cpu_s_dat_o        (wb_cpu_s_dat_o),
        .wb_cpu_s_ack_o        (wb_cpu_s_ack_o),
        .wb_cpu_s_err_o        (wb_cpu_s_err_o),
        .wb_cpu_s_rty_o        (wb_cpu_s_rty_o),
        
        // Wishbone peripheral interfaces (8-bit slaves)
        // ROM
        .wb_rom_adr_o          (wb_rom_adr_o),
        .wb_rom_dat_o          (wb_rom_dat_o),
        .wb_rom_sel_o          (wb_rom_sel_o),
        .wb_rom_we_o           (wb_rom_we_o),
        .wb_rom_cyc_o          (wb_rom_cyc_o),
        .wb_rom_stb_o          (wb_rom_stb_o),
        .wb_rom_cti_o          (wb_rom_cti_o),
        .wb_rom_bte_o          (wb_rom_bte_o),
        .wb_rom_rdt_i          (wb_rom_rdt_i),
        .wb_rom_ack_i          (wb_rom_ack_i),
        .wb_rom_err_i          (wb_rom_err_i),
        .wb_rom_rty_i          (wb_rom_rty_i),

        // External Flash 
        .wb_ext_flash_adr_o    (),
        .wb_ext_flash_dat_o    (),
        .wb_ext_flash_sel_o    (),
        .wb_ext_flash_we_o     (),
        .wb_ext_flash_cyc_o    (),
        .wb_ext_flash_stb_o    (),
        .wb_ext_flash_cti_o    (),
        .wb_ext_flash_bte_o    (),
        .wb_ext_flash_rdt_i    (),
        .wb_ext_flash_ack_i    (),
        .wb_ext_flash_err_i    (),
        .wb_ext_flash_rty_i    (),

        .wb_spi_m_adr_o        (wb_spi_m_adr_o),
        .wb_spi_m_dat_o        (wb_spi_m_dat_o),
        .wb_spi_m_sel_o        (wb_spi_m_sel_o),
        .wb_spi_m_we_o         (wb_spi_m_we_o),
        .wb_spi_m_cyc_o        (wb_spi_m_cyc_o),
        .wb_spi_m_stb_o        (wb_spi_m_stb_o),
        .wb_spi_m_cti_o        (wb_spi_m_cti_o),
        .wb_spi_m_bte_o        (wb_spi_m_bte_o),
        .wb_spi_m_rdt_i        (wb_spi_m_rdt_i),
        .wb_spi_m_ack_i        (wb_spi_m_ack_i),
        .wb_spi_m_err_i        (wb_spi_m_err_i),
        .wb_spi_m_rty_i        (wb_spi_m_rty_i),
        
        // UART 
        .wb_uart_adr_o         (wb_uart_adr_o),
        .wb_uart_dat_o         (wb_uart_dat_o),
        .wb_uart_sel_o         (wb_uart_sel_o),
        .wb_uart_we_o          (wb_uart_we_o),
        .wb_uart_cyc_o         (wb_uart_cyc_o),
        .wb_uart_stb_o         (wb_uart_stb_o),
        .wb_uart_cti_o         (wb_uart_cti_o),
        .wb_uart_bte_o         (wb_uart_bte_o),
        .wb_uart_rdt_i         (wb_uart_rdt_i),
        .wb_uart_ack_i         (wb_uart_ack_i),
        .wb_uart_err_i         (wb_uart_err_i),
        .wb_uart_rty_i         (wb_uart_rty_i),

        .wb_ram_adr_o          (wb_ram_adr_o),
        .wb_ram_dat_o          (wb_ram_dat_o),
        .wb_ram_sel_o          (wb_ram_sel_o),
        .wb_ram_we_o           (wb_ram_we_o),
        .wb_ram_cyc_o          (wb_ram_cyc_o),
        .wb_ram_stb_o          (wb_ram_stb_o),
        .wb_ram_cti_o          (wb_ram_cti_o),
        .wb_ram_bte_o          (wb_ram_bte_o),
        .wb_ram_rdt_i          (wb_ram_rdt_i),
        .wb_ram_ack_i          (wb_ram_ack_i),
        .wb_ram_err_i          (wb_ram_err_i),
        .wb_ram_rty_i          (wb_ram_rty_i)
    );

// -----------------------------------------------------------------------------
// SPI Memory Controller
// -----------------------------------------------------------------------------

  wb_spi_mem_ctrl_wb u_spi (
    .clk            (clk),
    .rst_n          (rst_n),

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


endmodule