`default_nettype none
`timescale 1ns / 1ps

module spi_tb ();
  reg        clk;
  reg        rst_n;

  reg [4:0]  wb_addr_i;
  reg  [7:0] wb_wdata_i;
  reg        wb_we_i;
  reg        wb_stb_i;
  wire       wb_ack_o;
  wire [7:0] wb_rdata_o;
  wire       irq_o;

  wire       cs_n;
  wire       sck;
  wire       mosi;
  wire       miso;

  // Behavioural SPI RAM model (READ 0x03 only)
  spi_ram_model #(.MEM_BYTES(256)) ram (
      .cs_n (cs_n),
      .sck  (sck),
      .mosi (mosi),
      .miso (miso)
  );

  // SPI memory controller under test
  wb_spi_mem_ctrl #(
     .MAX_FETCH_BYTES   (256)
  ) u_wb_spi_mem_ctrl (
    // Clock and reset
    .clk                (clk),
    .rst_n              (rst_n),
    // Wishbone interface
    .wb_addr_i          (wb_addr_i),
    .wb_wdata_i         (wb_wdata_i),
    .wb_we_i            (wb_we_i),
    .wb_stb_i           (wb_stb_i),
    .wb_rdata_o         (wb_rdata_o),
    .wb_ack_o           (wb_ack_o),
    .irq_o              (irq_o),
    // SPI signals
    .cs_n               (cs_n),
    .sck                (sck),
    .mosi               (mosi),
    .miso               (miso)
  );

  always #10 clk = ~clk; // TODO move this to cocotb land
 
   initial begin
      // load dummy data into the SPI RAM (READ 0x03 only)
      ram.mem[8'h00] = 8'b0000_1010; // Nibble 0
      ram.mem[8'h01] = 8'b0000_0010; // Nibble 1
      ram.mem[8'h02] = 8'b0000_0011; // Nibble 2
      ram.mem[8'h03] = 8'b0000_0100; // Nibble 3
      ram.mem[8'h04] = 8'b0000_0101; // Nibble 4
      ram.mem[8'h05] = 8'b0000_0110; // Nibble 5
      ram.mem[8'h06] = 8'b0000_0111; // Nibble 6
      ram.mem[8'h07] = 8'b0000_1000; // Nibble 7
      ram.mem[8'h08] = 8'b0000_1001; // Nibble 8
      ram.mem[8'h09] = 8'b0000_1010; // Nibble 9
      ram.mem[8'h0A] = 8'b0000_1011; // Nibble A
      ram.mem[8'h0B] = 8'b0000_1100; // Nibble B
      ram.mem[8'h0C] = 8'b0000_1101; // Nibble C
      ram.mem[8'h0D] = 8'b0000_1110; // Nibble D
      ram.mem[8'h0E] = 8'b0000_1111; // Nibble E
      ram.mem[8'h0F] = 8'b0000_0000; // Nibble F
      for (int i = 16; i < 256; i=i+1) begin
          ram.mem[i] = 8'b1111_1111; // CLR, CLR
      end
  end

  // Dump the signals to an FST file (CI expects tb.fst)
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, spi_tb);
    #1;
  end

endmodule
