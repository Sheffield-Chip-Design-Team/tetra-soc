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
