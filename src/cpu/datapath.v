// =======================================================================
// Module:      CPU Datapath
// Project:     Tetra-SoC, by SHaRC
// Description: Sequential module implementing the datapath for the CPU,
//              including registers, ALU, and shifter.
// =======================================================================

module datapath #(
  parameter DATA_WIDTH  = 4
)(
  // clock and reset
  input wire                   clk,
  input wire                   rst_n,

  // control signals 
  input wire                   alu_ctrl,
  input wire                   shift_ctrl,  
  
  // RAM Interface
  input wire  [DATA_WIDTH-1:0] ram_wdata,
  output reg                   ram_en,
  output reg                   ram_we,
  input wire  [DATA_WIDTH-1:0] ram_rdata,
  output reg  [DATA_WIDTH-1:0] ram_addr,

);
  

  // Regsiter File 
  // TODO instantiate the register file.

  // Shifter Logic
  // TODO instantiate the shifter.

  // MUX 
  //define a mux for controlling the ALU input.

  // ALU
  // TODO instantiate the ALU.

  
  // Status Register
  // TODO define a status register to hold flags like zero, carry, etc.

  // Accumulator 

  
  // RAM Access 
endmodule

