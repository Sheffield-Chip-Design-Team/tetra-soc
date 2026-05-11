import PySimpleGUI as sg
from mnemonics import instruction_table

# Build a lookup dict: opcode -> operand type
OPCODE_MAP = {row[0]: row[1] for row in instruction_table}

def toggle_clock(window, clock_running):
    """Toggle the clock running state and update the button text."""
    clock_running = not clock_running
    window['pause_clock'].update('Resume' if not clock_running else 'Pause')
    return clock_running

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

def update_line_numbers(window, gutter):
    pgml = window['program_input']

    first = int(pgml.Widget.index("@0,0").split('.')[0])      # top visible line
    height = int(pgml.Widget['height'])                       # visible rows
    total = int(pgml.Widget.index('end-1c').split('.')[0])    # total lines
    last = min(first + height - 1, total)                     # bottom visible line

    line_numbers = "\n".join(str(i) for i in range(first, last + 1))

    gutter.config(state='normal')
    gutter.delete('1.0', 'end')
    gutter.insert('1.0', line_numbers)
    gutter.config(state='disabled')

def onScroll(window, pgml, gutter, *args):
    pgml.widget.yview(*args)
    gutter.yview(*args)
    update_line_numbers(window, gutter)
