// Auto-generated Verilog Testbench Wrapper - Coraltb 
 
`timescale 1ns/1ns 


module reg_file_wtb;

  // reg_file instantation signals
  reg   clk;
  reg   a_en;
  reg   b_en;
  reg   s_en;
  reg   of_in;
  reg   uf_in;
  reg  [3:0] d_in;
  wire [3:0] ra_out;
  wire [3:0] rb_out;
  wire [3:0] rs_out;

reg_file dut (
      .clk(clk),
      .a_en(a_en),
      .b_en(b_en),
      .s_en(s_en),
      .of_in(of_in),
      .uf_in(uf_in),
      .d_in(d_in),
      .ra_out(ra_out),
      .rb_out(rb_out),
      .rs_out(rs_out)
  );

endmodule 
 