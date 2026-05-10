import PySimpleGUI as sg
from mnemonics import instruction_table


# Build a lookup dict: opcode -> operand type
OPCODE_MAP = {row[0]: row[1] for row in instruction_table}

def save_program(program_text):
    """Save the program text entered by the user to a file."""
    filename = sg.popup_get_file(
        'Save program as:',
        save_as=True,
        file_types=(('Text Files', '*.txt'), ('All Files', '*.*'))
    )

    if not filename:
        return

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(program_text)

    sg.popup('Program saved successfully!')

def load_program(window):
    """Load a program from a file and update the program input field."""
    filename = sg.popup_get_file(
        'Load program from:',
        file_types=(('Text Files', '*.txt'), ('All Files', '*.*'))
    )

    if not filename:
        return

    with open(filename, 'r', encoding='utf-8') as f:
        program_text = f.read()

    window['program_input'].update(program_text)
    sg.popup('Program loaded successfully!')

def parse_labels(lines):
    """Parse labels from the program lines according to the convention.
    
    Format:
        label.start
        <label_name> <type> <0x000>
        ...
        label.end
    
    Where <type> is:
        M -> memory address
        P -> program counter location
    """
    labels = {}
    label_types = {}  # Track if label is memory (M) or program counter (P)
    first_label_index = None
    last_label_index = None
    in_label_section = False
    labels_parsed_ok = True

    for i, line in enumerate(lines):

        if line == 'label.end':
            in_label_section = False
            continue
        
        if line == 'label.start':
            in_label_section = True
            continue

        if in_label_section:
            parts = line.split()
            if len(parts) != 3:
                labels_parsed_ok = False
                continue

            label_name = parts[0]
            label_type = parts[1]
            addr_str = parts[2]

            # Validate label type
            if label_type not in ('M', 'P'):
                labels_parsed_ok = False
                continue

            try:
                addr = int(addr_str, 16)
                labels[label_name] = addr
                label_types[label_name] = label_type
                if first_label_index is None:
                    first_label_index = i
                last_label_index = i
            except ValueError:
                labels_parsed_ok = False

    if in_label_section:
        labels_parsed_ok = False

    return {
        'labels': labels,
        'label_types': label_types,
        'first_label_index': first_label_index,
        'last_label_index': last_label_index,
        'parsed_ok': labels_parsed_ok
    }


def validate_syntax(lines, labels=None):
    """Validate the syntax of program lines outside label sections.
    
    Args:
        lines: List of program lines
        labels: Dict of label names to addresses (optional, for validating label operands)
    """
    if labels is None:
        labels = {}
    
    errors = []
    in_label_section = False
    for i, line in enumerate(lines, 1):
        if line == 'label.start':
            in_label_section = True
            continue
        if line == 'label.end':
            in_label_section = False
            continue
        if not in_label_section:
            parts = line.split()
            if not parts:
                errors.append(f"Line {i}: Empty line outside label section")
                continue

            opcode = parts[0]
            if opcode not in OPCODE_MAP:
                errors.append(f"Line {i}: Unknown opcode '{opcode}'")
                continue

            operand_type = OPCODE_MAP[opcode]
            operand_count = len(parts) - 1

            if operand_type == 'x':
                if operand_count > 0:
                    errors.append(f"Line {i}: Opcode '{opcode}' takes no operand, but got {operand_count}")
            elif operand_type == '#':
                if operand_count != 1:
                    errors.append(f"Line {i}: Opcode '{opcode}' requires immediate value, got {operand_count} operand(s)")
                elif not parts[1].startswith('#'):
                    errors.append(f"Line {i}: Immediate operand must start with '#', got '{parts[1]}'")
                else:
                    try:
                        int(parts[1][1:], 16)  # Validate hex after '#'
                    except ValueError:
                        errors.append(f"Line {i}: Invalid hex value '{parts[1][1:]}'")
            elif operand_type == '$':
                if operand_count != 1:
                    errors.append(f"Line {i}: Opcode '{opcode}' requires memory address, got {operand_count} operand(s)")
                elif not parts[1].startswith('$'):
                    errors.append(f"Line {i}: Memory address must start with '$', got '{parts[1]}'")
                else:
                    operand_value = parts[1][1:]  # Remove '$' prefix
                    # Try hex first, then check if it's a label
                    try:
                        int(operand_value, 16)  # Valid hex
                    except ValueError:
                        # Not hex, check if it's a valid label
                        if operand_value not in labels:
                            errors.append(f"Line {i}: '{operand_value}' is not a valid hex address or label")
    return errors


def simulate_program(program_text):
    """Simulate the program by parsing the input into an array of lines and extracting labels."""
    lines = program_text.strip().split('\n')
    # Strip whitespace from each line and remove empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    # Parse labels first
    label_data = parse_labels(lines)
    labels = label_data['labels']
    label_types = label_data['label_types']
    
    # Validate syntax with label references
    errors = validate_syntax(lines, labels)

    if errors:
        print("Syntax errors found:")
        for error in errors:
            print(error)
        return {
            'lines': lines,
            'labels': labels,
            'label_types': label_types,
            'errors': errors,
            'labels_parsed_ok': label_data['parsed_ok'],
            'first_label_index': label_data['first_label_index'],
            'last_label_index': label_data['last_label_index']
        }
    
    if not label_data['parsed_ok']:
        return {
            'lines': lines,
            'labels': labels,
            'label_types': label_types,
            'errors': ['Label parsing failed'],
            'labels_parsed_ok': False,
            'first_label_index': label_data['first_label_index'],
            'last_label_index': label_data['last_label_index']
        }
    
    print('Parsed program lines:', lines)
    print('Parsed labels:', labels)
    print('Label range:', label_data['first_label_index'], label_data['last_label_index'])
    return {
        'lines': lines,
        'labels': labels,
        'label_types': label_types,
        'first_label_index': label_data['first_label_index'],
        'last_label_index': label_data['last_label_index'],
        'labels_parsed_ok': label_data['parsed_ok'],
        'errors': []
    }