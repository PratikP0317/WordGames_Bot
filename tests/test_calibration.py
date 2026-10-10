import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from wordgames_bot.screen import CalibrationConfig, calibrate_via_keypress, take_screenshot


class CalibrationTests(unittest.TestCase):
    def test_interpolates_rows_and_columns_and_roundtrips(self):
        config = CalibrationConfig.from_centers((100, 200), (310, 470))
        self.assertTrue(config.is_complete())
        self.assertEqual(config.grid[0], [(100, 200), (170, 200), (240, 200), (310, 200)])
        self.assertEqual(config.grid[2][1], (170, 380))
        self.assertEqual(config.grid[-1][-1], (310, 470))
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "calibration.json"
            config.save_json(destination)
            self.assertEqual(CalibrationConfig.load_json(destination), config)

    def test_rounding_preserves_endpoints(self):
        config = CalibrationConfig.from_centers((-20, 10), (81, 113))
        self.assertEqual(config.grid[0][0], (-20, 10))
        self.assertEqual(config.grid[1][1], (14, 44))
        self.assertEqual(config.grid[-1][-1], (81, 113))

    def test_rejects_invalid_centers_and_sizes(self):
        for bottom_right in [(100, 300), (200, 200), (50, 100)]:
            with self.assertRaises(ValueError):
                CalibrationConfig.from_centers((100, 200), bottom_right)
        with self.assertRaises(ValueError):
            CalibrationConfig.from_centers((0, 0), (100, 100), 1)

    def capture(self, positions, keys):
        mouse = Mock()
        type(mouse).position = unittest.mock.PropertyMock(side_effect=positions)
        keyboard = SimpleNamespace(Key=SimpleNamespace(esc="escape"))

        def make_listener(on_release):
            listener = Mock()
            listener.__enter__ = Mock(return_value=listener)
            listener.__exit__ = Mock(return_value=False)

            def join():
                for key in keys:
                    if on_release(key) is False:
                        break

            listener.join.side_effect = join
            return listener

        keyboard.Listener = make_listener
        pynput = SimpleNamespace(keyboard=keyboard, mouse=SimpleNamespace(Controller=lambda: mouse))
        with patch.dict("sys.modules", {"pynput": pynput}), patch("builtins.print"):
            return calibrate_via_keypress()

    def test_only_two_captures_needed(self):
        config = self.capture([(100, 200), (310, 470)], [SimpleNamespace(char="c")] * 2)
        self.assertEqual(config.grid[1][2], (240, 290))

    def test_invalid_second_capture_can_be_retried(self):
        config = self.capture([(100, 200), (90, 100), (310, 470)], [SimpleNamespace(char="c")] * 3)
        self.assertTrue(config.is_complete())

    def test_escape_cancels(self):
        with self.assertRaisesRegex(RuntimeError, "cancelled"):
            self.capture([], ["escape"])

    def test_legacy_explicit_grid_is_preserved(self):
        data = {"grid_size": 2, "top_left": [0, 0], "bottom_right": [100, 100],
                "grid": [[[12, 13], [80, 14]], [[14, 81], [82, 83]]]}
        self.assertEqual(CalibrationConfig.from_dict(data).to_dict(), data)

    def test_screenshot_extends_beyond_cell_centers(self):
        config = CalibrationConfig.from_centers((100, 200), (310, 470))
        with patch("PIL.ImageGrab.grab") as grab, tempfile.TemporaryDirectory() as directory:
            take_screenshot(config, with_timer=False, output_path=Path(directory) / "board.png")
        grab.assert_called_once_with(bbox=(65, 155, 345, 515))


if __name__ == "__main__":
    unittest.main()
