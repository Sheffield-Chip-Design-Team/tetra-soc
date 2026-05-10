# Tetra CPU Instruction Mnemonics
# Array containing all operation mnemonics for the Tetra CPU
#
# Format: [[mnemonic, operand_type, instruction_length]]
# operand_type is:
#   x -> no extra input
#   # -> immediate value
#   $ -> memory address

instruction_table = [
    ["NOP",     "x", "1"],
    ["HALT",    "x", "1"],
    ["ADD",     "x", "1"],
    ["ADDC",    "x", "1"],
    ["SUB",     "x", "1"],
    ["SUBB",    "x", "1"],
    ["ADDI",    "#", "2"],
    ["ADCI",    "#", "2"],
    ["SUBI",    "#", "2"],
    ["SUBBI",   "#", "2"],
    ["LSH",     "x", "1"],
    ["ROL",     "x", "1"],
    ["RSH",     "x", "1"],
    ["ROR",     "x", "1"],
    ["AND",     "x", "1"],
    ["OR",      "x", "1"],
    ["XOR",     "x", "1"],
    ["NOT",     "x", "1"],
    ["INC",     "x", "1"],
    ["DEC",     "x", "1"],
    ["CMP",     "x", "1"],
    ["CLF",     "x", "1"],
    ["LDAI",    "#", "2"],
    ["LDBI",    "#", "2"],
    ["LDA",     "$", "2"],
    ["JMPX",    "$", "2"],
    ["JMP",     "$", "2"],
    ["BRZ",     "$", "2"],
    ["BRN",     "$", "2"],
    ["BRC",     "$", "2"],
    ["BRV",     "$", "2"],
    ["LHA",     "$", "2"],
    ["LLA",     "$", "2"],
    ["LHB",     "$", "2"],
    ["LLB",     "$", "2"],
    ["SAB",     "$", "2"],
    ["STR",     "$", "2"]
]