// =======================================================================
// Module:      SPI Read Byte
// Project:     Tetra-SoC, by SHaRC
// Description: Reads one byte from 23LC512-style SPI RAM.
//              Uses command 0x03 + 16-bit address.
// =======================================================================

module wb_spi_mem_ctrl(
  input  wire        clk,
  input  wire        rst_n,

  // Control signals from regs
  input  wire [15:0] addr,       // address in external RAM
  input  wire        start,      // pulse to start transaction 

  // Status back to regs
  output reg         busy,       // set while transactions are in progress
  output reg         valid,      // 1 for one clk when data_out is valid
  output reg  [7:0]  data_out,   // received byte

  // SPI signals
  output reg         cs_n,       // active-low chip select
  output reg         sck,        // SPI clock (mode 0)
  output reg         mosi,       // master-out
  input  wire        miso        // master-in
);

  spi_mem_ctrl_core core (
    .clk(clk),
    .rst_n(rst_n),
    .addr(addr),
    .start(start),
    .seq_mode(1'b1),   // not sequential mode
    .last(),       // only one byte to read
    .busy(busy),
    .valid(valid),
    .data_out(data_out),
    .cs_n(cs_n),
    .sck(sck),
    .mosi(mosi),
    .miso(miso)
  );


  // Registers
  // create 
