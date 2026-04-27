// =======================================================================
// Module:      Arithmetic Logic Unit 
// Project:     Tetra-SoC, by SHaRC
// Description: A combinational module that performs arithmetic 
//              and logic operations based on control signals.
// =======================================================================

module ALU(
    input [3:0] A,      
    input [3:0] B, 
    input [15:0] instr_in,
    //bit 0 - 8 - Instruction bits
    //bit 9 - 15 - Redundant.
    
    output reg [3:0] acc // output stored in accumulator 

);

always@(*) begin

    case (instr_in[8:0]) // Check the instruction bits
        11'b00100000000: acc <= A + B; // ADD
        11'b00100000001: acc <= A - B; // SUB
        11'b00100000010: acc <= A&B; // AND
        11'b00100000011: acc <= !acc; // NOT - Inverting accumulator.
        11'b00100000100: acc <= A^B ;//A XOR B
        11'b00100000101: acc <= acc<<1; //shift left by 1
        11'b00100000110: acc <= acc>>1; //shift right by 1
        //11'b00100000100: GreaterThanmod = 1; // Greater Than // change the bits
       // 11'b00100100101: LessThanmode = 1; // Less Than // changes the bits
        default: begin
            acc <= acc;
        end
    endcase
end 

endmodule
