/* wb_cpu8_to_wb32. Part of wb_intercon
 *
 * ISC License
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

`default_nettype none

// Bridge an 8-bit Wishbone master to a 32-bit Wishbone master interface.

// Notes/limits:
// - Supports a single outstanding transfer (classic Wishbone).
// - For pipelined/burst-capable masters, this bridge will stall by simply
//   not acknowledging until the outstanding transfer completes.

module wb8_to_wb32 #(
   parameter AW = 32,
   parameter endian = "little")
(
   input  wire             wb_clk_i,
   input  wire             wb_rst_i,

   input  wire [AW-1:0]    wbs_adr_i,
   // 8-bit Wishbone slave
   input  wire [7:0]       wbs_dat_i,
   input  wire             wbs_we_i,
   input  wire             wbs_cyc_i,
   input  wire             wbs_stb_i,
   input  wire [2:0]       wbs_cti_i,
   input  wire [1:0]       wbs_bte_i,
   output wire [7:0]       wbs_dat_o,
   output wire             wbs_ack_o,
   output wire             wbs_err_o,
   output wire             wbs_rty_o,

   // 32-bit Wishbone master (downstream to intercon)
   output wire [AW-1:0]    wbm_adr_o,
   output wire [31:0]      wbm_dat_o,
   output wire [3:0]       wbm_sel_o,
   output wire             wbm_we_o,
   output wire             wbm_cyc_o,
   output wire             wbm_stb_o,
   output wire [2:0]       wbm_cti_o,
   output wire [1:0]       wbm_bte_o,
   input  wire [31:0]      wbm_dat_i,
   input  wire             wbm_ack_i,
   input  wire             wbm_err_i,
   input  wire             wbm_rty_i
);

   reg        pending;
   reg [AW-1:0] r_adr;
   reg [7:0]  r_dat;
   reg        r_we;
   reg [2:0]  r_cti;
   reg [1:0]  r_bte;
   reg [1:0]  r_lane;

   wire req = wbs_cyc_i & wbs_stb_i;

   wire [1:0] lane_now = (endian == "little") ? wbs_adr_i[1:0]
                                               : (2'd3 - wbs_adr_i[1:0]);

   // Accept a new request only when no outstanding request exists.
   always @(posedge wb_clk_i) begin
      if (wb_rst_i) begin
         pending <= 1'b0;
      end else begin
         if (!pending && req) begin
            pending <= 1'b1;
            r_adr   <= wbs_adr_i;
            r_dat   <= wbs_dat_i;
            r_we    <= wbs_we_i;
            r_cti   <= wbs_cti_i;
            r_bte   <= wbs_bte_i;
            r_lane  <= lane_now;
         end

         if (pending && (wbm_ack_i | wbm_err_i | wbm_rty_i)) begin
            pending <= 1'b0;
         end
      end
   end

   // Drive downstream Wishbone from the latched request.
   assign wbm_adr_o = r_adr;
   assign wbm_we_o  = r_we;
   assign wbm_cti_o = r_cti;
   assign wbm_bte_o = r_bte;

   assign wbm_sel_o = (4'b0001 << r_lane);
   assign wbm_dat_o = ({24'b0, r_dat} << (8*r_lane));

   // Keep CYC/STB asserted while pending, so downstream can insert wait states.
   assign wbm_cyc_o = pending;
   assign wbm_stb_o = pending;

   // Return response to CPU side.
   assign wbs_ack_o = pending & wbm_ack_i;
   assign wbs_err_o = pending & wbm_err_i;
   assign wbs_rty_o = pending & wbm_rty_i;

   wire [7:0] dat_lane = (wbm_dat_i >> (8*r_lane));
   assign wbs_dat_o = dat_lane;

endmodule
