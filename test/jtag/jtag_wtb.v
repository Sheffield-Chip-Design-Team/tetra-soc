`default_nettype none
`timescale 1ns / 1ps

module jtag_wtb ();

  // Dump the signals to an FST file (CI expects tb.fst)
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, jtag_wtb);
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


  jtag_tap u_jtag_tap (
    .tck              (tck),
    // JTAG clock
    .tms              (tms),
    // JTAG mode select
    .tdi              (tdi),
    // JTAG data in
    .tdo              (tdo),
    // JTAG data out
    .trst_n           (trst_n),
    // Active-low JTAG reset 

    // Debug command outputs to dbg_unit.v
    .dbg_cmd          (dbg_cmd),
    .dbg_cmd_valid    (dbg_cmd_valid),
    // Optional debug/status wire for future readback
    .dbg_status       (dbg_status)
);
endmodule