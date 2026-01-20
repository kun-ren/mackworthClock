from psychopy import gui, core, visual
from enums import SessionType
from mackworth_clock import MackworthClock
from prompt import RSEO_TEXT, RSEC_TEXT
from questionnaire import run_kss_gui, run_vas_f, run_nasa_tlx, run_desq
import csv
exp_info = {
    'Subject_id': '',
    'Session': '',
    'Age': '',
    'Gender': ['male', 'female', 'other'],
}

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
        'Clock radius (pixels)': 600,
        'White dot size': 6,
        'Red dot size': 10,
        'Clock Steps': 96,
        'Jump interval (ms)': 800,
        'Warmup_steps': 4,
        'Response time (ms)': 3000,
        'Minimum gap between target events (step)': 8,
        'Series number': 18,
        'Steps per series': 180,
        'Target trial rate': 0.04,
    }

    dlg = gui.DlgFromDict(mackworth_param, title='Mackworth parameters: ')
    if dlg.OK:
        return mackworth_param
    else:
        core.quit()


def main():
    mackworth_param = mackworth_parameters()
    session_type = get_session_type_dialog()
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
            run_kss_gui(subject_info['subject_id'], 'KSS – Pre-Task')
            run_desq(subject_info['subject_id'], 'DESQ - Pre-Task')

            win = visual.Window(
                fullscr=True,
                waitBlanking=True,
                color='black',
                units='pix'
            )
            run_vas_f(win, subject_info['subject_id'], 'VAS-F - Pre-Task')

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
            mackworth_clock.show_instructions(RSEO_TEXT)
            mackworth_clock.resting_state(event_stream, global_clock)
            mackworth_clock.instantiate(event_stream, global_clock)
            mackworth_clock.resting_state(event_stream, global_clock, eyes_open=False)
            keys = event_stream[0].keys()

            event_file_name = f"subject_{subject_info['subject_id']}_gender_{subject_info['gender']}_session_{subject_info['session']}.csv"

            with open(event_file_name, "w", newline="", encoding="utf-8") as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(event_stream)

            print(f"the event streaming has been written into {event_file_name}")

            # post questionnaire
            run_kss_gui(subject_info['subject_id'], 'KSS – Post-Task')
            #todo

            # only after Task
            run_nasa_tlx(win, subject_info['subject_id'], 'NASA - TLX - Pre-Task')

            # end of exprienment
        else:
            core.quit()
    elif session_type == SessionType.PRACTICE:
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