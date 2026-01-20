from psychopy import visual, core, event,gui, parallel, sound
import math
import random
from enums import Triggers, FLICKER_OFFSET
#port = parallel.ParallelPort(address=0x378) # todo

class MackworthClock:
    def __init__(self, win, radius=600, white_dot_size=6, red_dot_size=10, steps=96, step_interval=800, warmup_steps=4, response_time=3000, minimun_target_gap=8, series_num=18, steps_per_series=180, target_rate=0.04):

        self.win = win
        self.radius = radius
        self.white_dot_size = white_dot_size
        self.red_dot_size = red_dot_size
        self.steps = steps
        self.step_interval = step_interval
        self.warmup_steps = warmup_steps
        self.response_time = response_time
        self.minimun_target_gap = minimun_target_gap
        self.series_num = series_num
        self.steps_per_series = steps_per_series
        self.target_rate = target_rate
        self.white_dots = []
        self.red_dot = None


    def generate_all_series(self):
        targets = []
        for i in range(self.series_num):
            targets_within_series = []
            possible_positions = list(range(self.warmup_steps, self.steps_per_series))
            num_target_per_series = round(self.steps_per_series * self.target_rate)
            while len(targets_within_series) < num_target_per_series:
                relative_position = random.choice(possible_positions)
                absolute_position = relative_position + self.steps_per_series * i
                if all(abs(absolute_position - t) >= (self.minimun_target_gap + 1) for t in targets):
                    targets_within_series.append(relative_position)
                    targets.append(absolute_position)

        return sorted(targets)

    def instantiate(self, event_stream, global_clock) -> list:
        step_interval_sec = self.step_interval / 1000.0  # ms → s

        # ========= intial visual stimu =========
        self.white_dots = []
        for i in range(self.steps):
            angle = 2 * math.pi * i / self.steps
            x = self.radius * math.sin(angle)
            y = self.radius * math.cos(angle)

            dot = visual.Circle(
                win=self.win,
                radius=self.white_dot_size,
                fillColor='white',
                lineColor=None,
                pos=(x, y)
            )
            self.white_dots.append(dot)

        self.red_dot = visual.Circle(
            win=self.win,
            radius=self.red_dot_size,
            fillColor='red',
            lineColor=None
        )

        rt_timer = None
        series_targets = self.generate_all_series()
        all_steps = [
            1 if step in series_targets else 0
            for step in range(self.steps_per_series * self.series_num)
        ]


        step_clock = core.Clock()

        # ========= session start =========
        self.win.callOnFlip(
            self.atomic_event,
            event_stream,
            global_clock,
            Triggers.ONSET
        )
        self.win.flip()

        num_steps_red_dot_jump_over = 0
        for index, step in enumerate(all_steps):

            is_target = (step == 1)

            if is_target:
                num_steps_red_dot_jump_over += 1

            angle = 2 * math.pi * ((index+num_steps_red_dot_jump_over) % self.steps) / self.steps
            self.red_dot.pos = (
                self.radius * math.sin(angle),
                self.radius * math.cos(angle)
            )


            for dot in self.white_dots:
                dot.draw()
            self.red_dot.draw()

            trigger = (
                Triggers.TARGET_TRIAL_FLICKER
                if is_target else
                Triggers.NONE_TARGET_TRIAL_FLICKER
            )

            self.win.callOnFlip(
                self.atomic_event,
                event_stream,
                global_clock,
                trigger
            )

            self.win.callOnFlip(step_clock.reset)


            if is_target:
                rt_timer = core.CountdownTimer()
                self.win.callOnFlip(
                    rt_timer.reset,
                    self.response_time / 1000.0
                )

            self.win.flip()

            # ===== non block waiting for step interval =====
            while step_clock.getTime() < step_interval_sec:

                if 'escape' in event.getKeys():
                    self.atomic_event(event_stream, global_clock, Triggers.END)
                    core.quit()

                if rt_timer:
                    if rt_timer.getTime() > 0:
                        if 'space' in event.getKeys():
                            self.atomic_event(event_stream, global_clock, Triggers.SUCCESS_RESPONSE_FLICKER)
                            rt_timer = None
                    else:
                        self.atomic_event(event_stream, global_clock, Triggers.FAILED_RESPONSE_FLICKER)
                        rt_timer = None

        # ========= session end =========
        self.win.callOnFlip(
            self.atomic_event,
            event_stream,
            global_clock,
            Triggers.END
        )
        self.win.flip()

        return event_stream

    def resting_state(self, event_stream, global_clock, eyes_open=True, prefix="PRE"):
        """
        Resting state recording
        eyes_open=True  -> RSEO
        eyes_open=False -> RSEC
        """

        start_trigger = (
            Triggers.RSEO_START if eyes_open else Triggers.RSEC_START
        )
        end_trigger = (
            Triggers.RSEO_END if eyes_open else Triggers.RSEC_END
        )

        rest_clock = core.Clock()
        beep = sound.Sound('C', secs=0.5)
        rest_duration = 120  # second
        fixation = visual.TextStim(
            win=self.win,
            text='+',
            color='white',
            height=30
        )
        # ===== start beep + trigger =====
        self.win.callOnFlip(
            self.atomic_event,
            event_stream,
            global_clock,
            start_trigger
        )
        self.win.callOnFlip(beep.play)
        self.win.flip()

        rest_clock.reset()

        # ===== resting loop =====
        while rest_clock.getTime() < rest_duration:

            if 'escape' in event.getKeys():
                self.atomic_event(event_stream, global_clock, Triggers.END)
                core.quit()

            fixation.draw()
            self.win.flip()

        self.win.callOnFlip(beep.play)
        self.win.callOnFlip(
            self.atomic_event,
            event_stream,
            global_clock,
            end_trigger
        )

    def show_instructions(self, text):
        instruction_text = visual.TextStim(
            win=self.win,
            color='white',
            wrapWidth=1200,
            height=40
        )
        instruction_text.text = text

        while True:
            instruction_text.draw()
            self.win.flip()

            keys = event.getKeys()
            if 'space' in keys:
                break


    def atomic_event(self, event_stream, clock, trigger_code):
        """
        atomic event：for callOnFlip

        """
        t = clock.getTime()

        # port.setData(trigger_code)
        #core.wait(0.005)

        #port.setData(0)
        event_stream.append({
            "time": t,
            "trigger": trigger_code
        })

