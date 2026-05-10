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