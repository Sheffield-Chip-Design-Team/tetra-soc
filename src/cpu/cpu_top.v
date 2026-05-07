// =======================================================================
// Module:      Tetra CPU top
// Project:     Tetra-SoC, by SHaRC
// Description: Sequential module implementing the control FSM for the CPU
//              fetch-decode-execute cycle.
// =======================================================================

module cpu_top (
  input wire        clk,
  input wire        rst_n,

  // debug interface 
  input wire        halt,
  input wire        resume,
  input wire        step,

  input wire [15:0] dbg_addr_in,
  input wire [7:0]  dbg_data_in,

  // wishbone master interface for connection to system bus
  output wire [15:0] wb_adr_o,
  input  wire [7:0]  wb_dat_i,
  output wire [7:0]  wb_dat_o,
  output wire        wb_we_o,
  output wire        wb_cyc_o,
  output wire        wb_stb_o,
  output wire [2:0]  wb_cti_o,
  output wire [1:0]  wb_bte_o,
  input  wire        wb_ack_i
);

  localparam S_IDLE  = 2'd0;
  localparam S_READ  = 2'd1;
  localparam S_WRITE = 2'd2;

  reg [1:0] cpu_state;

  // Control regs (temporary — will come from your CPU later)
  reg [15:0] addr_reg;
  reg [7:0]  transfer_count_reg;

  reg       trigger_read;
  reg       trigger_write;

  reg [7:0] write_data;
  reg       write_data_valid;

  // Status wires
  wire [7:0] read_data;
  wire       read_data_valid;
  wire       read_busy;
  wire       read_done;

  wire       write_busy;
  wire       write_done;

  wb_if u_wb_if (
    .clk                 (clk),
    .rst_n               (rst_n),
    // Wishbone master 
    .addr_o              (wb_adr_o),
    .dat_i               (wb_dat_i),
    .ack_i               (wb_ack_i),
    .dat_o               (wb_dat_o),
    .we_o                (wb_we_o),
    .cyc_o               (wb_cyc_o),
    .stb_o               (wb_stb_o),
    .cti_o               (wb_cti_o),
    .bte_o               (wb_bte_o),
    
    // Control signals
    .addr                (addr_reg),
    .transfer_count      (transfer_count_reg),

    // Data Read Interface
    .trigger_read        (trigger_read),
    .read_data           (read_data),
    .read_data_valid     (read_data_valid),
    .read_busy           (read_busy),
    .read_done           (read_done),

    // Data Write Interface
    .trigger_write       (trigger_write),
    .write_data          (write_data),
    .write_data_valid    (write_data_valid),
    .write_busy          (write_busy),
    .write_done          (write_done)
  );

  // -------------------- 

  // Dummy CPU FSM

  always @(posedge clk) begin
    if (!rst_n) begin
      cpu_state <= S_IDLE;

      trigger_read  <= 0;
      trigger_write <= 0;
      write_data_valid <= 0;

      addr_reg <= 0;
      transfer_count_reg <= 0;

    end else begin
      case (cpu_state)
        S_IDLE: begin
          addr_reg <= 16'h0000;
          transfer_count_reg <= 8'd4;
          trigger_read <= 1;
          cpu_state <= S_READ;
        end

        S_READ: begin
          trigger_read <= 0;
          if (read_done) begin
            addr_reg <= dbg_addr_in;
            transfer_count_reg <= 8'd4;
            trigger_write <= 1;
            cpu_state <= S_WRITE;
          end
        end

        S_WRITE: begin
          trigger_write <= 0;
          write_data_valid <= 1;
          write_data <= dbg_data_in;

          if (write_done) begin
            write_data_valid <= 0;
            cpu_state <= S_IDLE;
          end
        end
      endcase
    end
  end

endmodule