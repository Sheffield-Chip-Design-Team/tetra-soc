from unittest import case
import PySimpleGUI as sg
from mnemonics import instruction_table

def get_inst_length(opcode):
    """Return the instruction length for a given opcode."""
    for name, operand_type, length in instruction_table:
        if name == opcode:
            return int(length)
    return 1  # Default to 1 if opcode not found

def parse_program_input(window):
    """Return a variable-row, 3-column array matching the GUI structure."""
    raw = window['program_input'].get()
    rows = []
    address = 0

    for line in raw.splitlines():
        # Split on whitespace.
        parts = line.split()

        label = ""
        opcode = ""
        operand = ""

        if not parts:
            continue  # Skip empty lines
        if parts and parts[0].endswith(':'):
            label = parts[0][:-1]  # Remove trailing ':'
            parts = parts[1:]     # Remove label from parts
        if parts:
            opcode = parts[0]
            operand = parts[1] if len(parts) > 1 else ""

        address_hex = f"{address:03X}"
        rows.append([address_hex, label, opcode, operand])  # Store address as int for easier processing

        address += get_inst_length(opcode)  # Increment address by instruction length

    return rows

def first_pass_label_parsing(program_rows):
    """Parse labels and return a dict of label -> address."""
    labels = {}
    for address, label, opcode, operand in program_rows:
        if label:  # If label column is not empty
            if label in labels:
                raise ValueError(f"Duplicate label: {label}")
            
            labels[label] = f"{address}"

    for name, addr in labels.items():  # Debug print to verify label parsing
        print(f"Label: {name} -> Address: {addr}")  # End debug print

    return labels

def second_pass_label_resolution(program_rows, labels):
    """
    Replace label operands with their corresponding addresses,
    and remove rows where label == 'reg' or label == 'imm'.
    """
    resolved = []

    for address, label, opcode, operand in program_rows:

        # Resolve label operands (e.g., $START)
        if operand in labels:
            operand = labels[operand]

        # Append the cleaned row
        resolved.append([address, label, opcode, operand])

    return resolved

def full_program_parsing(window):
    """Parse the program input and return a list of resolved instructions."""
    program_rows = parse_program_input(window)
    labels = first_pass_label_parsing(program_rows)
    resolved_program = second_pass_label_resolution(program_rows, labels)
    return resolved_program

def update_clock(window, clock_phase, cycle_count):
    """Advance the clock state and update the GUI."""
    clock_phase = not clock_phase
    state_text = 'HIGH' if clock_phase else 'LOW'
    bg_color = 'green' if clock_phase else 'black'
    window['clock_state'].update(state_text, background_color=bg_color)

    if clock_phase:
        cycle_count += 1
        window['cycle_count'].update(str(cycle_count))

    return clock_phase, cycle_count

def single_cycle_execution(window, current_instruction, reg_a, reg_b, accum, status_reg, memory):
    """Execute a single instruction and update the GUI."""
    # This function would contain the logic to execute one instruction based on the opcode and operand,
    # and then call update_register_display to refresh the GUI with the new register values.
    
    current_address = current_instruction[0]
    opcode = current_instruction[2]
    operand = current_instruction[3]

    next_address = int(current_address, 16) + get_inst_length(opcode)  # Default next address (for non-jump instructions)

    match opcode:
        case "NOP":
            pass  # No operation
        case "HALT":
            next_address = current_address  # HALT should not advance the program counter\
            pass  # Simulation will stop after this instruction, so no state changes needed
        case "ADD":
            accum = (reg_a + reg_b) & 0xF
            status_reg[0] = 1 if (reg_a & 0x8) == (reg_b & 0x8) and (accum & 0x8) != (reg_a & 0x8) else 0  # Carry flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "ADDI":
            accum = (reg_a + int(operand)) & 0xF
            status_reg[1] = 1 if (reg_a & 0x8) == (int(operand) & 0x8) and (accum & 0x8) != (reg_a & 0x8) else 0  # Overflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "ADDC":
            accum = (reg_a + reg_b + status_reg[1]) & 0xF
            status_reg[0] = 1 if (reg_a & 0x8) == (reg_b & 0x8) and (accum & 0x8) != (reg_a & 0x8) else 0  # Carry flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "ADCI":
            accum = (reg_a + int(operand) + status_reg[1]) & 0xF
            status_reg[1] = 1 if (reg_a & 0x8) == (int(operand) & 0x8) and (accum & 0x8) != (reg_a & 0x8) else 0  # Overflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "SUB":
            accum = (reg_a - reg_b) & 0xF
            status_reg[3] = 1 if (reg_a & 0x8) != (reg_b & 0x8) and (accum & 0x8) != (reg_a & 0x8) else 0  # Underflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "SUBI":
            accum = (reg_a - int(operand)) & 0xF
            status_reg[3] = 1 if (reg_a & 0x8) != (int(operand) & 0x8) and (accum & 0x8) != (reg_a & 0x8) else 0  # Underflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "SUBB":
            accum = (reg_a - reg_b - status_reg[1]) & 0xF
            status_reg[3] = 1 if (reg_a & 0x8) != (reg_b & 0x8) and (accum & 0x8) != (reg_a & 0x8) else 0  # Underflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "SUBBI":
            accum = (reg_a - int(operand) - status_reg[1]) & 0xF
            status_reg[3] = 1 if (reg_a & 0x8) != (int(operand) & 0x8) and (accum & 0x8) != (reg_a & 0x8) else 0  # Underflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "LSH":
            accum = (accum << 1) & 0xF
            status_reg[1] = 1 if (accum & 0x10) else 0  # Overflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "RSH":
            accum = (accum >> 1) & 0xF
            status_reg[3] = 1 if (accum & 0x1) else 0  # Underflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "ROL":
            old_msb = (accum & 0x8) >> 3
            accum = ((accum << 1) & 0xF) | (status_reg[1] & 1) # Rotate left through overflow
            status_reg[1] = old_msb  # Overflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "ROR":
            old_lsb = accum & 0x1
            accum = (accum >> 1) | ((status_reg[3] & 1) << 3) # Rotate right through underflow
            status_reg[1] = old_lsb  # Underflow flag
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "AND":
            accum = reg_a & reg_b
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "OR":
            accum = reg_a | reg_b
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "XOR":
            accum = reg_a ^ reg_b
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "NOT":
            accum = (~accum) & 0xF
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "INC":
            accum = (accum + 1) & 0xF
            status_reg[1] = 1 if accum == 0 else 0  # Overflow flag (only set if we wrap from 0xF to 0x0)
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "DEC":
            accum = (accum - 1) & 0xF
            status_reg[3] = 1 if accum == 0xF else 0  # Underflow flag (only set if we wrap from 0x0 to 0xF)
            status_reg[4] = 1 if accum == 0 else 0  # Zero flag
            status_reg[5] = 1 if accum & 0x8 else 0  # Sign flag
            pass
        case "CMP":
            status_reg[4] = 1 if reg_a == reg_b else 0  # Zero flag
            status_reg[5] = 1 if (reg_a < reg_b) & 0x8 else 0  # Sign flag
            pass
        case "CLF":
            status_reg[0] = 0 if operand[1] else status_reg[0]  # Clear carry flag
            status_reg[1] = 0 if operand[0] else status_reg[1]  # Clear overflow flag
            status_reg[2] = 0 if operand[1] else status_reg[2]  # Clear borrow flag
            status_reg[3] = 0 if operand[0] else status_reg[3]  # Clear underflow flag
            status_reg[4] = 0 if operand[2] else status_reg[4]  # Clear zero flag
            status_reg[5] = 0 if operand[3] else status_reg[5]  # Clear sign flag
            pass
        case "JMPX":
            next_address = current_address + int(operand, 16)  # Relative jump
            pass
        case "LDAI":
            reg_a = int(operand, 16) & 0xF
            pass
        case "LDBI":
            reg_b = int(operand, 16) & 0xF
            pass
        case "JMP":
            next_address = int(operand, 16)  # Absolute jump
            pass
        case "BRZ":
            if status_reg[4] == 0:
                next_address = int(operand, 16)
                pass
        case "BRN":
            if status_reg[5] == 1:  # Check if negative (sign bit set)
                next_address = int(operand, 16)
                pass
        case "BRC":
            if status_reg[0] == 1 or status_reg[2] == 1:  # Check carry / borrow flag
                next_address = int(operand, 16)
                pass
        case "BRV":
            if status_reg[1] == 1 or status_reg[3] == 1:  # Check overflow / underflow flag
                next_address = int(operand, 16)
                pass
        case "LHA":
            reg_a = memory[int(operand, 16)] & 0xF
            pass
        case "LLA":
            reg_a = (reg_a & 0xF0) | (memory[int(operand, 16)] & 0xF)
            pass    
        case "LHB":
            reg_a = (reg_a & 0x0F) | ((memory[int(operand, 16)] & 0xF) << 4)
            pass
        case "LLB":
            reg_b = (reg_b & 0xF0) | (memory[int(operand, 16)] & 0xF)
            pass
        case "SAB":
            memory[int(operand, 16)] = reg_a, reg_b
            pass
        case "STR":
            memory[int(operand, 16)] = accum
            pass
        
    return f"{next_address:03X}", reg_a, reg_b, accum, status_reg, memory

def update_register_display(window, reg_a, reg_b, accum, status_reg):
    """Update the register display fields in the GUI."""
    window['reg_a'].update(f'{reg_a:02X}')
    window['reg_b'].update(f'{reg_b:02X}')
    window['accum'].update(f'{accum:02X}')
    window['status_reg'].update(''.join(str(bit) for bit in status_reg))
    window['status_reg_state'].update(''.join(str(bit) for bit in status_reg))