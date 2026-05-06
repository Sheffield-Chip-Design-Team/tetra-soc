// =======================================================================
// Module:      Digital Top Level
// Project:     Tetra-SoC, by SHaRC
// Description: Top-level module for the Tetra-SoC, Tiny Tapeout Submission
// =======================================================================

`default_nettype none

module tt_um_tetra_soc (
  input  wire [7:0] ui_in,    // Dedicated inputs
  output wire [7:0] uo_out,   // Dedicated outputs
  input  wire [7:0] uio_in,   // IOs: Input path
  output wire [7:0] uio_out,  // IOs: Output path
  output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
  input  wire       ena,      // always 1 when the design is powered, so you can ignore it
  input  wire       clk,      // clock
  input  wire       rst_n     // reset_n - low to reset
);

  wire spi_cs_n;
  wire spi_sck;
  wire spi_mosi;
  wire spi_miso;

  wire jtag_tck;
  wire jtag_tms;
  wire jtag_tdi;
  wire jtag_tdo;

  wire uart_rx;
  wire uart_tx;

  wire vga_hsync;
  wire vga_vsync;

  wire [1:0] vga_rr;
  wire [1:0] vga_gg;
  wire [1:0] vga_bb;

  // TODO add clocking and reset logic as needed

  wire [15:0] dbg_addr_in = {ui_in[7:0], ui_in[7:0]};

  dig_top u_dig_top (
    .clk          (clk),
    .rst_n        (rst_n),
    // JTAG Debug interface
    .jtag_tck     (jtag_tck),
    .jtag_tms     (jtag_tms),
    .jtag_tdi     (jtag_tdi),
    .jtag_tdo     (jtag_tdo),

    // SPI Memory Interface
    .spi_cs_n     (spi_cs_n),
    .spi_sck      (spi_sck),
    .spi_mosi     (spi_mosi),
    .spi_miso     (spi_miso),

    // UART interface
    .uart_rx      (uart_rx),
    .uart_tx      (uart_tx), 

    .vga_hsync    (vga_hsync),  
    .vga_vsync    (vga_vsync),

    .vga_rr       (vga_rr), 
    .vga_gg       (vga_gg), 
    .vga_bb       (vga_bb),

    .dbg_addr_in    (dbg_addr_in),
    .dbg_data_in    (ui_in[7:0]),
    .dbg_addr_out   (),
    .dbg_data_out   ()
  );

// ------------------------------------------------------------------
// TinyTapeout pin mapping
// ------------------------------------------------------------------

  // JTAG inputs (to avoid floating Xs, map from ui_in)
  assign jtag_tck = ui_in[0];
  assign jtag_tms = ui_in[1];
  assign jtag_tdi = ui_in[2];

  // UART RX from an otherwise-unused uio_in bit
  assign uart_rx  = uio_in[4];
  
  // MISO from board / RAM model
  assign spi_miso     = uio_in[2];
  // Map SPI to uio pins
  assign uio_out[0]   = spi_cs_n;
  assign uio_out[2]   = 1'b0;
  assign uio_out[1]   = spi_mosi;
  assign uio_out[3]   = spi_sck;
  assign uio_out[6:4] = 3'b000;
  assign uio_out[7]   = uart_tx;

  assign uio_oe[0]    = 1'b1; // CS
  assign uio_oe[1]    = 1'b1; // MOSI
  assign uio_oe[3]    = 1'b1; // SCK
  assign uio_oe[2]    = 1'b0; // MISO input
  assign uio_oe[7:4]  = 4'b1000;

  // Main outputs: pack VGA onto uo_out (8 bits)
  // [0]=HSYNC, [1]=VSYNC, [3:2]=R, [5:4]=G, [7:6]=B
  assign uo_out[0]   = vga_hsync;
  assign uo_out[1]   = vga_vsync;
  assign uo_out[3:2] = vga_rr;
  assign uo_out[5:4] = vga_gg;
  assign uo_out[7:6] = vga_bb;

  // Mark unused bits of uio_in to keep verilator happy
  wire _unused = &{uio_in[7:5], ui_in[7:3], ena, jtag_tdo, 1'b0};

endmodule

`default_nettype wire


