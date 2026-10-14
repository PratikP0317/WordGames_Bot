import unittest
from threading import Event
from types import SimpleNamespace
from unittest.mock import Mock, patch

from wordgames_bot.screen import CalibrationConfig, trace_word_path
from wordgames_bot.solver import WordHuntBot


class StopTests(unittest.TestCase):
    def test_stop_during_drag_releases_mouse_and_skips_remaining_tiles(self):
        mouse = Mock()
        stop = Event()
        waits = 0

        def wait(timeout):
            nonlocal waits
            waits += 1
            if waits == 2:
                stop.set()
            return stop.is_set()

        module = SimpleNamespace(Controller=lambda: mouse, Button=SimpleNamespace(left="left"))
        config = CalibrationConfig.from_centers((0, 0), (300, 300))
        with patch.dict("sys.modules", {"pynput.mouse": module}), patch.object(stop, "wait", wait):
            trace_word_path([(0, 0), (0, 1), (0, 2)], config, stop_event=stop)
        mouse.press.assert_called_once_with("left")
        mouse.release.assert_called_once_with("left")
        self.assertEqual(mouse.position, (100, 0))

    def test_stop_before_press_does_not_click(self):
        mouse = Mock()
        stop = Event()
        module = SimpleNamespace(Controller=lambda: mouse, Button=SimpleNamespace(left="left"))
        config = CalibrationConfig.from_centers((0, 0), (300, 300))
        with patch.dict("sys.modules", {"pynput.mouse": module}), patch.object(stop, "wait", return_value=True):
            trace_word_path([(0, 0), (0, 1)], config, stop_event=stop)
        mouse.press.assert_not_called()

    def test_cancelled_solver_skips_search(self):
        stop = Event()
        stop.set()
        with patch("wordgames_bot.solver.DictionaryTrie"):
            bot = WordHuntBot([list("abcd")] * 4)
        with patch.object(bot, "dfs") as dfs:
            bot.solve(stop_event=stop)
        dfs.assert_not_called()


if __name__ == "__main__":
    unittest.main()
