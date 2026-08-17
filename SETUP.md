# Setup and Usage

This guide covers the runnable manual-input workflow and the optional screenshot-to-grid experiment for Word Hunt Bot.

## Requirements

- macOS (the screenshot implementation uses `PIL.ImageGrab` and the automation is calibrated for a desktop game window)
- Python 3.13 or newer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- Accessibility permission for the terminal or IDE that runs the bot
- Screen Recording permission if you use screenshot capture

The optional vision workflow also requires [Ollama](https://ollama.com/) and the configured Qwen3-VL model.

## Install dependencies

From the repository root:

```bash
uv sync
```

## Calibrate the board

Open the game board and keep it in the position and size you intend to use. Then run:

```bash
uv run word-hunt-calibrate
```

Follow the terminal prompts:

1. Hover over the board's top-left corner and press `c`.
2. Hover over the board's bottom-right corner and press `c`.
3. Hover over the center of every tile in row-major order and press `c` for each one: `00`, `01`, `02`, `03`, `10`, and so on.
4. Press `Esc` at any point to cancel.

The command writes the captured bounding box and 16 tile coordinates to `config/calibration.json`.

> Recalibrate whenever the game window, display scaling, board position, or board size changes.

## Run the bot

```bash
uv run word-hunt-bot
```

When prompted, enter exactly 16 letters in row-major order. Spaces are optional, so both examples below are accepted:

```text
tooucrrhnelnadal
```

```text
toou crrh neln adal
```

After a three-second countdown, the bot solves the board, prints each selected word, and drags across its saved tile path. Longer words are attempted first. The runner stops playback after approximately 70 seconds.

## Optional screenshot and local vision workflow

The repository includes the building blocks for image-based board entry, but this path is commented out in `src/wordgames_bot/main.py`.

1. Install and start Ollama.
2. Pull the model configured in `src/wordgames_bot/solver.py`:

   ```bash
   ollama pull qwen3-vl:4b
   ```

3. Use `take_screenshot(...)` to capture the calibrated board as `images/captures/curr_board.png`.
4. Pass that image to `llm_image_to_board(...)`.
5. Replace the manual-input line in `src/wordgames_bot/main.py` with the screenshot-derived board while experimenting.

The extraction prompt in `data/board_extraction_prompt.txt` requests a lowercase 4×4 JSON grid. Model output is parsed directly as JSON, so malformed or decorated output will raise an error.

## Troubleshooting

### The mouse does not move or drag

Open **System Settings → Privacy & Security → Accessibility** and enable access for the terminal or IDE running Python.

### Screenshots fail or are blank

Enable **Screen Recording** for the same application, then restart it before trying again.

### Swipes miss the tiles

Run `uv run word-hunt-calibrate` again without moving or resizing the board afterward. Capture each tile near its center.

### A board is rejected

Manual input must contain exactly 16 alphabetic characters. Spaces are removed automatically; punctuation and digits are not accepted.

### The vision model is unavailable

Confirm Ollama is running and that `qwen3-vl:4b` appears in `ollama list`. The default manual-entry workflow does not require the model server to be running.
