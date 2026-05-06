// =======================================================================
// Module:      Arithmetic Logic Unit 
// Project:     Tetra-SoC, by SHaRC
// Description: A combinational module that performs arithmetic 
//              and logic operations based on control signals.
// =======================================================================

module alu (
    input   wire            of_in,
    input   wire            uf_in,
    input   wire    [5:0]   alu_control,
    //              Bit 5: Enable
    //              Bit 4: Carry | Borrow   -   Taken from flags register
    //              Bit 3: AND | OR | XOR
    //              Bit 2: Add | Sub
    //              Bit 1: XOR | SHIFT
    //              Bit 0: Sub | OR | Dec | RSH
    input   wire    [3:0]   inp_a,
    input   wire    [3:0]   inp_b,
    input   wire    [3:0]   acc_val,
    output  reg     [3:0]   result,
    output  reg             of_set,
    output  reg             uf_set
);

wire use_of;
wire use_uf;

assign use_of = of_in & alu_control[4];
assign use_uf = uf_in & alu_control[4];

always @* begin
    if (alu_control[5]) begin
        case (alu_control[3:0])
            4'b0000: {of_set, result} <= acc_val + 1 + use_of;
            4'b0001: {uf_set, result} <= acc_val - 1 - use_uf;
            4'b0010: {of_set, result} <= {acc_val, use_of} << 1;
            4'b0011: {result, uf_set} <= {use_uf, acc_val} >> 1;
            4'b0100,
            4'b0110: {of_set, result} <= inp_a + inp_b + use_of;
            4'b0101,
            4'b0111: {uf_set, result} <= inp_a - inp_b - use_of;
            4'b1000,
            4'b1100: result <= inp_a & inp_b;
            4'b1001,
            4'b1101: result <= inp_a | inp_b;
            4'b1010,
            4'b1011,
            4'b1110,
            4'b1111: result <= inp_a ^ inp_b;
        endcase
    end
end

endmodule
