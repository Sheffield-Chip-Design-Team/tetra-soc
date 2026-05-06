// =======================================================================
// Module:      Debug Interface
// Project:     Tetra-SoC, by SHaRC
// Description: Debug interface for system monitoring and diagnostics.
// =======================================================================

module debug (
  // JTAG Interface
  output reg step_req,
  output reg resume_req,
  output reg halt_req
);
  // Registers
  wire breakpoint_set;
  wire breakpoint_clear;
  wire breakpoint_addr;
  wire breakpoint_hit;

endmodule   

