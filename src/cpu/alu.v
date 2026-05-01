// =======================================================================
// Module:      Arithmetic Logic Unit 
// Project:     Tetra-SoC, by SHaRC
// Description: A combinational module that performs arithmetic 
//              and logic operations based on control signals.
// =======================================================================

module alu (
    input   wire    [3:0]   reg_a_val,
    input   wire    [3:0]   reg_b_val,
    input   wire    [3:0]   acc,
    input   wire    [5:0]   alu_control,
    output  reg     [3:0]   result,
    output  reg             overflow
);

always @* begin
    
    case (alu_control)
        6'd1:   {overflow, result}  = reg_a_val + reg_b_val;
        6'd2:   result              = reg_a_val-reg_b_val;
        6'd4:   result              = acc << 1;
        6'd8:   result              = acc >> 1;
        6'd16:  result              = reg_a_val & reg_b_val;
        6'd32:  result              = reg_a_val ^ reg_b_val;
        default: begin
                result      = 4'd0;
                overflow    = 1'd0;
        end
    endcase

end

endmodule
