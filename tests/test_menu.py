import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from wordgames_bot.menu import main


class MenuTests(unittest.TestCase):
    def test_dispatches_actions_and_returns_to_menu(self):
        bot, calibration = Mock(), Mock()
        modules = {"wordgames_bot.main": SimpleNamespace(main=bot),
                   "wordgames_bot.calibration": SimpleNamespace(main=calibration)}
        with patch.dict("sys.modules", modules), patch("builtins.print"), \
                patch("builtins.input", side_effect=["invalid", "2", "1", "3"]), \
                patch("wordgames_bot.menu.DEFAULT_CALIBRATION_PATH") as path:
            path.exists.return_value = True
            main()
        calibration.assert_called_once_with()
        bot.assert_called_once_with()

    def test_missing_calibration_prompts_before_running(self):
        with patch("builtins.print") as output, \
                patch("builtins.input", side_effect=["1", "q"]), \
                patch("wordgames_bot.menu.DEFAULT_CALIBRATION_PATH") as path:
            path.exists.return_value = False
            main()
        output.assert_any_call("Calibrate your board first (option 2).")

    def test_cancelled_calibration_returns_to_menu(self):
        calibration = Mock(side_effect=RuntimeError("Calibration cancelled"))
        with patch.dict("sys.modules", {"wordgames_bot.calibration": SimpleNamespace(main=calibration)}), \
                patch("builtins.print") as output, \
                patch("builtins.input", side_effect=["2", "3"]):
            main()
        output.assert_any_call("Calibration cancelled")


if __name__ == "__main__":
    unittest.main()
