// =======================================================================
// Module:      Register File
// Project:     Tetra-SoC, by SHaRC
// Description: Dual-port register file for CPU register storage.
// =======================================================================

module reg_file #(
  parameter DATA_WIDTH = 4     
)(
  input                     clk,
  input                     rst_n,
  input  [1:0]              reg_wstrb,
  input  [DATA_WIDTH-1:0]  ra_d,
  input  [DATA_WIDTH-1:0]  rb_in,
  output [DATA_WIDTH-1:0]  ra_out,
  output [DATA_WIDTH-1:0]  rb_out, 
);

 // TODO write the register file logic


endmodule

