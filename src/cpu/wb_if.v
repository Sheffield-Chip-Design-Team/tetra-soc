// =======================================================================
// Module:      Tetra CPU top
// Project:     Tetra-SoC, by SHaRC
// Description: Sequential module implementing the control FSM for the CPU
//              fetch-decode-execute cycle.
// =======================================================================

module wb_if (
  input wire        clk,
  input wire        rst_n,

  // Wishbone master 
  output reg [15:0] addr_o,
  input wire [7:0] dat_i,
  input wire        ack_i,
  output reg [7:0]  dat_o,
  output reg        we_o,
  output reg        cyc_o,
  output reg        stb_o,
  output reg [2:0]  cti_o,
  output reg [1:0]  bte_o,

  // Control signals
  input wire [15:0] addr,
  input wire [7:0]  transfer_count,

  // Data Read Interface
  input wire        trigger_read,
  output reg [7:0]  read_data,
  output reg        read_data_valid,
  output reg        read_busy,
  output reg        read_done,

  // Data Write Interface
  input wire        trigger_write,
  input wire [7:0]  write_data,
  input wire        write_data_valid,
  output reg        write_busy,
  output reg        write_done
);

// --------------------------------------------------------------------
// Parameters
// --------------------------------------------------------------------
  
  // State encodings
  localparam [1:0] IDLE  = 2'b00;
  localparam [1:0] READ  = 2'b01;
  localparam [1:0] WRITE = 2'b10;
  localparam [1:0] DONE  = 2'b11;

  // Wishbone B3 burst encodings
  localparam [2:0] CTI_CLASSIC = 3'b000;
  localparam [2:0] CTI_INCR    = 3'b010;
  localparam [2:0] CTI_EOB     = 3'b111;
  localparam [1:0] BTE_LINEAR  = 2'b00;

// --------------------------------------------------------------------
// Internal Signals
// --------------------------------------------------------------------

  reg [1:0] state;
  reg [1:0] next_state;

  reg [15:0] next_addr_o;
  reg        next_cyc_o;
  reg        next_stb_o;
  reg [2:0]  next_cti_o;
  reg [1:0]  next_bte_o;
  reg  [7:0] next_dat_o;
  reg        next_we_o;

  reg  [7:0] bytes_left;
  reg  [7:0] next_bytes_left;

  reg  [7:0] next_read_data;
  reg        next_read_data_valid;
  reg        next_read_busy;
  reg        next_read_done;

  reg        wr_pending;
  reg        next_wr_pending;
  reg  [7:0] wr_data_lat;
  reg  [7:0] next_wr_data_lat;

//--------------------------------------------------------------------
// FSM
// --------------------------------------------------------------------
always @(*) begin
  // Defaults
  next_state            = state;
  next_addr_o           = addr_o;
  next_bytes_left       = bytes_left;

  next_cyc_o            = 1'b0;
  next_stb_o            = 1'b0;
  next_cti_o            = CTI_CLASSIC;
  next_bte_o            = BTE_LINEAR;
  next_dat_o            = dat_o;
  next_we_o             = 1'b0;

  next_read_data        = read_data;
  next_read_data_valid  = 1'b0;
  next_read_busy        = 1'b0;
  next_read_done        = 1'b0;

  next_wr_pending       = wr_pending;
  next_wr_data_lat      = wr_data_lat;
  write_busy            = 1'b0;
  write_done            = 1'b0;

  case (state)
    // =========================
    IDLE: begin
      if (trigger_read) begin
        next_addr_o     = addr;
        next_bytes_left = transfer_count;
        next_state      = (transfer_count == 0) ? DONE : READ;
      end 
      else if (trigger_write) begin
        next_addr_o     = addr;
        next_bytes_left = transfer_count; // reuse as write count
        next_state      = (transfer_count == 0) ? DONE : WRITE;
      end
    end

    // =========================
    READ: begin
      next_read_busy = 1'b1;

      next_cyc_o = 1'b1;
      next_stb_o = (bytes_left != 0);
      next_we_o  = 1'b0;

      next_cti_o = (bytes_left <= 1) ? CTI_EOB : CTI_INCR;

      if (ack_i && next_stb_o) begin
        next_read_data       = dat_i;
        next_read_data_valid = 1'b1;

        next_bytes_left = bytes_left - 1;
        next_addr_o     = addr_o + 1;

        if (bytes_left <= 1)
          next_state = DONE;
      end
    end

    // =========================
    WRITE: begin
      write_busy = 1'b1;

      next_cyc_o = 1'b1;
      next_we_o  = 1'b1;

      // Handshake for input data
      // write_data_ready_o = (bytes_left != 0) && !wr_pending;

      if (write_data_valid && !wr_pending && (bytes_left != 0)) begin
        next_wr_data_lat = write_data;
        next_wr_pending  = 1'b1;
      end

      next_dat_o = wr_data_lat;
      next_stb_o = wr_pending;

      next_cti_o = (bytes_left <= 1) ? CTI_EOB : CTI_INCR;

      if (ack_i && wr_pending) begin
        next_wr_pending  = 1'b0;

        next_bytes_left = bytes_left - 1;
        next_addr_o     = addr_o + 1;

        if (bytes_left <= 1)
          next_state = DONE;
      end
    end

    // =========================
    DONE: begin
      next_read_done  = (state == READ);
      write_done      = (state == WRITE);

      if (!trigger_read && !trigger_write)
        next_state = IDLE;
    end

    default: begin 
      next_state = IDLE;
      next_addr_o = 16'd0;
      next_bytes_left = 8'd0;
    end
  endcase
end

  always @(posedge clk) begin
    if (~rst_n) begin
      state <= IDLE;
      addr_o <= 17'd0;
      bytes_left <= 8'd0;

      we_o <= 1'b0;
      cyc_o <= 1'b0;
      stb_o <= 1'b0;
      cti_o <= CTI_CLASSIC;
      bte_o <= BTE_LINEAR;

      read_data <= 8'd0;
      read_data_valid <= 1'b0;
      read_busy <= 1'b0;
      read_done <= 1'b0;

      dat_o <= 8'd0;
      wr_pending <= 1'b0;
      wr_data_lat <= 8'd0;
      // write_data_ready_o <= 1'b0;
    
    end else begin
      state <= next_state;
      addr_o <= next_addr_o;
      bytes_left <= next_bytes_left;

      we_o <= next_we_o;
      cyc_o <= next_cyc_o;
      stb_o <= next_stb_o;
      cti_o <= next_cti_o;
      bte_o <= next_bte_o;

      read_data <= next_read_data;
      read_data_valid <= next_read_data_valid;
      read_busy <= next_read_busy;
      read_done <= next_read_done;

      dat_o <= next_dat_o;
      wr_pending <= next_wr_pending;
      wr_data_lat <= next_wr_data_lat;
    end
  end

endmodule