import subprocess
import time
import ctypes
from ctypes import wintypes
from psychopy import monitors, visual, core
from screeninfo import get_monitors

import ctypes

SW_SHOWMINNOACTIVE = 7
info = subprocess.STARTUPINFO()
info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = SW_SHOWMINNOACTIVE

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per monitor
except:
    ctypes.windll.user32.SetProcessDPIAware()
# -------------------- Windows API --------------------
user32 = ctypes.windll.user32

HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040


def get_hwnds_for_pid(pid):
    """get windows HWND list"""
    hwnds = []

    EnumWindows = user32.EnumWindows
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    IsWindowVisible = user32.IsWindowVisible

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def foreach_window(hwnd, lParam):
        _pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(_pid))
        if _pid.value == pid and IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    EnumWindows(foreach_window, 0)
    return hwnds


def set_window_topmost_noactivate(hwnd):
    """top most a window"""
    user32.SetWindowPos(
        hwnd,
        HWND_TOPMOST,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
    )


def move_window_to_screen(hwnd, x, y, width, height):
    """move and resize a window"""
    SWP_NOZORDER = 0x0004
    SWP_SHOWWINDOW = 0x0040
    user32.SetWindowPos(hwnd, HWND_TOPMOST, x, y, width, height, SWP_NOZORDER | SWP_SHOWWINDOW | SWP_NOACTIVATE)


# -------------------- screen info --------------------
def get_screens_info():
    """

    return a list of  {"width": ..., "height": ..., "x": 0, "y": 0}
    """
    screens = []
    for i, m in enumerate(get_monitors()):
        screens.append({
            "x": m.x, # start point
            "y": m.y,
            "width": m.width,
            "height": m.height
        })
    return screens


# -------------------- VisualStimuli --------------------
def launch_visualstimuli_on_screen(exe_path, screen_index, paradigm_winHandle):
    """
    lauch VisualStimuli.exe
    """
    screens = get_screens_info()
    if screen_index >= len(screens):
        raise ValueError(f"screen_index {screen_index} out of range")

    target = screens[screen_index]
    CREATE_NO_WINDOW = 0x08000000
    #process = subprocess.Popen(exe_path, creationflags=CREATE_NO_WINDOW)
    process = subprocess.Popen(exe_path, startupinfo=info)

    # wait for the creation of the flicker window
    hwnds = []
    timeout = 10
    start = time.time()
    while time.time() - start < timeout:
        hwnds = get_hwnds_for_pid(process.pid)
        if hwnds:
            break
        time.sleep(0.1)
    if not hwnds:
        raise RuntimeError("VisualStimuli window not found")

    # move and top up
    for hwnd in hwnds:
        move_window_to_screen(hwnd, target["x"], target["y"], target["width"], target["height"])
        #set_window_topmost_noactivate(hwnd)

    #paradigm_hwnd = int(paradigm_winHandle)
    user32.SetForegroundWindow(paradigm_winHandle._hwnd)

    return process