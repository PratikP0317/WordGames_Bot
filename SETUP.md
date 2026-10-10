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

Open the game board and keep it in the position and size you intend to use. Start the menu:

```bash
uv run main.py
```

Choose **2. Calibrate board**, then follow the terminal prompts:

1. Hover over the **center of the top-left tile** and press and release `c`.
2. Hover over the **center of the bottom-right tile** and press and release `c`.
3. Press `Esc` at any point to cancel and return to the menu.

The bot calculates all 16 tile centers by evenly spacing them between the two captured centers, then saves them to `config/calibration.json`. This assumes an axis-aligned, evenly spaced board. Existing calibration files still work. The direct `uv run word-hunt-calibrate` command is also available.

> Recalibrate whenever the game window, display scaling, board position, or board size changes.

## Run the bot

```bash
uv run main.py
```

Choose **1. Run bot**. The direct `uv run word-hunt-bot` command is also available.

When prompted, enter exactly 16 letters in row-major order. Spaces are optional, so both examples below are accepted:

```text
tooucrrhnelnadal
```

```text
toou crrh neln adal
```

After a three-second countdown, the bot solves the board, prints each selected word, and drags across its saved tile path. Longer words are attempted first. The runner stops playback after approximately 70 seconds.

## Optional screenshot and local vision workflow

The repository includes the building blocks for image-based board entry, but this path is not enabled in `src/wordgames_bot/main.py`.

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

Choose **Calibrate board** again without moving or resizing the board afterward. Capture the centers of the top-left and bottom-right tiles.

### A board is rejected

Manual input must contain exactly 16 alphabetic characters. Spaces are removed automatically; punctuation and digits are not accepted.

### The vision model is unavailable

Confirm Ollama is running and that `qwen3-vl:4b` appears in `ollama list`. The default manual-entry workflow does not require the model server to be running.
