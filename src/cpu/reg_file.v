// =======================================================================
// Module:      Register File
// Project:     Tetra-SoC, by SHaRC
// Description: Dual-port register file for CPU register storage.
// =======================================================================

module reg_file(
  input             clk,
  input             a_en,   // a_en, b_en, and s_en should all be mutually exclusive.
  input             b_en,   //
  input             s_en,   //
  input             of_in,  // taken from the result of alu operations
  input             uf_in,  //
  input       [3:0] d_in,
  output  reg [3:0] ra_out,
  output  reg [3:0] rb_out, 
  output  reg [3:0] rs_out
);

wire  [3:0] a_mask;
wire  [3:0] b_mask;
wire  [3:0] s_mask;

wire  [3:0] s_val;

assign  a_mask = d_in & {4{a_en}};
assign  b_mask = d_in & {4{b_en}};
assign  s_val = rs_out;

assign  s_mask[0] = (d_in[0] & {s_en}) | of_in | (rs_out[0] & !s_en);
assign  s_mask[1] = (d_in[1] & {s_en}) | uf_in | (rs_out[1] & !s_en);
assign  s_mask[3:2] = (d_in[3:2] & {2{s_en}}) | (rs_out[3:2] & {2{!s_en}});

 // TODO write the register file logic
always @(posedge clk) begin
  ra_out <= a_mask;
  rb_out <= b_mask;
  rs_out <= s_mask;
end

endmodule

