`timescale 1ns/1ps

module mem_tb #(
    parameter ADDR_WIDTH = 15,
    parameter DATA_WIDTH = 8
)(
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] wb_adr_i,
    input  wire [7:0]  wb_dat_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output wire [7:0]  wb_dat_o,
    output wire        wb_ack_o
);

    // Instantiate RAM Controller
    wb_ram_ctrl #(
        .ADDR_WIDTH(ADDR_WIDTH),
        .DATA_WIDTH(DATA_WIDTH)
    ) dut (
        .clk      (clk),
        .rst      (~rst_n), // RAM ctrl uses active-high reset
        .wb_adr_i (wb_adr_i),
        .wb_dat_i (wb_dat_i),
        .wb_we_i  (wb_we_i),
        .wb_stb_i (wb_stb_i),
        .wb_cyc_i (wb_cyc_i),
        .wb_dat_o (wb_dat_o),
        .wb_ack_o (wb_ack_o)
    );

    // VCD Dump
    initial begin
        $dumpfile("mem_tb.vcd");
        $dumpvars(0, mem_tb);
    end

endmodule
