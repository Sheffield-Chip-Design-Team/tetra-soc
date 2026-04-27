module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/rtl/alu_wtb.fst");
    $dumpvars(0, alu_wtb);
end
endmodule
