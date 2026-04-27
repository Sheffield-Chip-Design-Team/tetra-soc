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












endmodule