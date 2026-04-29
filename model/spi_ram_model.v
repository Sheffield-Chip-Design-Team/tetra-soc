// spi_ram_model.v
// Simple behavioural SPI RAM model (READ 0x03 only).
// Mode 0: sample MOSI on rising edge, change MISO on falling edge.

`timescale 1ns/1ps

module spi_ram_model #(
    parameter MEM_BYTES = 256
)(
  input  wire cs_n,
  input  wire sck,
  input  wire mosi,
  output reg  miso
);
    // Internal memory
    reg [7:0] mem [0:MEM_BYTES-1];

    // Internal state
    localparam ST_CMD     = 2'd0;
    localparam ST_ADDR_HI = 2'd1;
    localparam ST_ADDR_LO = 2'd2;
    localparam ST_DATA    = 2'd3;

    reg [1:0]  state;
    reg [7:0]  in_shift;
    reg [2:0]  rx_cnt;       // 0..7 within a byte
    reg [7:0]  cmd;
    reg [15:0] addr;
    reg [7:0]  out_shift;
    reg [2:0]  tx_cnt;       // transmit bit counter 0..7

    function [15:0] next_addr;
        input [15:0] cur;
        begin
            if (cur == MEM_BYTES - 1) begin
                next_addr = 16'd0;
            end else begin
                next_addr = cur + 16'd1;
            end
        end
    endfunction

    // Receive command and address on rising edge of SCK; also reset on CS rising
    always @(posedge sck or posedge cs_n) begin
        if (cs_n) begin
            // end of transaction: reset internal state
            state    <= ST_CMD;
            in_shift <= 8'h00;
            rx_cnt   <= 3'd0;
            cmd      <= 8'h00;
            addr     <= 16'h0000;
            out_shift<= 8'h00;
            tx_cnt   <= 3'd0;
        end else begin
            // normal SCK-driven receive when CS is low
            in_shift <= {in_shift[6:0], mosi};
            rx_cnt   <= rx_cnt + 3'd1;

            if (rx_cnt == 3'd7) begin
                // Just received a full byte
                case (state)
                    ST_CMD: begin
                        cmd   <= {in_shift[6:0], mosi};
                        state <= ST_ADDR_HI;
                    end
                    ST_ADDR_HI: begin
                        addr[15:8] <= {in_shift[6:0], mosi};
                        state      <= ST_ADDR_LO;
                    end
                    ST_ADDR_LO: begin
                        addr[7:0]  <= {in_shift[6:0], mosi};
                        state      <= ST_DATA;
                        // Prepare the data byte to send (use full 16-bit address)
                        out_shift  <= mem[{addr[15:8], in_shift[6:0], mosi} % MEM_BYTES];
                        tx_cnt     <= 3'd0;
                    end
                    default: ; // ignore
                endcase
                rx_cnt <= 3'd0;
            end

            // Handle transmit shifting and byte progression in data phase
            if (state == ST_DATA && cmd == 8'h03) begin
                if (tx_cnt == 3'd7) begin
                    // Completed shifting previous byte on this posedge, prepare next byte
                    addr <= next_addr(addr);
                    out_shift <= mem[next_addr(addr) % MEM_BYTES];
                    tx_cnt <= 3'd0;
                end else begin
                    // shift out current byte (prepare next MISO value)
                    out_shift <= {out_shift[6:0], 1'b0};
                    tx_cnt <= tx_cnt + 3'd1;
                end
            end
        end
    end

    // Drive MISO on falling edge of SCK in data phase; also respond to CS rising
    always @(negedge sck or posedge cs_n) begin
        if (cs_n) begin
            // force MISO low when transaction ends
            miso <= 1'b0;
        end else begin
            if (state == ST_DATA && cmd == 8'h03) begin
                // Output MSB first (reflect MSB of out_shift prepared on previous posedge)
                miso <= out_shift[7];
            end else begin
                miso <= 1'b0;
            end
        end
    end

endmodule
