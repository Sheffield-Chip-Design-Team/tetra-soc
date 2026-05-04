`default_nettype none

module ram_tb;

    reg clk;
    reg rst_n;

    reg  [7:0] wb_addr_i;
    reg  [7:0] wb_wdata_i;
    wire [7:0] wb_rdata_o;
    reg        wb_we_i;
    reg        wb_cyc_i;
    reg        wb_stb_i;
    wire       wb_ack_o;

    wire [7:0] ram_addr_o;
    wire [7:0] ram_rdata_o;

    wb_ram_ctrl #(
        .DATA_WIDTH(8),
        .ADDR_WIDTH(8)
    ) dut (
        .clk         (clk),
        .rst_n       (rst_n),
        .wb_addr_i   (wb_addr_i),
        .wb_wdata_i  (wb_wdata_i),
        .wb_rdata_o  (wb_rdata_o),
        .wb_we_i     (wb_we_i),
        .wb_cyc_i    (wb_cyc_i),
        .wb_stb_i    (wb_stb_i),
        .wb_ack_o    (wb_ack_o),
        .ram_addr_o  (ram_addr_o),
        .ram_rdata_o (ram_rdata_o)
    );

    initial begin
        clk = 1'b0;
    end

endmodule

`default_nettype wire
