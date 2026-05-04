`default_nettype none

// =======================================================================
// Module:      sram_1rw
// Project:     Tetra-SoC, by SHaRC
// Description: Simple parameterised single-port read/write SRAM.
// =======================================================================

module sram_1rw #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 8
)(
    input  wire                  clk,
    input  wire                  rst_n,

    input  wire                  we,
    input  wire [ADDR_WIDTH-1:0] addr,
    input  wire [DATA_WIDTH-1:0] wdata,
    output wire [DATA_WIDTH-1:0] rdata
);

    localparam DEPTH = (1 << ADDR_WIDTH);

    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];

`ifndef SYNTHESIS
    integer i;
    initial begin
        for (i = 0; i < DEPTH; i = i + 1) begin
            mem[i] = {DATA_WIDTH{1'b0}};
        end
    end
`endif

    // Synchronous write. RAM contents are intentionally not cleared on reset.
    always @(posedge clk) begin
        if (!rst_n) begin
            // No memory clear on reset.
        end else if (we) begin
            mem[addr] <= wdata;
        end
    end

    // Combinational read for first-version RAM subsystem.
    assign rdata = mem[addr];

endmodule

`default_nettype wire
