"""
whisper_pill.core.injector
--------------------------
Modern Windows keystroke and clipboard injection engine.
Uses native Win32 SendInput (replacing legacy keybd_event) with proper
input structure alignment and window focus restoration.
"""

from __future__ import annotations
import ctypes
from ctypes import wintypes
import time
import pyperclip


# --- Win32 Native Structures (MSDN Standard) ---
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_CONTROL = 0x11
VK_V = 0x56

ULONG_PTR = ctypes.c_ulong if ctypes.sizeof(ctypes.c_void_p) == 4 else ctypes.c_ulonglong


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUTunion(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUTunion),
    ]


# Win32 API Functions
user32 = ctypes.windll.user32
SendInput = user32.SendInput
SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
SendInput.restype = wintypes.UINT


def make_key_input(vk_code: int, flags: int = 0) -> INPUT:
    """Creates a single Win32 keyboard INPUT packet."""
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki = KEYBDINPUT(
        wVk=vk_code,
        wScan=0,
        dwFlags=flags,
        time=0,
        dwExtraInfo=0
    )
    return inp


def send_paste_input() -> None:
    """
    Sends atomic Ctrl+V keystrokes using modern Win32 SendInput.
    Presses Control down, V down, V up, Control up in an atomic batch.
    """
    inputs = (INPUT * 4)(
        make_key_input(VK_CONTROL, 0),
        make_key_input(VK_V, 0),
        make_key_input(VK_V, KEYEVENTF_KEYUP),
        make_key_input(VK_CONTROL, KEYEVENTF_KEYUP),
    )
    SendInput(4, inputs, ctypes.sizeof(INPUT))


class TextInjector:
    """
    Handles reliable clipboard insertion and focus hand-off to the active application.
    """

    @staticmethod
    def get_foreground_window() -> int:
        """Returns the handle (HWND) of the currently focused top-level window."""
        return user32.GetForegroundWindow()

    @staticmethod
    def is_valid_window(hwnd: int) -> bool:
        """Verifies if the given window handle is still alive."""
        return bool(user32.IsWindow(hwnd)) if hwnd else False

    @classmethod
    def restore_focus(cls, hwnd: int) -> bool:
        """Restores focus to the target window prior to keystroke simulation."""
        if not cls.is_valid_window(hwnd):
            return False
        return bool(user32.SetForegroundWindow(hwnd))

    @staticmethod
    def get_window_title(hwnd: int) -> str:
        """Returns the window title text of the given window handle."""
        if not hwnd or not user32.IsWindow(hwnd):
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value

    @classmethod
    def paste_text(cls, text: str, target_hwnd: int | None = None) -> bool:
        """
        Copies text to clipboard, restores window focus, verifies safety, and triggers atomic Ctrl+V.
        """
        if not text:
            return False

        # Put transcribed text into Windows clipboard
        pyperclip.copy(text)

        # Restore window focus if a target was recorded
        if target_hwnd and cls.is_valid_window(target_hwnd):
            cls.restore_focus(target_hwnd)
            # Brief thread switch interval for Windows message queue
            time.sleep(0.04)

        current_fg = cls.get_foreground_window()
        current_title = cls.get_window_title(current_fg)

        # Fire Team Elite Security Check: Verify that we are not pasting into an unapproved or hijacked window
        from whisper_pill.core.guard import SecurityGuard
        safe, reason = SecurityGuard.verify_paste_safety(target_hwnd, current_fg, current_title)
        if not safe:
            print(f"[!] {reason}")
            return False

        # Fire native SendInput
        send_paste_input()
        return True
