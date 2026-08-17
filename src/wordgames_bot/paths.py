"""Shared paths for the repository's data, configuration, and image assets."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
IMAGES_DIR = PROJECT_ROOT / "images"

DEFAULT_DICTIONARY_PATH = DATA_DIR / "enable1.txt"
DEFAULT_PROMPT_PATH = DATA_DIR / "board_extraction_prompt.txt"
DEFAULT_CALIBRATION_PATH = CONFIG_DIR / "calibration.json"
DEFAULT_CAPTURE_PATH = IMAGES_DIR / "captures" / "curr_board.png"
