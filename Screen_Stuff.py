"""Screen utilities for Word Hunt bot (macOS).

Requires:
- pynput (global hotkeys + mouse position)
- pillow (PIL.ImageGrab for screenshots)

Note: On macOS you may need to grant your terminal/IDE Screen Recording
permission for screenshots to work.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable


def screenshot_box_from_origin(
	x: int,
	y: int,
	size: int = 230,
	save_path: str | Path | None = None,
):
	"""Take a screenshot of a size×size box starting at (x, y) going right+down.

	Returns a PIL Image. If save_path is provided, saves the image.
	"""

	try:
		from PIL import ImageGrab  # type: ignore
	except ModuleNotFoundError as e:
		raise ModuleNotFoundError(
			"Missing dependency 'pillow'. Install with: uv add pillow"
		) from e

	bbox = (int(x), int(y), int(x) + int(size), int(y) + int(size))
	img = ImageGrab.grab(bbox=bbox)

	if save_path is not None:
		save_path = Path(save_path)
		save_path.parent.mkdir(parents=True, exist_ok=True)
		img.save(save_path)

	return img


def listen_and_print_cursor_on_f(
	on_position: Callable[[int, int], None] | None = None,
) -> None:
	"""Block and listen globally; on pressing 'f' prints mouse (x, y).

	Press ESC to quit.
	"""

	try:
		from pynput import keyboard, mouse  # type: ignore
	except ModuleNotFoundError as e:
		raise ModuleNotFoundError(
			"Missing dependency 'pynput'. Install with: uv add pynput"
		) from e

	if on_position is None:
		on_position = lambda x, y: print(f"x={x}, y={y}")

	m = mouse.Controller()

	def _on_press(key):
		try:
			# Character keys
			if key.char == "f":
				x, y = m.position
				on_position(int(x), int(y))
		except AttributeError:
			# Special keys
			if key == keyboard.Key.esc:
				return False

		return None

	print("Listening for key 'f'... (press ESC to quit)")
	with keyboard.Listener(on_press=_on_press) as listener:
		listener.join()


if __name__ == "__main__":
	# Demo: press 'f' to print coords; press ESC to quit.
	# Optional: set TAKE_SHOT=1 to also save a 230x230 screenshot at each press.
	import os

	take_shot = os.environ.get("TAKE_SHOT") == "1"

	def handler(x: int, y: int) -> None:
		print(f"x={x}, y={y}")
		if take_shot:
			out = Path("./screenshots") / f"shot_{x}_{y}.png"
			screenshot_box_from_origin(x, y, size=230, save_path=out)
			print(f"saved: {out}")

	listen_and_print_cursor_on_f(on_position=handler)
