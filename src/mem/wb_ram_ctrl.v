`default_nettype none

// =======================================================================
// Module:      wb_ram_ctrl
// Project:     Tetra-SoC, by SHaRC
// Description: Minimal 8-bit Wishbone RAM controller.
// =======================================================================

module wb_ram_ctrl #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 8
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // 8-bit Wishbone peripheral interface
    input  wire [ADDR_WIDTH-1:0] wb_addr_i,
    input  wire [DATA_WIDTH-1:0] wb_wdata_i,
    output wire [DATA_WIDTH-1:0] wb_rdata_o,
    input  wire                  wb_we_i,
    input  wire                  wb_cyc_i,
    input  wire                  wb_stb_i,
    output wire                  wb_ack_o,

    // Debug / observation outputs
    output wire [ADDR_WIDTH-1:0] ram_addr_o,
    output wire [DATA_WIDTH-1:0] ram_rdata_o
);

    wire wb_valid;
    wire ram_we;
    wire [DATA_WIDTH-1:0] ram_rdata;

    assign wb_valid = wb_cyc_i & wb_stb_i;

    // First-version behaviour: immediate ACK for a valid bus access.
    assign wb_ack_o = wb_valid;

    // Write only during valid Wishbone write cycles.
    assign ram_we = wb_valid & wb_we_i;

    assign ram_addr_o  = wb_addr_i;
    assign ram_rdata_o = ram_rdata;

    // On writes, return the written value. On reads, return RAM data.
    assign wb_rdata_o = wb_we_i ? wb_wdata_i : ram_rdata;

    sram_1rw #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) u_sram_1rw (
        .clk   (clk),
        .rst_n (rst_n),
        .we    (ram_we),
        .addr  (wb_addr_i),
        .wdata (wb_wdata_i),
        .rdata (ram_rdata)
    );

endmodule

`default_nettype wire
