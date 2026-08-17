"""Screen utilities for Word Hunt bot (macOS).

Requires:
- pynput (global hotkeys + mouse position)
- pillow (PIL.ImageGrab for screenshots)

Note: On macOS you may need to grant your terminal/IDE Screen Recording
permission for screenshots to work.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from PIL import ImageGrab
from pynput.mouse import Button, Controller

from .paths import DEFAULT_CALIBRATION_PATH, DEFAULT_CAPTURE_PATH

Point = tuple[int, int]


@dataclass(slots=True)
class CalibrationConfig:
    """Holds screen calibration for a Word Hunt-style grid."""

    grid_size: int = 4
    top_left: Point | None = None
    bottom_right: Point | None = None
    grid: list[list[Point]] = field(default_factory=list)

    def is_complete(self) -> bool:
        if self.top_left is None or self.bottom_right is None:
            return False
        if len(self.grid) != self.grid_size:
            return False
        return all(len(row) == self.grid_size for row in self.grid)

    def to_dict(self) -> dict:
        return {
            "grid_size": self.grid_size,
            "top_left": list(self.top_left) if self.top_left is not None else None,
            "bottom_right": list(self.bottom_right)
            if self.bottom_right is not None
            else None,
            "grid": [[list(p) for p in row] for row in self.grid],
        }

    @staticmethod
    def from_dict(data: dict) -> CalibrationConfig:
        grid_size = int(data.get("grid_size", 4))
        tl = data.get("top_left")
        br = data.get("bottom_right")
        grid_raw = data.get("grid", [])
        grid: list[list[Point]] = []
        for row in grid_raw:
            grid.append([(int(p[0]), int(p[1])) for p in row])
        return CalibrationConfig(
            grid_size=grid_size,
            top_left=(int(tl[0]), int(tl[1])) if tl is not None else None,
            bottom_right=(int(br[0]), int(br[1])) if br is not None else None,
            grid=grid,
        )

    def save_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def load_json(path: str | Path) -> CalibrationConfig:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return CalibrationConfig.from_dict(data)


def calibrate_via_keypress(
    grid_size: int = 4,
    key_char: str = "c",
    save_path: str | Path | None = None,
) -> CalibrationConfig:
    """Interactively capture board calibration using a global keypress.

    Flow:
    - Hover top-left of the board, press `key_char`
    - Hover bottom-right of the board, press `key_char`
    - Hover each grid cell target in row-major order and press `key_char`
      (00, 01, 02, 03, 10, 11, ...)

    Press ESC to cancel.
    """

    if len(key_char) != 1:
        raise ValueError("key_char must be a single character")

    try:
        from pynput import keyboard, mouse  # type: ignore
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "Missing dependency 'pynput'. Install with: uv add pynput"
        ) from e

    m = mouse.Controller()
    config = CalibrationConfig(grid_size=int(grid_size))
    grid_points: list[list[Point | None]] = [
        [None for _ in range(config.grid_size)] for _ in range(config.grid_size)
    ]
    step = 0  # 0=top_left, 1=bottom_right, 2=grid
    grid_index = 0
    total_grid = config.grid_size * config.grid_size
    cancelled = False

    def _next_prompt() -> str:
        if step == 0:
            return f"Next: hover TOP-LEFT and press '{key_char}'"
        if step == 1:
            return f"Next: hover BOTTOM-RIGHT and press '{key_char}'"
        row = grid_index // config.grid_size
        col = grid_index % config.grid_size
        return f"Next: hover grid[{row}][{col}] and press '{key_char}'"

    def _capture_position() -> Point:
        x, y = m.position
        return (int(x), int(y))

    listener: keyboard.Listener | None = None

    def _on_press(key) -> None:
        nonlocal step, grid_index, cancelled

        # Character keys
        if getattr(key, "char", None) in {key_char.lower(), key_char.upper()}:
            pos = _capture_position()
            if step == 0:
                config.top_left = pos
                step = 1
                print(f"Captured top_left: {pos}")
                print(_next_prompt())
                return
            if step == 1:
                config.bottom_right = pos
                step = 2
                print(f"Captured bottom_right: {pos}")
                print(_next_prompt())
                return

            row = grid_index // config.grid_size
            col = grid_index % config.grid_size
            grid_points[row][col] = pos
            print(f"Captured grid[{row}][{col}]: {pos}")
            grid_index += 1
            if grid_index >= total_grid and listener is not None:
                listener.stop()
                return
            print(_next_prompt())
            return

        # Special keys
        if key == keyboard.Key.esc:
            cancelled = True
            if listener is not None:
                listener.stop()

    print("Calibration started. Press ESC to cancel.")
    print(_next_prompt())
    listener = keyboard.Listener(on_press=_on_press)
    listener.start()
    listener.join()

    if cancelled:
        raise RuntimeError("Calibration cancelled")
    if config.top_left is None or config.bottom_right is None:
        raise RuntimeError("Calibration incomplete: missing bounding box")

    grid_final: list[list[Point]] = []
    for r in range(config.grid_size):
        row_final: list[Point] = []
        for c in range(config.grid_size):
            p = grid_points[r][c]
            if p is None:
                raise RuntimeError("Calibration incomplete: missing grid points")
            row_final.append(p)
        grid_final.append(row_final)
    config.grid = grid_final

    if save_path is not None:
        config.save_json(save_path)
        print(f"Saved calibration: {Path(save_path)}")

    return config


def run_calibration() -> None:
    config = calibrate_via_keypress(
        grid_size=4,
        key_char="c",
        save_path=DEFAULT_CALIBRATION_PATH,
    )
    print("Calibration complete.")
    print(f"top_left={config.top_left} bottom_right={config.bottom_right}")


def take_screenshot(
    config: CalibrationConfig,
    with_timer: bool = True,
    output_path: str | Path = DEFAULT_CAPTURE_PATH,
) -> None:
    """Take a screenshot of the calibrated board area."""
    if config.top_left is None or config.bottom_right is None:
        raise ValueError("CalibrationConfig is incomplete")

    box = (
        config.top_left[0],
        config.top_left[1],
        config.bottom_right[0],
        config.bottom_right[1],
    )
    if with_timer:
        from time import sleep

        print("Taking screenshot in 5 seconds. Prepare the screen.")
        sleep(1)
        print("4...")
        sleep(1)
        print("3...")
        sleep(1)
        print("2...")
        sleep(1)
        print("1...")
        sleep(1)
        print("Capturing screenshot now.")
        sleep(0.5)

    screenshot = ImageGrab.grab(bbox=box)
    screenshot.show()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot.save(output_path)
    print(f"Screenshot saved as {output_path}")


mouse = Controller()


def trace_word_path(path, config):
    if not path:
        return

    r0, c0 = path[0]
    x0, y0 = config.grid[r0][c0]

    mouse.position = (x0, y0)
    time.sleep(0.2)
    mouse.press(Button.left)

    for r, c in path[1:]:
        x, y = config.grid[r][c]
        mouse.position = (x, y)
        time.sleep(0.08)

    mouse.release(Button.left)
