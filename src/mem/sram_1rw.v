`default_nettype none

// =======================================================================
// Module:      sram_1rw
// Project:     Tetra-SoC, by SHaRC
// Description: Simple parameterised single-port synchronous read/write RAM.
// =======================================================================
//
// Notes:
// - Synchronous write.
// - Synchronous read: rdata updates on the rising clock edge.
// - This better models a real SRAM/OpenRAM-style macro, where read data is
//   available after a clocked read access rather than combinationally.
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
    output reg  [DATA_WIDTH-1:0] rdata
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

    always @(posedge clk) begin
        if (!rst_n) begin
            rdata <= {DATA_WIDTH{1'b0}};
        end else begin
            if (we) begin
                mem[addr] <= wdata;
                rdata     <= wdata;  // write-first behaviour for simulation
            end else begin
                rdata     <= mem[addr];
            end
        end
    end

endmodule

`default_nettype wire
