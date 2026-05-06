module data_mux (
    input   wire            data_sel,
    input   wire    [7:0]   registers,
    input   wire    [7:0]   immidiates,
    input   wire    [3:0]   accumulator,
    output  reg     [7:0]   data_out
);
    
endmodule