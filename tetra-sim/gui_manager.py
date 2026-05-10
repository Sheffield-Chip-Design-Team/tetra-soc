### GUI Manager for Tetra Simulator
import PySimpleGUI as sg
from io_manager import save_program, load_program, simulate_program

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

            [sg.Button('Pause', size=(10, 1), key='pause_clock'),
             sg.Button('Step',size=(10, 1), key='step_clock'),
             sg.Text('Cycle:', pad=((10, 0), 0)),
             sg.Text('0', key='cycle_count', size=(6, 1))]

        ], pad=(5, 5), element_justification='left')],
        [sg.Button('Save', size=(11, 1)),
         sg.Button('Load', size=(10, 1)),
         sg.Button('Simulate', size=(11, 1))]
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

def run_event_loop():
    """Run the main event loop for the GUI."""
    window = create_window()
    clock_running = False
    clock_phase = False
    cycle_count = 0
    clock_speed = 5
    timeout = int(max(10, 1000 / clock_speed))

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

        program_text = values['program_input']
        update_line_numbers(window, gutter)

        if event == 'program_input':
            update_line_numbers(window, gutter)

        if event == sg.TIMEOUT_EVENT:
            if clock_running:
                clock_phase = not clock_phase
                state_text = 'HIGH' if clock_phase else 'LOW'
                bg_color = 'green' if clock_phase else 'black'
                window['clock_state'].update(state_text, background_color=bg_color)
                if clock_phase:
                    cycle_count += 1
                    window['cycle_count'].update(str(cycle_count))
            continue

        if event == 'pause_clock':
            clock_running = not clock_running
            window['pause_clock'].update('Resume' if not clock_running else 'Pause')

        elif event == 'step_clock':
            if not clock_running:
                clock_phase = not clock_phase
                state_text = 'HIGH' if clock_phase else 'LOW'
                bg_color = 'green' if clock_phase else 'black'
                window['clock_state'].update(state_text, background_color=bg_color)
                if clock_phase:
                    cycle_count += 1
                    window['cycle_count'].update(str(cycle_count))

        elif event == 'clock_speed':
            clock_speed = int(values['clock_speed'])
            timeout = int(max(10, 1000 / clock_speed))
            window['clock_speed_label'].update(f'{clock_speed} Hz')

        elif event == 'Save':
            save_program(program_text)
        elif event == 'Load':
            load_program(window)

        elif event == 'Simulate':
            result = simulate_program(program_text)
            labels = result['labels']
            errors = result.get('errors', [])
            parsed_ok = result.get('labels_parsed_ok', False)

            if errors:
                window['ram_list'].update('')
                sg.popup_error('\n'.join(errors))
            elif not parsed_ok:
                window['ram_list'].update('')
                sg.popup_error('Label parsing failed.')
            else:
                ram_content = '\n'.join([f"{name}: 0x{addr:03X} = 0" for name, addr in labels.items()])
                window['ram_list'].update(ram_content)
                sg.popup('Simulation started successfully!')

    window.close()
