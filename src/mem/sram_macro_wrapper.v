`default_nettype none

// =======================================================================
// Module:      sram_macro_wrapper
// Project:     Tetra-SoC, by SHaRC
// Description: Wrapper layer for swapping between a generic simulation
//              SRAM model and a sky130/OpenRAM SRAM macro model.
// =======================================================================
//
// Default mode:
//   Uses sram_1rw as a simple behavioural simulation model.
//
// USE_OPENRAM_MODEL mode:
//   Intended to instantiate a provided sky130/OpenRAM SRAM Verilog model.
//   The exact macro module name and ports should be updated once the
//   generated/provided SRAM model is selected.
//
// Target configuration:
//   DATA_WIDTH = 8
//   ADDR_WIDTH = 10
//   Capacity   = 1024 x 8-bit = 1KiB
// =======================================================================

module sram_macro_wrapper #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 10
)(
    input  wire                  clk,
    input  wire                  rst_n,

    input  wire                  we,
    input  wire [ADDR_WIDTH-1:0] addr,
    input  wire [DATA_WIDTH-1:0] wdata,
    output wire [DATA_WIDTH-1:0] rdata
);

`ifdef USE_OPENRAM_MODEL

    // TODO:
    // Replace this block with the selected sky130/OpenRAM SRAM model.
    // Exact module name and port names must match the provided model.

    sky130_sram_1kbyte_1rw1r_8x1024_8 u_sram_macro (
        .clk0  (clk),
        .csb0  (1'b0),
        .web0  (~we),
        .addr0 (addr),
        .din0  (wdata),
        .dout0 (rdata)
    );

`else

    sram_1rw #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) u_generic_sram (
        .clk   (clk),
        .rst_n (rst_n),
        .we    (we),
        .addr  (addr),
        .wdata (wdata),
        .rdata (rdata)
    );

`endif

endmodule

`default_nettype wire
