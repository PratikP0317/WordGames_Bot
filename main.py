"""Launch the terminal menu directly from the repository."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from wordgames_bot.menu import main


if __name__ == "__main__":
    main()
