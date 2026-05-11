### GUI Manager for Tetra Simulator
import PySimpleGUI as sg
from io_manager import *
from simulator import full_program_parsing, update_clock, single_cycle_execution

# Defines the GUI layout and event loop for the Tetra Simulator.
# Responsible for creating the main window, handling user interactions, and updating the display based on the simulation state.
# Uses PySimpleGUI.

def create_layout():
    """Return the main window layout for the simulator GUI."""
    left_column = [
        # PROGRAM INPUT FRAME
        [sg.Frame('PROGRAM INPUT', [
            [sg.Column([
                [sg.Multiline(size=(39, 18),key='program_input',enable_events=True,pad=(0, 0),font=('Courier New', 10))]
            ],vertical_alignment='top',pad=(0, 0))]
        ],pad=(5, 5))],

        [sg.Frame('CLOCK CONTROL', [            
            [sg.Text('Clock:'),
             sg.Text('LOW', key='clock_state', size=(6, 1), text_color='white', background_color='black'),
             sg.Text(' ' * 10),  # Spacer
             sg.Text('Cycle:', pad=((10, 0), 0)),
             sg.Text('0', key='cycle_count', size=(6, 1))],

            [sg.Text('Speed:'),
             sg.Slider(range=(1, 10), default_value=5, orientation='h', size=(18, 15), key='clock_speed', enable_events=True),
             sg.Text('5 Hz', key='clock_speed_label')],

            [sg.Button('Start', size=(10, 1), key='pause_clock'),
             sg.Button('Step',size=(10, 1), key='step_clock'),
             sg.Button('Reset', size=(10, 1), key='reset_clock')]

        ], pad=(5, 5), element_justification='left')],
        [sg.Button('Save', size=(11, 1)),
         sg.Button('Load', size=(10, 1)),
         sg.Button('Parse', size=(11, 1))]
    ]

    center_column = [ # Block diagram and register states
        
        [sg.Frame('BLOCK DIAGRAM', [[sg.Text('', size=(60, 18), background_color='white', pad=(0, 0))]], pad=(5, 5))],

        [sg.Frame('REGISTER LIST AND STATES', [
            [
                sg.Frame('REG_A', [[sg.Input(key='reg_a', size=(17, 1))]], pad=(2, 2)),
                sg.Frame('REG_B', [[sg.Input(key='reg_b', size=(17, 1))]], pad=(2, 2)),
                sg.Frame("ACCUM'", [[sg.Input(key='accum', size=(18, 1))]], pad=(2, 2))
            ],

            [sg.Frame('STATUS REG', [[sg.Input(key='status_reg', size=(58, 1))]], pad=(2, 2))],
            [sg.Frame('STATUS_REG STATE', [[sg.Input(key='status_reg_state', size=(58, 1))]], pad=(2, 2))]
            
        ], pad=(5, 5), element_justification='left')]
    ]

    right_column = [
        [sg.Frame('RAM LIST', [[sg.Multiline(size=(20, 32), key='ram_list', disabled=True)]], pad=(5, 5))]
    ]

    layout = [
        [
            sg.Column(left_column, vertical_alignment='top'),
            sg.Column(center_column, vertical_alignment='top'),
            sg.Column(right_column, vertical_alignment='top')
        ]
    ]

    return layout

def create_window():
    """Create and return the main PySimpleGUI window."""
    return sg.Window('Simulator', create_layout(), resizable=True, finalize=True)

def onScroll(window, pgml, gutter, *args):
    pgml.widget.yview(*args)
    gutter.yview(*args)
    update_line_numbers(window, gutter)

def update_registers(window, reg_a, reg_b, accum, status_reg, memory):
    """Update the register display in the GUI."""
    window['reg_a'].update(f"{reg_a:04b} ({reg_a})")
    window['reg_b'].update(f"{reg_b:04b} ({reg_b})")
    window['accum'].update(f"{accum:04b} ({accum})")
    window['status_reg'].update(' '.join(str(bit) for bit in status_reg))
    window['status_reg_state'].update(
        f"V:{status_reg[0]} C:{status_reg[1]} Z:{status_reg[2]} N:{status_reg[3]}"
    )

def run_event_loop():
    """Run the main event loop for the GUI."""
    window = create_window()
    clock_running = False
    clock_phase = False
    cycle_count = 0
    clock_speed = 5
    timeout = int(max(10, 1000 / clock_speed))
    
    next_address = 0
    next_inst = None
    reg_a = 0
    reg_b = 0
    accum = 0
    status_reg = [0, 0, 0, 0, 0, 0]
    memory = [0] * 1024
    
    parsed = False

    # Always update line numbers to stay in sync
    pgml = window['program_input']

    pgml.vsb.configure(command=lambda *args: onScroll(window, pgml, gutter, *args))
    pgml_parent = pgml.Widget.master

    gutter = sg.tk.Text(
        master=pgml_parent,
        width=4, height=1,
        background='lightgray',
        font=('Courier New', 10))
    
    gutter.pack(side='left', fill='y', before=pgml.Widget)
    
    window['clock_state'].update('LOW', background_color='black')
    window['clock_speed_label'].update(f'{clock_speed} Hz')
    window['cycle_count'].update(str(cycle_count))

    while True:
        event, values = window.read(timeout=timeout)

        if event == sg.WIN_CLOSED or event == 'Cancel':
            break

        if event == 'program_input':
            update_line_numbers(window, gutter)

        if event == sg.TIMEOUT_EVENT:
            if clock_running:
                clock_phase, cycle_count = update_clock(window, clock_phase, cycle_count)
                if clock_phase:  # Only update on rising edge
                    try:
                        next_address, reg_a, reg_b, accum, status_reg, memory = single_cycle_execution(window, next_inst, reg_a, reg_b, accum, status_reg, memory)
                        next_inst = next(row for row in resolved_program if row[0] == next_address)
                        update_registers(window, reg_a, reg_b, accum, status_reg, memory)
                    except Exception as e:
                        sg.popup_error(f"Error during execution: {e}")
            continue

        if event == 'pause_clock':
            if clock_running:
                clock_running = toggle_clock(window, clock_running)
            else:
                if not parsed:
                    sg.popup_error("Please parse the program before starting the clock.")
                else:
                    clock_running = toggle_clock(window, clock_running)
                    
        elif event == 'step_clock':
            if not clock_running:
                if parsed:
                    clock_phase, cycle_count = update_clock(window, clock_phase, cycle_count)
                    if clock_phase:  # Only execute on rising edge
                        try:
                            next_address, reg_a, reg_b, accum, status_reg, memory = single_cycle_execution(window, next_inst, reg_a, reg_b, accum, status_reg, memory)
                            next_inst = resolved_program[next_address] if next_address < len(resolved_program) else None
                            update_registers(window, reg_a, reg_b, accum, status_reg, memory)
                        except Exception as e:
                            sg.popup_error(f"Error during execution: {e}")
                else:
                    sg.popup_error("Please parse the program before stepping through the clock.")
                
        elif event == 'reset_clock':
            clock_running = False
            clock_phase = False
            cycle_count = 0
            next_address = 0
            reg_a = 0
            reg_b = 0
            accum = 0
            status_reg = [0, 0, 0, 0, 0]
            parsed = False
            resolved_program = None
            
            window['clock_state'].update('LOW', background_color='black')
            window['cycle_count'].update(str(cycle_count))
            window['pause_clock'].update('Start')
            window['program_input'].Disabled = False  # Re-enable editing on reset

        elif event == 'clock_speed':
            clock_speed = int(values['clock_speed'])
            timeout = int(max(10, 1000 / clock_speed))
            window['clock_speed_label'].update(f'{clock_speed} Hz')

        elif event == 'Save':
            save_program(pgml.get())
        elif event == 'Load':
            load_program(window)

        elif event == 'Parse':
            try:
                resolved_program = full_program_parsing(window)
                next_inst = resolved_program[0]
                sg.popup('Program parsed successfully!')
                parsed = True
                window['program_input'].Disabled = True  # Disable editing after parsing
            except Exception as e:
                sg.popup_error(f"Error during parsing: {e}")


    window.close()