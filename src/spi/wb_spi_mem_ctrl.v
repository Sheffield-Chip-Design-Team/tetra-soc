// =======================================================================
// Module:      SPI Memory Controller
// Project:     Tetra-SoC, by SHaRC
// Description: Reads one byte from 23LC512-style SPI RAM.
//              Uses command 0x03 + 16-bit address.
// =======================================================================

module wb_spi_mem_ctrl #(
  parameter MAX_FETCH_BYTES = 256
)(
  // Clock and reset
  input  wire        clk,
  input  wire        rst_n,

  // Wishbone interface
  input  wire [4:0] wb_addr_i,
  input  wire [7:0] wb_wdata_i,
  input  wire       wb_we_i,
  input  wire       wb_stb_i,
  output reg  [7:0] wb_rdata_o,
  output wire       wb_ack_o,
  output wire       irq_o,

  // SPI signals
  output reg         cs_n,     // active-low chip select
  output reg         sck,      // SPI clock (mode 0)
  output reg         mosi,     // master-out
  input  wire        miso      // master-in
);

  localparam BYTE_COUNT_WIDTH = $clog2(MAX_FETCH_BYTES);

// --------------------------------------------------------------
// Internal signals 
// --------------------------------------------------------------

  // Control and status signals for the SPI controller core
  wire                        start_spi_fetch;      // pulse to start transaction 
  wire                        spi_fetch_done;       // pulse from core when byte_out is valid  
  wire                        seq_mode;             // 1 to keep reading sequentially after first byte

  reg                         spi_block_fetch_done; // set when the last byte in a block has been received, cleared by regs
  reg                         last;                 // asserted when this is the last byte to read in sequential mode
  
  wire                        busy;                 // set while transactions are in progress
  wire                        valid;                // 1 for one clk when data_out is valid
  wire [7:0]                  byte_out;             // received byte
  reg  [BYTE_COUNT_WIDTH-1:0] byte_count;           // number of bytes to fetch in sequential mode  
  reg  [BYTE_COUNT_WIDTH-1:0] next_byte_count;       // registered version of byte_count for edge detection
  reg  [15:0]                 ram_addr;             // address in external RAM

  reg [BYTE_COUNT_WIDTH-1:0]  max_byte_count;

  // Currently-unused IRQ enable/clear outputs from the regbank: keep connected for completeness,
  // but consume them in a no-op expression to satisfy strict lint.
  wire irq_byte_done_en_unused;
  wire irq_block_done_en_unused;
  wire irq_byte_done_clr_unused;
  wire irq_block_done_clr_unused;
  wire _irq_unused_consume = irq_byte_done_en_unused ^
                             irq_block_done_en_unused ^
                             irq_byte_done_clr_unused ^
                             irq_block_done_clr_unused;

// -------------------------------------------------------------
// Fetch Control Logic
// -------------------------------------------------------------

  // BUG sequential and non-sequential mode don't work as expected

  always @(*) begin
    next_byte_count = byte_count ^ {BYTE_COUNT_WIDTH{_irq_unused_consume & 1'b0}};
    if (spi_fetch_done) begin
      if (byte_count < max_byte_count) begin
        next_byte_count = byte_count + 1;
      end else begin
        next_byte_count = {BYTE_COUNT_WIDTH{1'b0}};
      end
    end
  end

  always @(posedge clk ) begin
     if (!rst_n) begin
        byte_count <= {BYTE_COUNT_WIDTH{1'b0}};
     end else begin
        byte_count <= next_byte_count;
     end
  end

  // Address and LAST signal control logic
  always @(posedge clk) begin
    if (!rst_n) begin
      ram_addr        <= 16'h0000;
      last            <= 1'b0;
    end else begin
      if (seq_mode) begin 
        if (spi_fetch_done) begin
          if (byte_count < max_byte_count-2) begin
            last        <= 1'b0;
          end else if (byte_count == max_byte_count-2) begin
            last        <= 1'b1;
          end else if (byte_count == max_byte_count-1) begin  
            last        <= 1'b0;
            ram_addr    <= ram_addr + {{16-BYTE_COUNT_WIDTH{1'b0}}, max_byte_count};
          end
        end
      end else begin // Not sequential mode, just single fetch
        if (start_spi_fetch) begin
          last        <= start_spi_fetch; //  the first is the last
          ram_addr    <= ram_addr + 1;
        end
      end
    end
  end

  assign spi_block_fetch_done = (byte_count == max_byte_count) && spi_fetch_done;

// -------------------------------------------------------------
// SPI memory controller register bank
// -------------------------------------------------------------

  wb_spi_mem_ctrl_regs u_wb_spi_mem_ctrl_regs (
    .clk                                  (clk),
    .rst_n                                (rst_n),
    // Wishbone interface
    .wb_addr_i                            (wb_addr_i),
    .wb_wdata_i                           (wb_wdata_i),
    .wb_we_i                              (wb_we_i),
    .wb_stb_i                             (wb_stb_i),
    .wb_rdata_o                           (wb_rdata_o),
    .wb_ack_o                             (wb_ack_o),
    .irq_o                                (irq_o),
    // Register bank interface
    // inputs
    .ext_f_SPI_STATUS_spi_busy_i          (busy),
    .ext_f_SPI_STATUS_spi_error_i         (1'b0),  // FiXME add some error reporting logic from the core
    .r_BYTES_FETCHED_i                    (byte_count),
    .ext_f_IRQ_STATUS_block_done_i        (spi_block_fetch_done),
    .ext_f_IRQ_STATUS_byte_done_i         (spi_fetch_done),
    // outputs
    .f_SPI_CTRL_fetch_mode_o              (seq_mode),
    .f_SPI_CTRL_start_pulse_o             (start_spi_fetch),
    .r_MAX_FETCH_SIZE_o                   (max_byte_count),
    .f_IRQ_ENABLE_byte_done_en_o          (irq_byte_done_en_unused),
    .f_IRQ_ENABLE_block_done_en_o         (irq_block_done_en_unused),
    .ext_f_IRQ_STATUS_byte_done_clr_o     (irq_byte_done_clr_unused),
    .ext_f_IRQ_STATUS_block_done_clr_o    (irq_block_done_clr_unused)
  );
// -------------------------------------------------------------
// SPI memory controller core
// -------------------------------------------------------------

  spi_mem_ctrl_core u_spi_mem_ctrl_core (
    .clk         (clk),
    .rst_n       (rst_n),
    // Control signals from regs
    .addr        (ram_addr),
    .start       (start_spi_fetch),
    .last        (last),
    // Control singals back to regs
    .busy        (busy),
    .valid       (spi_fetch_done),
    .data_out    (byte_out),
    // SPI Interface
    .cs_n        (cs_n),
    .sck         (sck),
    .mosi        (mosi),
    .miso        (miso)
  );

endmodule
