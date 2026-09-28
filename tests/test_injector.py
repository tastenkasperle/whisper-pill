import os
import sys
import ctypes

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from whisper_pill.core.injector import INPUT, KEYBDINPUT, make_key_input, VK_CONTROL, VK_V, KEYEVENTF_KEYUP, TextInjector


def test_input_structures():
    # Verify ctypes alignment and size
    inp = make_key_input(VK_CONTROL, 0)
    assert inp.type == 1  # INPUT_KEYBOARD
    assert inp.union.ki.wVk == VK_CONTROL
    assert inp.union.ki.dwFlags == 0

    inp_up = make_key_input(VK_V, KEYEVENTF_KEYUP)
    assert inp_up.union.ki.wVk == VK_V
    assert inp_up.union.ki.dwFlags == KEYEVENTF_KEYUP

    assert ctypes.sizeof(INPUT) > 0
    print(f"[OK] Win32 SendInput structures validated (sizeof INPUT: {ctypes.sizeof(INPUT)} bytes).")


def test_window_detection():
    hwnd = TextInjector.get_foreground_window()
    print(f"[OK] Current foreground window HWND: {hwnd}")
    if hwnd:
        assert TextInjector.is_valid_window(hwnd) is True


if __name__ == "__main__":
    test_input_structures()
    test_window_detection()
