
## Calibration

Generate a screen calibration file by running:

`uv run ./Screen_Stuff.py`

Then:
- Hover **top-left** of the board and press `c`
- Hover **bottom-right** of the board and press `c`
- Hover each cell target in row-major order (00, 01, 02, 03, 10, 11, ...) and press `c`
- Press `ESC` to cancel

This writes `calibration.json` in the project root.

