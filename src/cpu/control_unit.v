module ControlUnit (
    input  [3:0] opcode,
    output reg display_outputreg,
    output reg sub_mode,
    output reg Add_mode,
    output reg str_intr_reg,
    output reg str_Acc,
    output reg clear_pc,
    output reg clear_acc,
    output reg clear_data_reg,
    output reg clear_output_reg,
    output reg load_PC,
    output reg XOR_mode,
    output reg NAND_mode,
    output reg GreaterThan_mode,
    output reg LessThan_mode
);



always @(*) begin
    case (opcode)
        4'b0000: begin // NOP
            display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end
        4'b0001: begin // STR Accumulator
            display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b1;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end

        4'b0010: begin // STR Instruction Register
            display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b1;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        
        end 

        4'b0011: begin // Add mode
            display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b1;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;

        end

        4'b0100: begin // sub mode  
            display_outputreg = 1'b0;
            sub_mode = 1'b1;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;


        end

        4'b0101: begin // Display output register
            display_outputreg = 1'b1;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;

        end

        4'b0110: begin // Clear PC
            display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b1;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end

        // Accumulator clear
        4'b0111: begin
            display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b1;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end

        //Clear data register
        4'b1000: begin
            display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b1;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end

        // Clear output register
        4'b1001: begin
            display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;            
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b1;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end
        // Additional cases for other opcodes can be added here

        4'b1010: begin // Load pc 
             display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b1;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end
        4'b1011: begin // XOR mode
         display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b1;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end
        4'b1100: begin // NAND mode
             display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b1;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end
        4'b1101: begin // Greater than mode
             display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b1;
            LessThan_mode = 1'b0;
        end
        4'b1110: begin // Less than mode
             display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b1;
        end

        default: begin
           display_outputreg = 1'b0;
            sub_mode = 1'b0;
            Add_mode = 1'b0;
            str_intr_reg = 1'b0;
            str_Acc = 1'b0;
            clear_pc = 1'b0;
            clear_acc = 1'b0;
            clear_data_reg = 1'b0;
            clear_output_reg = 1'b0;
            load_PC = 1'b0;
            XOR_mode = 1'b0;
            NAND_mode = 1'b0;
            GreaterThan_mode = 1'b0;
            LessThan_mode = 1'b0;
        end
    endcase


end 
endmodule