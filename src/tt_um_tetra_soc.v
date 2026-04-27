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

  dig_top tetra_soc (
    .clk      (clk),
    .rst_n    (rst_n),
    .spi_cs_n (spi_cs_n),
    .spi_sck  (spi_sck),
    .spi_mosi (spi_mosi),  
    .spi_miso (spi_miso),   
  );

  // MISO from board / RAM model
  assign spi_miso     = uio_in[2];

  // Map SPI to uio pins
  assign uio_out[0]   = spi_cs_n;
  assign uio_out[2]   = 1'b0;
  assign uio_out[1]   = spi_mosi;
  assign uio_out[3]   = spi_sck;
  assign uio_out[6:4] = 3'b000;
  assign uio_out[7]   = valid;

  assign uio_oe[0]    = 1'b1; // CS
  assign uio_oe[1]    = 1'b1; // MOSI
  assign uio_oe[3]    = 1'b1; // SCK
  assign uio_oe[2]    = 1'b0; // MISO input
  assign uio_oe[7:4]  = 4'b1000;

  // CPU result on main outputs
  // assign uo_out  = ena ? cpu_out : 8'h00; // use ena
  assign uo_out  = cpu_out;

  // Mark unused bits of uio_in to keep verilator happy
  wire _unused = &{uio_in[7:3], ena, 1'b0};
endmodule

`default_nettype wire


