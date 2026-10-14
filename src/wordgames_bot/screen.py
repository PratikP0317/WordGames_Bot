"""Screen utilities for Word Hunt bot (macOS).

Requires:
- pynput (global hotkeys + mouse position)
- pillow (PIL.ImageGrab for screenshots)

Note: On macOS you may need to grant your terminal/IDE Screen Recording
permission for screenshots to work.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event

from .paths import DEFAULT_CALIBRATION_PATH, DEFAULT_CAPTURE_PATH

Point = tuple[int, int]


@dataclass(slots=True)
class CalibrationConfig:
    """Holds screen calibration for a Word Hunt-style grid."""

    grid_size: int = 4
    top_left: Point | None = None
    bottom_right: Point | None = None
    grid: list[list[Point]] = field(default_factory=list)

    @staticmethod
    def from_centers(
        top_left: Point, bottom_right: Point, grid_size: int = 4
    ) -> CalibrationConfig:
        """Interpolate an evenly spaced grid from its opposite cell centers."""
        if grid_size < 2:
            raise ValueError("grid_size must be at least 2")
        if bottom_right[0] <= top_left[0] or bottom_right[1] <= top_left[1]:
            raise ValueError("Bottom-right center must be below and right of top-left.")
        dx = (bottom_right[0] - top_left[0]) / (grid_size - 1)
        dy = (bottom_right[1] - top_left[1]) / (grid_size - 1)
        grid = [
            [
                (round(top_left[0] + col * dx), round(top_left[1] + row * dy))
                for col in range(grid_size)
            ]
            for row in range(grid_size)
        ]
        return CalibrationConfig(grid_size, top_left, bottom_right, grid)

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
    - Hover the CENTER of the top-left cell, press and release `key_char`
    - Hover the CENTER of the bottom-right cell, press and release `key_char`
    - Calculate every other cell center automatically

    Press ESC to cancel.
    """

    if len(key_char) != 1:
        raise ValueError("key_char must be a single character")
    if grid_size < 2:
        raise ValueError("grid_size must be at least 2")

    try:
        from pynput import keyboard, mouse  # type: ignore
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "Missing dependency 'pynput'. Install with: uv add pynput"
        ) from e

    m = mouse.Controller()
    config: CalibrationConfig | None = None
    top_left: Point | None = None
    cancelled = False

    def _next_prompt() -> str:
        cell = "TOP-LEFT" if top_left is None else "BOTTOM-RIGHT"
        return f"Next: hover the CENTER of the {cell} cell and press '{key_char}'"

    def _capture_position() -> Point:
        x, y = m.position
        return (int(x), int(y))

    def _on_release(key):
        nonlocal config, top_left, cancelled

        # Character keys
        if getattr(key, "char", None) in {key_char.lower(), key_char.upper()}:
            pos = _capture_position()
            if top_left is None:
                top_left = pos
                print(f"Captured top-left cell center: {pos}")
                print(_next_prompt())
                return
            try:
                config = CalibrationConfig.from_centers(top_left, pos, grid_size)
            except ValueError as error:
                print(error)
                print(_next_prompt())
                return
            print(f"Captured bottom-right cell center: {pos}")
            print(f"Calculated all {grid_size * grid_size} cell centers.")
            return False

        # Special keys
        if key == keyboard.Key.esc:
            cancelled = True
            return False

    print("Calibration started. Press ESC to cancel.")
    print(_next_prompt())
    with keyboard.Listener(on_release=_on_release) as listener:
        listener.join()

    if cancelled:
        raise RuntimeError("Calibration cancelled")
    if config is None:
        raise RuntimeError("Calibration incomplete: missing cell centers")

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
    from PIL import ImageGrab

    if not config.is_complete() or config.grid_size < 2:
        raise ValueError("CalibrationConfig is incomplete")

    # Extend half a cell beyond the centers to capture the whole board.
    top_left = config.grid[0][0]
    bottom_right = config.grid[-1][-1]
    half_width = (bottom_right[0] - top_left[0]) / (2 * (config.grid_size - 1))
    half_height = (bottom_right[1] - top_left[1]) / (2 * (config.grid_size - 1))
    box = (
        round(top_left[0] - half_width),
        round(top_left[1] - half_height),
        round(bottom_right[0] + half_width),
        round(bottom_right[1] + half_height),
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


def trace_word_path(
    path, config, stop_event: Event | None = None,
    *, start_delay: float = 0.2, step_delay: float = 0.08,
):
    stop_event = stop_event if stop_event is not None else Event()
    if not path or stop_event.is_set():
        return

    from pynput.mouse import Button, Controller

    mouse = Controller()

    r0, c0 = path[0]
    x0, y0 = config.grid[r0][c0]

    mouse.position = (x0, y0)
    if stop_event.wait(start_delay):
        return
    mouse.press(Button.left)

    try:
        for r, c in path[1:]:
            if stop_event.is_set():
                break
            x, y = config.grid[r][c]
            mouse.position = (x, y)
            if stop_event.wait(step_delay):
                break
    finally:
        mouse.release(Button.left)
