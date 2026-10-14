<div align="center">

# Word Hunt Bot

### Losing at Word Hunt? Apparently my answer was to write a bot.

[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Package manager: uv](https://img.shields.io/badge/package%20manager-uv-6E56CF)](https://docs.astral.sh/uv/)
[![Platform: macOS](https://img.shields.io/badge/platform-macOS-111111?logo=apple)](https://www.apple.com/macos/)

[Overview](#overview) · [How it works](#how-it-works) · [Architecture](#architecture) · [Getting started](#getting-started)

<img src="images/demo/board.png" alt="Example 4 by 4 Word Hunt board" width="360">

</div>

## Overview

I made this because I kept losing to my friend at Word Hunt on GamePigeon. After enough losses, I decided to make a bot. A perfectly reasonable response to a word game.

Along the way, it turned into a fun project for learning about tries, graph search, and mouse automation. The motivation was personal. The data structures are educational.

Give Word Hunt Bot the 16 board letters and it will:

1. search every valid adjacent-letter path;
2. prune impossible paths with a prefix trie;
3. order the results longest first, shortest first, or randomly; and
4. trace each word across calibrated screen coordinates.

The project combines a classic graph-search problem with desktop automation. It also includes an experimental local vision path that can convert a board screenshot into a letter grid with a Qwen3-VL model served by Ollama. The current `main.py` flow uses manual letter entry by default.

## What it demonstrates

| Capability | Implementation |
| --- | --- |
| Board search | Depth-first search explores all eight neighboring tiles without reusing a tile in one word. |
| Fast validation | A custom trie rejects branches as soon as their letter sequence is no longer a valid prefix. |
| Word prioritization | Choose longest first, shortest first, or random order; each word is played once. |
| Screen automation | Calibrated cell coordinates are translated into click-and-drag mouse paths. |
| Board capture | The calibrated board region can be saved as an image for processing. |
| Local vision experiment | Ollama and Qwen3-VL can parse a screenshot into a 4×4 JSON letter grid. |

## How it works

```mermaid
flowchart LR
    A[16 board letters] --> B[4×4 grid]
    B --> C[DFS from every tile]
    D[ENABLE word list] --> E[Prefix trie]
    E --> C
    C --> F[Valid words + tile paths]
    F --> G[Choose word order]
    H[Screen calibration] --> I[Mouse coordinates]
    G --> J[Automated swipe playback]
    I --> J
```

For each tile, the solver walks horizontally, vertically, and diagonally through unvisited neighbors. The trie makes this practical by stopping a branch immediately when the current letters cannot begin any dictionary word. Every completed word is stored alongside the exact tile path needed to play it.

## Architecture

| File | Responsibility |
| --- | --- |
| [`main.py`](main.py) | Opens the terminal menu for running the bot or calibrating. |
| [`main.py`](src/wordgames_bot/main.py) | Coordinates board input, solving, timing, sorting, and playback. |
| [`solver.py`](src/wordgames_bot/solver.py) | Implements board parsing, DFS search, and the optional Ollama vision experiment. |
| [`trie.py`](src/wordgames_bot/trie.py) | Loads the dictionary into a compact prefix trie for word and prefix lookup. |
| [`screen.py`](src/wordgames_bot/screen.py) | Stores calibration, captures the board, and translates paths into mouse movement. |
| [`calibration.py`](src/wordgames_bot/calibration.py) | Provides the interactive calibration entry point. |
| [`paths.py`](src/wordgames_bot/paths.py) | Centralizes paths to data, configuration, and captured images. |

### Repository layout

```text
WordGames_Bot/
├── src/wordgames_bot/  # Application package
├── data/               # Dictionary and vision prompt
├── config/             # Calibration and game configuration
├── images/             # Demo boards, captures, and crops
├── examples/           # Standalone usage examples
├── README.md            # Project overview
└── SETUP.md             # Installation and operation guide
```

## Getting started

Ready to take a word game a little too seriously? Start here:

```bash
uv sync
uv run main.py
```

Choose **Calibrate board** on your first run, then **Run bot**. Calibration only needs the centers of the top-left and bottom-right cells; the remaining cell centers are calculated automatically for an evenly spaced grid. The menu returns after each action. You can also open it with `uv run python -m wordgames_bot`.

After entering the board, press **Q** to stop the bot, even while the game window is focused. This works during the countdown, solving, and mouse playback; an active drag is released before returning to the menu.

Each run prompts for **Slow, Normal, or Fast** playback and **Highest first (longest words), Lowest first (shortest words), or Random** word order. Press Enter at both prompts to use normal speed and longest words first. Each word is played only once, even if it can be formed along multiple tile paths.

Calibration is machine- and window-position-specific. On macOS, the terminal or IDE running the bot also needs Accessibility permission for mouse control; screenshot capture additionally needs Screen Recording permission.

See [SETUP.md](SETUP.md) for installation, calibration, input format, optional screenshot extraction, and troubleshooting.

## Current scope

- The active game path targets a 4×4 board.
- Board letters are entered manually in the default runner at `src/wordgames_bot/main.py`.
- Playback stops after roughly 70 seconds to avoid running beyond a game round.
- Calibration data is tied to the current screen layout and must be regenerated when the board moves or resizes.
- Screenshot-to-grid extraction exists as an optional local-model experiment and is not enabled in the default runner.

