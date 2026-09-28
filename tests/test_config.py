import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from whisper_pill.core.config import AppConfig


def test_default_config():
    cfg = AppConfig()
    assert cfg.default_model_tier == "High"
    assert cfg.hotkey == "F8"
    assert "High" in cfg.model_presets
    assert len(cfg.quips) > 0
    print("[OK] Default AppConfig validated.")


def test_config_save_load():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    try:
        cfg = AppConfig(default_model_tier="Low", hotkey="F9", sound_enabled=False)
        cfg.save(temp_path)

        loaded = AppConfig.load(temp_path)
        assert loaded.default_model_tier == "Low"
        assert loaded.hotkey == "F9"
        assert loaded.sound_enabled is False
        print("[OK] Config save & load cycle validated.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    test_default_config()
    test_config_save_load()
