module control_unit (
    input  [15:0]   instruction,
    input  [3:0]    flags,
    output reg [5:0] alu_control

);

wire    alu_en;
assign  alu_en = (instruction[3:0] == 1) | (instruction[3:0] == 2);

wire    [3:0]   opcode;
assign          opcode = instruction[3:0];

wire    [3:0]   operand;
assign          operand = instruction[7:4];

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
        8'b10000001,    // ADD IMM
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

        
        8'b00000010, //INC
        8'b00010010, //DEC
        8'b00100010, //LSH
        8'b00110010, //RSH
        8'b01000010, //INC
        8'b01010010, //DEC
        8'b01100010, //LSH
        8'b01110010, //RSH
        8'b10000010, //INC
        8'b10010010, //DEC
        8'b10100010, //LSH
        8'b10110010, //RSH
        8'b11000010, //INC
        8'b11010010, //DEC
        8'b11100010, //LSH
        8'b11110010: //RSH
        begin 
            alu_control[5] <= 1;
            alu_control[4] <= (instruction[4] & flags[3]) | (!instruction[4] & flags[2]);
            alu_control[3] <= 0;
            alu_control[2] <= 0;
            alu_control[1] <= instruction[6];
            alu_control[0] <= instruction[5];

        end


        default:begin 
             alu_control <= 0;

        end
    endcase

end 
endmodule






