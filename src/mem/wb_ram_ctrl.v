`default_nettype none

// =======================================================================
// Module:      wb_ram_ctrl
// Project:     Tetra-SoC, by SHaRC
// Description: Parameterisable 8-bit Wishbone RAM controller.
// =======================================================================
//
// Features:
// - Parameterisable data width and RAM address width
// - Separate Wishbone address width for out-of-range detection
// - Single-cycle read/write response
// - Basic burst-compatible interface using Wishbone CTI/BTE signals
// - Error response for accesses outside the configured RAM address space
//
// Notes:
// - Burst address sequencing is expected to be driven by the Wishbone master.
// - This slave responds to each valid in-range beat with ACK.
// - Out-of-range accesses assert ERR and do not write RAM.
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

    output wire                       wb_ack_o,
    output wire                       wb_err_o,

    // Debug / observation outputs
    output wire [RAM_ADDR_WIDTH-1:0]  ram_addr_o,
    output wire [DATA_WIDTH-1:0]      ram_rdata_o
);

    wire wb_valid;
    wire addr_in_range;
    wire ram_we;
    wire [DATA_WIDTH-1:0] ram_rdata;
    wire [RAM_ADDR_WIDTH-1:0] ram_addr;

    assign wb_valid = wb_cyc_i & wb_stb_i;

    // Address range check.
    // If the incoming Wishbone address is wider than the RAM address,
    // the upper bits must be zero. Otherwise, the access is out of range.
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

    // In-range access: ACK.
    // Out-of-range access: ERR.
    assign wb_ack_o = wb_valid & addr_in_range;
    assign wb_err_o = wb_valid & ~addr_in_range;

    // Write only during valid in-range Wishbone write cycles.
    assign ram_we = wb_valid & addr_in_range & wb_we_i;

    assign ram_addr_o  = ram_addr;
    assign ram_rdata_o = ram_rdata;

    // On valid writes, return the written value.
    // On reads, return RAM data.
    // On out-of-range access, return zero.
    assign wb_rdata_o = addr_in_range
                      ? (wb_we_i ? wb_wdata_i : ram_rdata)
                      : {DATA_WIDTH{1'b0}};

    // CTI/BTE are accepted for burst-compatible access.
    // The slave does not need to internally increment the address because
    // the Wishbone master supplies each beat address.
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
