// =======================================================================
// Module:      Debug Interface
// Project:     Tetra-SoC, by SHaRC
// Description: Simple debug command decoder for halt, stop, and resume.
// =======================================================================

module debug (
  input wire       clk,
  input wire       rst_n,

  // Command interface from future JTAG TAP / testbench
  input wire [7:0] dbg_cmd,
  input wire       dbg_cmd_valid,

  // Request outputs to CPU control logic
  output reg       step_req,
  output reg       resume_req,
  output reg       halt_req
);
  
  // Debug command encodings
  localparam DBG_NOP    = 8'h00;
  localparam DBG_HALT   = 8'h01;
  localparam DBG_RESUME = 8'h02;
  localparam DBG_STEP   = 8'h03;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      step_req   <= 1'b0;
      resume_req <= 1'b0;
      halt_req   <= 1'b0;
    end
    
    else begin
      // Default low so requests are one-clock-cycle pulses
      step_req   <= 1'b0;
      resume_req <= 1'b0;
      halt_req   <= 1'b0;

      if (dbg_cmd_valid) begin
        case (dbg_cmd)
          DBG_HALT: begin
            halt_req <= 1'b1;
          end

          DBG_RESUME: begin
            resume_req <= 1'b1;
          end

          DBG_STEP: begin
            step_req <= 1'b1;
          end
 
          default: begin
            step_req   <= 1'b0;
            resume_req <= 1'b0;
            halt_req   <= 1'b0;
          end 
        endcase
      end
    end
  end

endmodule   

