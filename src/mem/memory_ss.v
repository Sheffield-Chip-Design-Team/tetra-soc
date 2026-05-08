`default_nettype none

// =======================================================================
// Module:      memory_ss
// Project:     Tetra-SoC, by SHaRC
// Description: Memory subsystem wrapping the RAM controller and RAM model.
// =======================================================================
//
// This module keeps the RAM controller independent from the actual RAM
// implementation. The simulation RAM can later be swapped for an OpenRAM
// macro without changing wb_ram_ctrl.
// =======================================================================

module memory_ss #(
    parameter DATA_WIDTH     = 8,
    parameter RAM_ADDR_WIDTH = 12,
    parameter WB_ADDR_WIDTH  = 32
)(
    input  wire                       clk,
    input  wire                       rst_n,

    // Wishbone slave interface from interconnect
    input  wire [WB_ADDR_WIDTH-1:0]   wb_adr_i,
    input  wire [DATA_WIDTH-1:0]      wb_dat_i,
    input  wire [3:0]                 wb_sel_i,
    input  wire                       wb_we_i,
    input  wire                       wb_cyc_i,
    input  wire                       wb_stb_i,
    input  wire [2:0]                 wb_cti_i,
    input  wire [1:0]                 wb_bte_i,

    output wire [DATA_WIDTH-1:0]      wb_rdt_o,
    output wire                       wb_ack_o,
    output wire                       wb_err_o,
    output wire                       wb_rty_o
);

    wire                       ram_we;
    wire [RAM_ADDR_WIDTH-1:0]  ram_addr;
    wire [DATA_WIDTH-1:0]      ram_wdata;
    wire [DATA_WIDTH-1:0]      ram_rdata;

    // The interconnect has already decoded this transaction into the RAM
    // region, so the local RAM address is taken from the low address bits.
    wire [RAM_ADDR_WIDTH-1:0] local_wb_addr;
    assign local_wb_addr = wb_adr_i[RAM_ADDR_WIDTH-1:0];

    wb_ram_ctrl #(
        .DATA_WIDTH(DATA_WIDTH),
        .RAM_ADDR_WIDTH(RAM_ADDR_WIDTH),
        .WB_ADDR_WIDTH(RAM_ADDR_WIDTH)
    ) u_wb_ram_ctrl (
        .clk         (clk),
        .rst_n       (rst_n),

        .wb_addr_i   (local_wb_addr),
        .wb_wdata_i  (wb_dat_i),
        .wb_rdata_o  (wb_rdt_o),
        .wb_we_i     (wb_we_i),
        .wb_cyc_i    (wb_cyc_i),
        .wb_stb_i    (wb_stb_i),
        .wb_cti_i    (wb_cti_i),
        .wb_bte_i    (wb_bte_i),
        .wb_ack_o    (wb_ack_o),
        .wb_err_o    (wb_err_o),

        .ram_we_o    (ram_we),
        .ram_addr_o  (ram_addr),
        .ram_wdata_o (ram_wdata),
        .ram_rdata_i (ram_rdata)
    );

    sram_1rw #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(RAM_ADDR_WIDTH)
    ) u_sram_1rw (
        .clk   (clk),
        .rst_n (rst_n),
        .we    (ram_we),
        .addr  (ram_addr),
        .wdata (ram_wdata),
        .rdata (ram_rdata)
    );

    assign wb_rty_o = 1'b0;

    // Currently unused by this 8-bit RAM model.
    wire unused_wb_sel;
    assign unused_wb_sel = &{1'b0, wb_sel_i};

endmodule

`default_nettype wire
