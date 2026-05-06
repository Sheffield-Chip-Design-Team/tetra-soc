// Auto-generated Verilog Testbench Wrapper - Coraltb 
 
`timescale 1ns/1ns 


module alu_wtb;

  // alu instantation signals
  reg  [3:0] reg_a_val;
  reg  [3:0] reg_b_val;
  reg  [3:0] acc;
  reg  [5:0] alu_control;
  wire [3:0] result;
  wire  of_set;
  wire  uf_set;

alu dut (
      .reg_a_val(reg_a_val),
      .reg_b_val(reg_b_val),
      .acc(acc),
      .alu_control(alu_control),
      .result(result),
      .of_set(of_set),
      .uf_set(uf_set)
  );

endmodule 
 