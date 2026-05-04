// =======================================================================
// Module:      JTAG TAP
// Project:     Tetra-SoC, by SHaRC
// Description: Minimal JTAG TAP for debug command transfer.
// =======================================================================
//
// This module implements a small JTAG Test Access Port (TAP)
//
// Its main purpose is to receive an 8-bit debug command through the JTAG
// serial interface and expose it to dbg_unit.v as:
//
// dbg_cmd
// dbg_cmd_valid
//
// Supported instructions:
//
// IR_IDCODE    : shift out a fixed 32-bit ID code
// IR_DBG_CMD   : shift in an 8-bit debug command
// IR_DBG_STATUS: shift out a 32-bit status word
// IR_BYPASS    : 1-bit bypass register
//
// JTAG shifting is LSB-first, which is the normal JTAG convention.
// =======================================================================

module jtag_tap(
    input wire tck,    // JTAG clock
    input wire tms,    // JTAG mode select
    input wire tdi,    // JTAG data in
    output reg tdo,    // JTAG data out
    input wire trst_n, // Active-low JTAG reset 

    // Debug command outputs to dbg_unit.v
    output reg [7:0] dbg_cmd,
    output reg       dbg_cmd_valid,

    // Optional debug/status wire for future readback
    input wire [31:0] dbg_status
);

    // -------------------------------------------------------------------
    // TAP state encoding
    // -------------------------------------------------------------------
    localparam TEST_LOGIC_RESET = 4'd0;
    localparam RUN_TEST_IDLE    = 4'd1;

    localparam SELECT_DR_SCAN   = 4'd2;
    localparam CAPTURE_DR       = 4'd3;
    localparam SHIFT_DR         = 4'd4;
    localparam EXIT1_DR         = 4'd5;
    localparam PAUSE_DR         = 4'd6;
    localparam EXIT2_DR         = 4'd7;
    localparam UPDATE_DR        = 4'd8;

    localparam SELECT_IR_SCAN   = 4'd9;
    localparam CAPTURE_IR       = 4'd10;
    localparam SHIFT_IR         = 4'd11;
    localparam EXIT1_IR         = 4'd12;
    localparam PAUSE_IR         = 4'd13;
    localparam EXIT2_IR         = 4'd14;
    localparam UPDATE_IR        = 4'd15;

    reg [3:0] tap_state;
    reg [3:0] tap_next_state;

    // -------------------------------------------------------------------
    // Instruction register
    // -------------------------------------------------------------------
    localparam IR_WIDTH = 4;

    localparam IR_IDCODE    = 4'h1;
    localparam IR_DBG_CMD   = 4'h2;
    localparam IR_DBG_STATUS= 4'h3;
    localparam IR_BYPASS    = 4'hF;

    reg [IR_WIDTH-1:0] ir_shift;
    reg [IR_WIDTH-1:0] ir_current;

    // -------------------------------------------------------------------
    // Data registers
    // -------------------------------------------------------------------
    reg [7:0]  cmd_shift;
    reg [31:0] status_shift;
    reg        bypass_shift;

    // Simple fixed ID value for now
    // This can be changed later if the team wants a specific project ID
    localparam [31:0] IDCODE_VALUE = 32'hDEADBEEF;

    // -------------------------------------------------------------------
    // TAP next-state logic
    // -------------------------------------------------------------------
    always @(*) begin
        case (tap_state)
            
            TEST_LOGIC_RESET: begin
                tap_next_state = tms ? TEST_LOGIC_RESET : RUN_TEST_IDLE;
            end

            RUN_TEST_IDLE: begin
                tap_next_state = tms ? SELECT_DR_SCAN : RUN_TEST_IDLE;
            end

            SELECT_DR_SCAN: begin
                tap_next_state = tms ? SELECT_IR_SCAN : CAPTURE_DR;
            end

            CAPTURE_DR: begin
                tap_next_state = tms ? EXIT1_DR : SHIFT_DR;
            end

            SHIFT_DR: begin
                tap_next_state = tms ? EXIT1_DR : SHIFT_DR;
            end

            EXIT1_DR: begin
                tap_next_state = tms ? UPDATE_DR : PAUSE_DR;
            end

            PAUSE_DR: begin
                tap_next_state = tms ? EXIT2_DR : PAUSE_DR;
            end

            EXIT2_DR: begin
                tap_next_state = tms ? UPDATE_DR : SHIFT_DR;
            end

            UPDATE_DR: begin
                tap_next_state = tms ? SELECT_DR_SCAN : RUN_TEST_IDLE;
            end

            SELECT_IR_SCAN: begin
                tap_next_state = tms ? TEST_LOGIC_RESET : CAPTURE_IR;
            end

            CAPTURE_IR: begin
                tap_next_state = tms ? EXIT1_IR : SHIFT_IR;
            end

            SHIFT_IR: begin
                tap_next_state = tms ? EXIT1_IR : SHIFT_IR;
            end

            EXIT1_IR: begin
                tap_next_state = tms ? UPDATE_IR : PAUSE_IR;
            end

            PAUSE_IR: begin
                tap_next_state = tms ? EXIT2_IR : PAUSE_IR;
            end

            EXIT2_IR: begin
                tap_next_state = tms ? UPDATE_IR : SHIFT_IR;
            end

            UPDATE_IR: begin
                tap_next_state = tms ? SELECT_DR_SCAN : RUN_TEST_IDLE;
            end

            default: begin
                tap_next_state = TEST_LOGIC_RESET;
            end
            
        endcase
    end

    // -------------------------------------------------------------------
    // TAP sequential logic
    // -------------------------------------------------------------------
    always @(posedge tck or negedge trst_n) begin
        if (!trst_n) begin
            tap_state     <= TEST_LOGIC_RESET;

            ir_shift      <= IR_IDCODE;
            ir_current    <= IR_IDCODE;

            cmd_shift     <= 8'h00;
            status_shift  <= 32'h0000_0000;
            bypass_shift  <= 1'b0;

            dbg_cmd       <= 8'h00;
            dbg_cmd_valid <= 1'b0;
        end
        else begin
            tap_state <= tap_next_state;

            // dbg_cmd_valid is only a one-TCK-cycle pulse
            dbg_cmd_valid <= 1'b0;

            case (tap_state)

                // Instruction register path

                CAPTURE_IR: begin
                    // JTAG convention: captured IR should end with 2'b01
                    ir_shift <= 4'b0001;
                end

                SHIFT_IR: begin
                    // Shift in LSB-first
                    // TDI enters the MSB side, current LSB shifts out on TDO
                    ir_shift <= {tdi, ir_shift[IR_WIDTH-1:1]};
                end

                UPDATE_IR: begin
                    ir_current <= ir_shift;
                end

                // Data register path

                CAPTURE_DR: begin
                    case (ir_current)

                        IR_IDCODE: begin
                            status_shift <= IDCODE_VALUE;
                        end

                        IR_DBG_STATUS: begin
                            status_shift <= dbg_status;
                        end

                        IR_DBG_CMD: begin
                            cmd_shift <= 8'h00;
                        end

                        IR_BYPASS: begin
                            bypass_shift <= 1'b0;
                        end

                        default: begin
                            bypass_shift <= 1'b0;
                        end
                        
                    endcase
                end

                SHIFT_DR: begin
                    case (ir_current)

                        IR_IDCODE, IR_DBG_STATUS: begin
                            status_shift <= {tdi, status_shift[31:1]};
                        end

                        IR_DBG_CMD: begin
                            cmd_shift <= {tdi, cmd_shift[7:1]};
                        end

                        IR_BYPASS: begin
                            bypass_shift <= tdi;
                        end

                        default: begin
                            bypass_shift <= tdi;
                        end
                        
                    endcase
                end

                UPDATE_DR: begin
                    if (ir_current == IR_DBG_CMD) begin
                        dbg_cmd       <= cmd_shift;
                        dbg_cmd_valid <= 1'b1;
                    end
                end

                default: begin
                    // No action required in other states
                end
                
            endcase
        end
    end

    // ----------------------------------------------------------------
    // TDO output logic
    // ----------------------------------------------------------------
    //
    // JTAG convention is that TDO updates on the falling edge of TCK.
    // During SHIFT_IR, TDO shows the current IR LSB.
    // During SHIFT_DR, TDO shows the selected DR LSB.
    //
    always @(negedge tck or negedge trst_n) begin
        if (!trst_n) begin
            tdo <= 1'b0;
        end
        else begin
            case (tap_state)

                SHIFT_IR: begin
                    tdo <= ir_shift[0];
                end

                SHIFT_DR: begin
                    case (ir_current)

                        IR_IDCODE, IR_DBG_STATUS: begin
                            tdo <= status_shift[0];
                        end

                        IR_DBG_CMD: begin
                            tdo <= cmd_shift[0];
                        end

                        IR_BYPASS: begin
                            tdo <= bypass_shift;
                        end

                        default: begin
                            tdo <= bypass_shift;
                        end
                        
                    endcase
                end

                default: begin
                    tdo <= 1'b0;
                end
                
            endcase
        end
    end
    
endmodule
