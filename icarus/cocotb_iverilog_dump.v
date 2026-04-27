module cocotb_iverilog_dump();
initial begin
    string dumpfile_path;    if ($value$plusargs("dumpfile_path=%s", dumpfile_path)) begin
        $dumpfile(dumpfile_path);
    end else begin
        $dumpfile("/home/aaiva132/git-repos/tetra-soc/icarus/_wtb.fst");
    end
    $dumpvars(0, _wtb);
end
endmodule
