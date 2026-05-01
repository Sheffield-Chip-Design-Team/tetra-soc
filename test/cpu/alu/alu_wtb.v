// Auto-generated Verilog Testbench Wrapper - Coraltb 
 
`timescale 1ns/1ns 


module alu_wtb;

  // alu instantation signals
  reg  [3:0] reg_a_val;
  reg  [3:0] reg_b_val;
  reg  [3:0] acc;
  reg  [5:0] alu_control;
  wire [3:0] result;
  wire  overflow;

alu dut (
      .reg_a_val(reg_a_val),
      .reg_b_val(reg_b_val),
      .acc(acc),
      .alu_control(alu_control),
      .result(result),
      .overflow(overflow)
  );

endmodule 
 