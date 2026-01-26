import time
from psychopy import gui, core, visual, monitors
from enums import SessionType
from mackworth_clock import MackworthClock
from prompt import RSEO_TEXT, RSEC_TEXT, paradigm_TEXT, exp_info
from questionnaire import run_kss_gui, run_vas_f, run_nasa_tlx, run_desq
import csv
import ctypes
from ctypes import wintypes
from screen import get_screens_info, launch_visualstimuli_on_screen

user32 = ctypes.windll.user32

task_screen_index = 0 # corresponding to the index in   Setting

screens = get_screens_info()

print(screens)

task_monitor = screens[task_screen_index]

def get_session_type_dialog() -> SessionType:
    session_types = [session_type.value for session_type in list(SessionType)]
    info = {'Session type': session_types}
    dlg = gui.DlgFromDict(info, title='Please choose a session type: ')
    if dlg.OK:
        selected_session = SessionType(info['Session type'])
        return selected_session
    else:
        core.quit()

def mackworth_parameters() -> dict:
    mackworth_param = {
        'Clock radius (pixels)': 400,
        'White dot size': 2,
        'Red dot size': 4,
        'Clock Steps': 96,
        'Jump interval (ms)': 800,
        'Warmup_steps': 4,
        'Response time (ms)': 3000,
        'Minimum gap between target events (step)': 8,
        'Series number': 18,
        'Steps per series': 180,
        'Target trial rate': 0.04,
        'Distance To Monitor (cm)': 80,
    }

    dlg = gui.DlgFromDict(mackworth_param, title='Mackworth parameters: ')
    if dlg.OK:
        return mackworth_param
    else:
        core.quit()


def main():
    mackworth_param = mackworth_parameters()
    session_type = get_session_type_dialog()

    mon = monitors.Monitor('winMon')
    mon.setDistance(mackworth_param['Distance To Monitor (cm)'])
    mon.setSizePix((task_monitor['width'], task_monitor['height']))

    if session_type == SessionType.FORMAL:
        subject_info = {
            'subject_id': '',
            'session': ['flicker', 'no_flicker'],
            'age': '',
            'gender': ['male', 'female', 'other']
        }
        dlg = gui.DlgFromDict(subject_info, title='Mackworth + EEG')
        if dlg.OK:
            #questionnaire
            #run_kss_gui(subject_info['subject_id'], 'KSS – Pre-Task')
            #run_desq(subject_info['subject_id'], 'DESQ - Pre-Task')

            win = visual.Window(
                fullscr=False,
                monitor=mon,
                size=(task_monitor['width'],task_monitor['height']),
                waitBlanking=True,
                color=130,
                colorSpace='rgb255',
                units='pix',
                allowGUI=False,
                screen=task_screen_index,
            )
            #run_vas_f(win, subject_info['subject_id'], 'VAS-F - Pre-Task')

            # save info
            mackworth_clock = MackworthClock(
                win,
                radius=mackworth_param['Clock radius (pixels)'],
                white_dot_size=mackworth_param['White dot size'],
                red_dot_size=mackworth_param['Red dot size'],
                steps=mackworth_param['Clock Steps'],
                step_interval=mackworth_param['Jump interval (ms)'],
                warmup_steps=mackworth_param['Warmup_steps'],
                response_time=mackworth_param['Response time (ms)'],
                minimun_target_gap=mackworth_param['Minimum gap between target events (step)'],
                series_num=mackworth_param['Series number'],
                steps_per_series=mackworth_param['Steps per series'],
                target_rate=mackworth_param['Target trial rate'],
            )

            event_stream = []
            global_clock = core.Clock()
            process = None
            mackworth_clock.show_instructions(RSEO_TEXT)
            mackworth_clock.resting_state(event_stream, global_clock)
            mackworth_clock.show_instructions(RSEC_TEXT)
            mackworth_clock.resting_state(event_stream, global_clock, eyes_open=False)

            if subject_info['session'] == 'flicker':
                process = launch_visualstimuli_on_screen(r".\VisualStimuli.exe", screen_index=task_screen_index, paradigm_winHandle=win.winHandle)
            mackworth_clock.show_instructions(paradigm_TEXT)

            mackworth_clock.instantiate(event_stream, global_clock)
            if process:
                process.terminate()
            mackworth_clock.show_instructions(RSEO_TEXT)
            mackworth_clock.resting_state(event_stream, global_clock, eyes_open=True)
            mackworth_clock.show_instructions(RSEC_TEXT)
            mackworth_clock.resting_state(event_stream, global_clock, eyes_open=False)
            keys = event_stream[0].keys()

            event_file_name = f"subject_{subject_info['subject_id']}_gender_{subject_info['gender']}_session_{subject_info['session']}.csv"

            with open(event_file_name, "w", newline="", encoding="utf-8") as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(event_stream)

            print(f"the event streaming has been written into {event_file_name}")

            # post questionnaire
            #run_kss_gui(subject_info['subject_id'], 'KSS – Post-Task')
            #todo

            # only after Task
            #run_nasa_tlx(win, subject_info['subject_id'], 'NASA - TLX - Pre-Task')

            # end of exprienment
        else:
            core.quit()
    elif session_type == SessionType.PRACTICE:
        win = visual.Window(
            fullscr=False,
            monitor=mon,
            size=(task_monitor['width'],task_monitor['height']),
            waitBlanking=True,
            color=130,
            colorSpace='rgb255',
            units='pix',
            allowGUI=False,
            screen=task_screen_index,
        )
        #win.winHandle.lower()
        #win.winHandle._window.set_always_on_top(False)
        event_stream = []
        global_clock = core.Clock()
        mackworth_clock = MackworthClock(
            win,
            radius=mackworth_param['Clock radius (pixels)'],
            white_dot_size=mackworth_param['White dot size'],
            red_dot_size=mackworth_param['Red dot size'],
            steps=mackworth_param['Clock Steps'],
            step_interval=mackworth_param['Jump interval (ms)'],
            warmup_steps=mackworth_param['Warmup_steps'],
            response_time=mackworth_param['Response time (ms)'],
            minimun_target_gap=mackworth_param['Minimum gap between target events (step)'],
            series_num=1,
            steps_per_series=mackworth_param['Steps per series'],
            target_rate=mackworth_param['Target trial rate'],
        )
        event_stream = mackworth_clock.instantiate(event_stream, global_clock)
        print(event_stream)
if __name__ == "__main__":
    main()