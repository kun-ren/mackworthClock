from psychopy import gui, core, visual, event
from datetime import datetime
from prompt import KSS_INSTRUCTION, VAS_ITEMS, DESQ_ITEMS, NASA_TLX_DIMENSIONS
def append_to_report(line: str, questionnaire_name):
    """
    reports.txt
    """
    filename=f"{questionnaire_name}_reports.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_kss_gui(subject_id, title="KSS – Pre-Task",):
    """
    Runs KSS questionnaire and returns rating (int)
    """
    today = datetime.now().strftime("%Y-%m-%d")

    win = visual.Window(fullscr=True, color='black', units='pix')

    instruction_text = visual.TextStim(
        win=win,
        text=KSS_INSTRUCTION + "\n\nPress SPACE to continue",
        color='white',
        wrapWidth=1200,
        height=28
    )

    while True:
        instruction_text.draw()
        win.flip()
        keys = event.getKeys()
        if 'space' in keys:
            break
        if 'escape' in keys:
            core.quit()

    win.close()

    info = {
        "Participant ID": subject_id,
        "Date": today,
        "Plese evaluate your Sleepiness Rating (1-9)": "5"
    }

    dlg = gui.DlgFromDict(
        dictionary=info,
        title=title,
        order=["Participant ID", "Date", "Sleepiness Rating (1-9)"],
        fixed=[],
    )

    if not dlg.OK:
        core.quit()

    # Validate rating
    try:
        rating = int(info["Plese evaluate your Sleepiness Rating (1-9)"])
        if rating < 1 or rating > 9:
            raise ValueError
    except ValueError:
        gui.popupError("Please enter a valid number between 1 and 9.")
        return run_kss_gui(title)

    append_to_report(f"Subject {subject_id}, {title}: {rating}, "
                     f"Date: {today}", f"KSS")

    return


def run_desq(subject_id, title="DESQ"):
    today = datetime.now().strftime("%Y-%m-%d")
    desq_responses = {}

    options = DESQ_ITEMS.copy()

    dlg = gui.DlgFromDict(
        dictionary=options,
        title=f"DESQ - Participant {subject_id}",
    )
    if not dlg.OK:
        core.quit()

    for key, value in options.items():
        if value == 'YES':
            desq_responses[key] = 1
        else:
            desq_responses[key] = 0

    total_score = sum(desq_responses.values())

    append_to_report(
        f"Subject {subject_id}, {title}, Date: {today}, Responses: {desq_responses}, Total Score: {total_score}",
        'DESQ'
    )

    return desq_responses, total_score

def run_nasa_tlx(win, subject_id, title):
    """
    """
    ratings = []
    today = datetime.now().strftime("%Y-%m-%d")
    for idx, dim in enumerate(NASA_TLX_DIMENSIONS, start=1):
        instruction = visual.TextStim(
            win=win,
            text=f"Dimension {idx}: {dim}\n\nUse mouse to adjust slider, press SPACE to confirm",
            color='white',
            wrapWidth=1200,
            height=28,
            pos=(0, 200)
        )


        slider_line = visual.Line(win=win, start=(-400, 0), end=(400, 0), lineColor='white', lineWidth=3)

        cursor = visual.Circle(win=win, radius=10, fillColor='red', lineColor='red', pos=(0,0))


        left_text = visual.TextStim(win=win, text="Low", pos=(-420, -40), color='white', height=24)
        right_text = visual.TextStim(win=win, text="High", pos=(420, -40), color='white', height=24)

        cursor_x = 0
        mouse = event.Mouse(visible=True, win=win)

        while True:

            if mouse.getPressed()[0]:
                pos = mouse.getPos()
                cursor_x = max(-400, min(400, pos[0]))
            keys = event.getKeys()
            if 'left' in keys:
                cursor_x = max(-400, cursor_x-5)
            if 'right' in keys:
                cursor_x = min(400, cursor_x+5)
            if 'space' in keys:
                break
            if 'escape' in keys:
                core.quit()

            cursor.pos = (cursor_x, 0)

            instruction.draw()
            slider_line.draw()
            left_text.draw()
            right_text.draw()
            cursor.draw()
            win.flip()

        rating = ((cursor_x + 400)/800)*100
        ratings.append(rating)

    rating_str = "".join(str(e) + ', ' for e in ratings)
    append_to_report(f"Subject {subject_id}, {title}: {rating_str}, "
                     f"Date: {today}", f"NASA-TLX")

    return ratings


def run_vas_f(win, subject_id, title):

    ratings = []
    today = datetime.now().strftime("%Y-%m-%d")

    for idx, (left_label, right_label) in enumerate(VAS_ITEMS, start=1):

        instruction = visual.TextStim(
            win=win,
            text=f"Item {idx}: {left_label} – {right_label}\n\nUse mouse to adjust slider, press SPACE when done.",
            color='white',
            wrapWidth=1200,
            height=28,
            pos=(0, 200)
        )


        slider = visual.Rect(
            win=win,
            width=600,
            height=6,
            fillColor='white',
            lineColor='white',
            pos=(0, 0)
        )
        cursor = visual.Circle(
            win=win,
            radius=10,
            fillColor='red',
            lineColor='red',
            pos=(0, 0)
        )

        left_text = visual.TextStim(win=win, text=left_label, pos=(-320, -30), color='white', height=24)
        left_measure = visual.TextStim(win=win, text='0', pos=(-320, 30), color='white', height=24)
        right_text = visual.TextStim(win=win, text=right_label, pos=(320, -30), color='white', height=24)
        right_measure = visual.TextStim(win=win, text='10', pos=(320, 30), color='white', height=24)



        cursor_x = 0
        mouse = event.Mouse(visible=True, win=win)

        while True:
            if mouse.getPressed()[0]:
                pos = mouse.getPos()
                cursor_x = max(-300, min(300, pos[0]))
            keys = event.getKeys()
            if 'left' in keys:
                cursor_x = max(-300, cursor_x - 5)
            if 'right' in keys:
                cursor_x = min(300, cursor_x + 5)
            if 'space' in keys:
                break
            if 'escape' in keys:
                core.quit()

            cursor.pos = (cursor_x, 0)

            instruction.draw()
            slider.draw()
            left_text.draw()
            right_text.draw()
            cursor.draw()
            win.flip()

        rating = ((cursor_x + 300) / 600) * 100
        ratings.append(rating)
    rating_str = "".join(str(e) + ', ' for e in ratings)
    append_to_report(f"Subject {subject_id}, {title}: {rating_str}, "
                     f"Date: {today}", f"VAS-F")
    return ratings



