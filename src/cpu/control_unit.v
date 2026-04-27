// =======================================================================
// Module:      Control Unit
// Project:     Tetra-SoC, by SHaRC
// Description: Sequential module implementing the control FSM for the CPU
//              fetch-decode-execute cycle.
// =======================================================================

// TODO finalize the control unit ports

module control_unit (
    input wire [7:0] instr_byte,    // 8-bit instruction input
    output reg [3:0] alu_ctrl,      // ALU control signals
    output reg [1:0] shift_ctrl,
    output reg       acc_en,
    output reg       acc_clr,
    output reg       ram_we,
    output reg       reg_we,
);
    
    // TODO implement the control FSM here, with states for fetch, decode, execute, etc.
    // The control unit will generate control signals for the datapath and ALU based on the current state and opcode.


endmodule