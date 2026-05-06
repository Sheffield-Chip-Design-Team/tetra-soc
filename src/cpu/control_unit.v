module ControlUnit (
    input  [15:0]   instruction,
    input  [3:0]    flags,
    // I assume an 'instruction' to have this format:
    // (opcode 4 bits)(sub on/off 1 with a logic mode bit 1 (total 2 bits))(Logic or aritmetic bit)( immediate adrressing 1 bit)(operand 4 bits)
    output reg [5:0] alu_control

);

wire    alu_en;
assign  alu_en = (instruction[3:0] == 1) | (instruction[3:0] == 2);

wire    opcode;
assign  opcode = instruction[3:0];

wire    operand;
assign  operand = instruction[7:4];

always @(*) begin
    case ({operand, opcode})
        8'b00000001,    // ADD Imp
        8'b00010001,    // SUB Imp
        8'b10010001,    // ADD IMM
        8'b10010001:    // SUB IMM
        begin
            alu_control[4] <= flags[2];
            alu_control[3] <= 0;
            alu_control[2] <= 1;
            alu_control[1] <= 0;
            alu_control[0] <= instruction[4];
        end
    endcase
end 
endmodule
