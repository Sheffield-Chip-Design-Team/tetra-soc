// =======================================================================
// Module:      Block RAM
// Project:     Tetra-SoC, by SHaRC
// Description: Block RAM memory for instruction and data storage.
// =======================================================================

module wb_ram_ctrl #(
    parameter ADDR_WIDTH = 15,  // Adjust based on RAM size
    parameter DATA_WIDTH = 8
)(
    // Wishbone Signals
    input  wire [31:0]           wb_adr_i, // 32-bit from memory map
    input  wire [DATA_WIDTH-1:0] wb_dat_i,
    input  wire                  wb_we_i,
    input  wire                  wb_stb_i,
    input  wire                  wb_cyc_i,
    input  wire                  clk,
    input  wire                  rst,
    
    output wire [DATA_WIDTH-1:0] wb_dat_o,
    output reg                   wb_ack_o
);

    // Internal wires to SRAM
    wire [ADDR_WIDTH-1:0] sram_addr = wb_adr_i[ADDR_WIDTH-1:0];
    wire sram_we = wb_stb_i && wb_cyc_i && wb_we_i;

    // Instantiate Storage
    sram_1rw #(
        .ADDR_WIDTH(ADDR_WIDTH),
        .DATA_WIDTH(DATA_WIDTH)
    ) u_ram_storage (
        .clk  (clk),
        .addr (sram_addr),
        .din  (wb_dat_i),
        .we   (sram_we),
        .dout (wb_dat_o)
    );

    // Wishbone Ack Logic: Immediate response for zero-wait-state
    always @(posedge clk) begin
        if (rst) begin
            wb_ack_o <= 1'b0;
        end else begin
            // Ack is high when transaction is valid and not already acked
            wb_ack_o <= (wb_stb_i && wb_cyc_i && !wb_ack_o);
        end
    end

endmodule