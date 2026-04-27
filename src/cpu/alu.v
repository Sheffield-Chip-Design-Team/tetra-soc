// =======================================================================
// Module:      Arithmetic Logic Unit 
// Project:     Tetra-SoC, by SHaRC
// Description: A combinational module that performs arithmetic 
//              and logic operations based on control signals.
// =======================================================================

module ALU(
    input [3:0] A,       // First operand
    input [3:0] B,       // Second operand
    input submode,
    input addmode,
    input XORmode,
    input NANDmode,
    input GreaterThanmode,
    input LessThanmode,
    output reg [3:0] Result // ALU result
);

always@(*) begin
    if (submode) begin
        Result <= A-B;

    end else if (addmode) begin
        Result <= A+B;

    end else if (XORmode) begin
        Result <= A^B;

    end else if (NANDmode) begin
        Result <= ~(A&B);

    end else if (GreaterThanmode) begin
        Result <= (A > B) ? 4'b0001 : 4'b0000; // 1 if A > B, else 0

    end else if (LessThanmode) begin
        Result <= (A < B) ? 4'b0001 : 4'b0000; // 1 if A < B, else 0

    end else begin
        Result <= 4'b0000; // Default case
    end

end 

endmodule
