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

// ALU CONTROL BIT LOGIC REMINDER:

// [5] ALU ENABLE
// [4] CARRY or Borrow flag
// [3] LOGIC bit (1 for logic, 0 for arithmetic or shift)
// [2] Arithemtic bit (1 for add/sub, 0 for logic or shift)
// [1] XOR OR SHIFT depending on what other bits are high
// [0] SUB, OR, DEC, RSH depending on what other bits are high


always @(*) begin
    case ({operand, opcode})
        8'b00000001,    // ADD Imp
        8'b00010001,    // SUB Imp
        8'b10010001,    // ADD IMM
        8'b10010001:    // SUB IMM
        begin
            alu_control[5] <= 1;
            alu_control[4] <= flags[2];
            alu_control[3] <= 0;
            alu_control[2] <= 1;
            alu_control[1] <= 0;
            alu_control[0] <= instruction[4];
        end
        8'b01000001,    // AND Imp
        8'b01010001,    // OR Imp
        8'b01100001,    // XOR Imp
        8'b11000001,    // AND Immediate
        8'b11010001,    // OR Immediate
        8'b11100001:   // XOR Immediate
        begin
            alu_control[5] <= 1;
            alu_control[4] <= flags[2];
            alu_control[3] <= 1;
            alu_control[2] <= 0;
            alu_control[1] <= instruction[5];
            alu_control[0] <= instruction[4];
        end

        
        6'b000010, //INC
        6'b010010, //DEC
        6'b100010, //LSH
        6'b110010: //RSH
        begin 
            alu_control[5] <= 1;
            alu_control[4] <= flags[2];
            alu_control[3] <= 0;
            alu_control[2] <= 0;
            alu_control[1] <= instruction[6];
            alu_control[0] <= instruction[5];

        end

   

      

        default: alu_control <= 0;
    endcase

end 
endmodule
