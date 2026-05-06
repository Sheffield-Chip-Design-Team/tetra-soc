// =======================================================================
// Module:      Single-Port RAM
// Project:     Tetra-SoC, by SHaRC
// Description: Single-port read/write SRAM for general data storage.
// =======================================================================

module sram_1rw #(
    parameter ADDR_WIDTH = 15,
    parameter DATA_WIDTH = 8
)(
    input  wire                   clk,
    input  wire [ADDR_WIDTH-1:0]  addr,
    input  wire [DATA_WIDTH-1:0]  din,
    input  wire                   we,
    output wire [DATA_WIDTH-1:0]  dout
);
    // 256-byte memory array
    reg [DATA_WIDTH-1:0] ram [0:(2**ADDR_WIDTH)-1];

    // Synchronous Write
    always @(posedge clk) begin
        if (we) begin
            ram[addr] <= din;
        end
    end

    // Asynchronous Read (Important for single-cycle CPU execution)
    assign dout = ram[addr];

endmodule