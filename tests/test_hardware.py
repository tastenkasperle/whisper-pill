import os
import sys

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from whisper_pill.core.hardware import detect_optimal_hardware, HardwareProfile


def test_hardware_detection():
    hw = detect_optimal_hardware()
    assert isinstance(hw, HardwareProfile)
    assert hw.total_logical_cores > 0
    assert hw.optimal_threads > 0
    assert hw.optimal_threads <= hw.total_logical_cores
    print(f"[OK] Hardware detected: {hw.description}")


if __name__ == "__main__":
    test_hardware_detection()
