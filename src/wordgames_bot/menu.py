"""Small terminal menu for the bot and calibration."""

from .paths import DEFAULT_CALIBRATION_PATH


def main() -> None:
    while True:
        print("\n=== Word Hunt Bot ===")
        print("1. Run bot")
        print("2. Calibrate board")
        print("3. Quit")
        try:
            choice = input("Choose [1/2/3]: ").strip().lower()
            if choice in {"3", "q", "quit"}:
                return
            if choice == "1":
                if not DEFAULT_CALIBRATION_PATH.exists():
                    print("Calibrate your board first (option 2).")
                    continue
                from .main import main as run_bot

                run_bot()
            elif choice == "2":
                from .calibration import main as calibrate

                calibrate()
            else:
                print("Please choose 1, 2, or 3.")
        except EOFError:
            print()
            return
        except KeyboardInterrupt:
            print("\nInterrupted. Returning to menu.")
        except (OSError, ValueError, RuntimeError) as error:
            print(f"{error}")
