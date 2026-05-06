// Auto-generated Verilog Testbench Wrapper - Coraltb 
 
`timescale 1ns/1ns 


module alu_wtb;

  // alu instantation signals
  reg   clk;
  reg   rst;
  reg  [3:0] A;
  reg  [3:0] B;
  reg  [15:0] instr_in;
  wire [3:0] acc;

alu dut (
      .clk(clk),
      .rst(rst),
      .A(A),
      .B(B),
      .instr_in(instr_in),
      .acc(acc)
  );

endmodule 
 