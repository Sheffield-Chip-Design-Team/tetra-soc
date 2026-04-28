`default_nettype none
`timescale 1ns / 1ps

module debug_wtb ();

  // Dump the signals to an FST file (CI expects tb.fst)
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, debug_wtb);
    #1;
  end

  wire       clk;
  wire       rst_n;
  wire [7:0] dbg_cmd;
  wire       dbg_cmd_valid;

  reg        step_req;
  reg        resume_req;
  reg        halt_req;

  dbg_unit u_debug (
    .clk              (clk),
    .rst_n            (rst_n),
    // Command interface from future JTAG TAP / testbench
    .dbg_cmd          (dbg_cmd),
    .dbg_cmd_valid    (dbg_cmd_valid),
    // Request outputs to CPU control logic
    .step_req         (step_req),
    .resume_req       (resume_req),
    .halt_req         (halt_req)
  );

endmodule