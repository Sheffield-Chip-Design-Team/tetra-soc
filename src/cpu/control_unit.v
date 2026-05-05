module ControlUnit (
    input  [11:0] instruction,
    // I assume an 'instruction' to have this format:
    // (opcode 4 bits)(sub on/off 1 with a logic mode bit 1 (total 2 bits))(Logic or aritmetic bit)( immediate adrressing 1 bit)(operand 4 bits)
    output reg [5:0] alu_control

);

always @(*) begin

    case(instruction[11:8]) // Isolating the opcode to determine the type of operation
        // This is going off Aivas ALU module with the instruction google sheet.
        4'b0001: begin // ALU operations
            case(instruction[7:5]) // Isolating the "Sub bit" to determine if it's an addition or subtraction operation
            3'b000: alu_control = 6'd1; // Addition
            3'b100: alu_control = 6'd2; // Subtraction  
            3'b001: alu_control = 6'd16; // A AND B
            //3'b011: alu_control = whatever binary number it is; // A OR B
            3'b101: alu_control = 6'd32; // A XOR B
            default: alu_control = 6'd0; // Default case 

            endcase
        end
        default: alu_control = 6'd0; // Default case for unsupported opcodes
    endcase  
end 
endmodule