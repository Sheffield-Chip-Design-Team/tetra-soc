`default_nettype none

// =======================================================================
// Module:      wb_ram_ctrl
// Project:     Tetra-SoC, by SHaRC
// Description: Parameterisable Wishbone RAM controller with synchronous read.
// =======================================================================
//
// Features:
// - Parameterisable data width and RAM address width.
// - Separate Wishbone address width for out-of-range detection.
// - Registered ACK/ERR response.
// - Supports clocked/synchronous RAM read behaviour.
// - Basic burst-compatible interface using Wishbone CTI/BTE signals.
// - Error response for accesses outside the configured RAM address space.
//
// Timing:
// - A valid in-range request is accepted on a clock edge.
// - ACK is asserted on the following cycle.
// - For reads, wb_rdata_o is valid when ACK is asserted.
// - For writes, the RAM write occurs on the request clock edge and ACK is
//   returned on the following cycle.
// =======================================================================

module wb_ram_ctrl #(
    parameter DATA_WIDTH     = 8,
    parameter RAM_ADDR_WIDTH = 8,
    parameter WB_ADDR_WIDTH  = 16
)(
    input  wire                       clk,
    input  wire                       rst_n,

    // Wishbone peripheral interface
    input  wire [WB_ADDR_WIDTH-1:0]   wb_addr_i,
    input  wire [DATA_WIDTH-1:0]      wb_wdata_i,
    output wire [DATA_WIDTH-1:0]      wb_rdata_o,
    input  wire                       wb_we_i,
    input  wire                       wb_cyc_i,
    input  wire                       wb_stb_i,

    // Wishbone burst cycle signals
    input  wire [2:0]                 wb_cti_i,
    input  wire [1:0]                 wb_bte_i,

    output reg                        wb_ack_o,
    output reg                        wb_err_o,

    // Debug / observation outputs
    output wire [RAM_ADDR_WIDTH-1:0]  ram_addr_o,
    output wire [DATA_WIDTH-1:0]      ram_rdata_o
);

    wire wb_request;
    wire addr_in_range;
    wire ram_we;
    wire [RAM_ADDR_WIDTH-1:0] ram_addr;
    wire [DATA_WIDTH-1:0] ram_rdata;

    reg response_is_write;
    reg [DATA_WIDTH-1:0] response_wdata;

    assign wb_request = wb_cyc_i & wb_stb_i;

    generate
        if (WB_ADDR_WIDTH > RAM_ADDR_WIDTH) begin : gen_addr_range_check
            assign addr_in_range =
                wb_addr_i[WB_ADDR_WIDTH-1:RAM_ADDR_WIDTH] ==
                {(WB_ADDR_WIDTH-RAM_ADDR_WIDTH){1'b0}};
        end else begin : gen_no_addr_range_check
            assign addr_in_range = 1'b1;
        end
    endgenerate

    assign ram_addr = wb_addr_i[RAM_ADDR_WIDTH-1:0];

    // Write on the request clock edge for valid in-range writes.
    assign ram_we = wb_request & addr_in_range & wb_we_i;

    assign ram_addr_o  = ram_addr;
    assign ram_rdata_o = ram_rdata;

    // Registered response. ACK/ERR are delayed by one clock cycle.
    always @(posedge clk) begin
        if (!rst_n) begin
            wb_ack_o          <= 1'b0;
            wb_err_o          <= 1'b0;
            response_is_write <= 1'b0;
            response_wdata    <= {DATA_WIDTH{1'b0}};
        end else begin
            wb_ack_o          <= wb_request & addr_in_range;
            wb_err_o          <= wb_request & ~addr_in_range;
            response_is_write <= wb_request & addr_in_range & wb_we_i;
            response_wdata    <= wb_wdata_i;
        end
    end

    // For reads, ram_rdata is valid when wb_ack_o is asserted.
    // For writes, return the written value for visibility in simulation.
    // For out-of-range accesses, return zero.
    assign wb_rdata_o = wb_err_o
                      ? {DATA_WIDTH{1'b0}}
                      : (response_is_write ? response_wdata : ram_rdata);

    // CTI/BTE are accepted for burst-compatible access.
    // The master supplies each beat address. This controller returns one
    // registered response per valid request beat.
    wire [2:0] unused_cti;
    wire [1:0] unused_bte;
    assign unused_cti = wb_cti_i;
    assign unused_bte = wb_bte_i;

    sram_1rw #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(RAM_ADDR_WIDTH)
    ) u_sram_1rw (
        .clk   (clk),
        .rst_n (rst_n),
        .we    (ram_we),
        .addr  (ram_addr),
        .wdata (wb_wdata_i),
        .rdata (ram_rdata)
    );

endmodule

`default_nettype wire
