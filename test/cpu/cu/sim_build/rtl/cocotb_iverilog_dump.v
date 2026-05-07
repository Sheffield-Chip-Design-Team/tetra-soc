module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/rtl/control_unit_wtb.fst");
    $dumpvars(0, control_unit_wtb);
end
endmodule
