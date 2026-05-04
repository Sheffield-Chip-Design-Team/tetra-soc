`default_nettype none
`timescale 1ns / 1ps

module jtag_debug_wtb ();

  // Dump the signals to an FST file (CI expects tb.fst)
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, jtag_debug_wtb);
    #1;
  end

  wire tck;
  wire tms;
  wire tdi;
  reg  tdo;
  wire trst_n;
  wire [7:0] dbg_cmd;
  wire       dbg_cmd_valid;
  wire [31:0] dbg_status;
  wire halt_req;
  wire resume_req;
  wire step_req;
  


  jtag_debug_wrapper u_jtag_debug_wrapper (
    .tck           (tck),
    .tms           (tms),
    .tdi           (tdi),
    .tdo           (tdo),
    .trst_n        (trst_n),
    .dbg_status    (dbg_status),
    .halt_req      (halt_req),
    .resume_req    (resume_req),
    .step_req      (step_req)
);
endmodule