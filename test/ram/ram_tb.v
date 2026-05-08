`default_nettype none

module ram_tb;

    reg clk;
    reg rst_n;

    reg  [15:0] wb_addr_i;
    reg  [7:0]  wb_wdata_i;
    wire [7:0]  wb_rdata_o;
    reg         wb_we_i;
    reg         wb_cyc_i;
    reg         wb_stb_i;
    reg  [2:0]  wb_cti_i;
    reg  [1:0]  wb_bte_i;
    wire        wb_ack_o;
    wire        wb_err_o;

    wire        ram_we_o;
    wire [7:0]  ram_addr_o;
    wire [7:0]  ram_wdata_o;
    wire [7:0]  ram_rdata_i;

    wb_ram_ctrl #(
        .DATA_WIDTH(8),
        .RAM_ADDR_WIDTH(8),
        .WB_ADDR_WIDTH(16)
    ) dut (
        .clk         (clk),
        .rst_n       (rst_n),
        .wb_addr_i   (wb_addr_i),
        .wb_wdata_i  (wb_wdata_i),
        .wb_rdata_o  (wb_rdata_o),
        .wb_we_i     (wb_we_i),
        .wb_cyc_i    (wb_cyc_i),
        .wb_stb_i    (wb_stb_i),
        .wb_cti_i    (wb_cti_i),
        .wb_bte_i    (wb_bte_i),
        .wb_ack_o    (wb_ack_o),
        .wb_err_o    (wb_err_o),

        .ram_we_o    (ram_we_o),
        .ram_addr_o  (ram_addr_o),
        .ram_wdata_o (ram_wdata_o),
        .ram_rdata_i (ram_rdata_i)
    );

    sram_1rw #(
        .DATA_WIDTH(8),
        .ADDR_WIDTH(8)
    ) u_sram_1rw (
        .clk   (clk),
        .rst_n (rst_n),
        .we    (ram_we_o),
        .addr  (ram_addr_o),
        .wdata (ram_wdata_o),
        .rdata (ram_rdata_i)
    );

    initial begin
        clk = 1'b0;
    end

endmodule

`default_nettype wire
