// Auto-generated Verilog Testbench Wrapper - Coraltb 
 
`timescale 1ns/1ns 


module control_unit_wtb;

  // control_unit instantation signals
  reg  [15:0] instruction;
  reg  [3:0] flags;
  wire [5:0] alu_control;

control_unit dut (
      .instruction(instruction),
      .flags(flags),
      .alu_control(alu_control)
  );

endmodule 
 