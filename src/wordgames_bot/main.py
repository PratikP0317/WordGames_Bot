import time
from threading import Event

from .paths import DEFAULT_CALIBRATION_PATH
from .screen import CalibrationConfig, trace_word_path
from .solver import WordHuntBot, manual_board_input


SPEEDS = {
    "1": ("Slow", 0.35, 0.15, 0.8),
    "2": ("Normal", 0.2, 0.08, 0.5),
    "3": ("Fast", 0.1, 0.04, 0.15),
}
ORDERS = {"1": "longest", "2": "shortest", "3": "random"}


def choose_playback_options() -> tuple[tuple[str, float, float, float], str]:
    print("\nPlayback speed: 1. Slow  2. Normal  3. Fast")
    while True:
        speed = input("Choose speed [1/2/3, Enter = Normal]: ").strip() or "2"
        if speed in SPEEDS:
            break
        print("Please choose 1, 2, or 3.")
    print("Word order: 1. Highest first (longest)  2. Lowest first (shortest)  3. Random")
    while True:
        order = input("Choose order [1/2/3, Enter = Highest first]: ").strip() or "1"
        if order in ORDERS:
            return SPEEDS[speed], ORDERS[order]
        print("Please choose 1, 2, or 3.")


def main() -> None:
    from pynput import keyboard

    config = CalibrationConfig.load_json(DEFAULT_CALIBRATION_PATH)
    if not config.is_complete() or config.grid_size != 4:
        raise ValueError("Run calibration first to save a complete 4x4 grid.")
    (speed_name, start_delay, step_delay, word_delay), order = choose_playback_options()
    print(f"Using {speed_name.lower()} speed and {order} word order.")
    board = manual_board_input()
    stop_event = Event()

    def on_press(key):
        if getattr(key, "char", None) in {"q", "Q"}:
            stop_event.set()
            return False

    print("Press Q at any time to stop the bot.")
    with keyboard.Listener(on_press=on_press):
        try:
            for remaining in (3, 2, 1):
                print(remaining)
                if stop_event.wait(1):
                    return
            print("Go!")
            start_time = time.time()

            bot = WordHuntBot(board)
            if stop_event.is_set():
                return
            bot.solve(stop_event=stop_event)
            if stop_event.is_set():
                return

            elapsed_time = time.time() - start_time
            print(f"Solved after: {elapsed_time:.2f} seconds")

            word_path_pairs = bot.get_found_words(order=order)
            for word, path in word_path_pairs:
                if stop_event.is_set():
                    break
                print(f"Word: {word}")
                trace_word_path(
                    path, config, stop_event=stop_event,
                    start_delay=start_delay, step_delay=step_delay,
                )
                if stop_event.wait(word_delay):
                    break
                if time.time() - start_time > 70:
                    print("Stopping tracing to avoid long execution.")
                    break
        finally:
            if stop_event.is_set():
                print("Bot stopped.")


if __name__ == "__main__":
    main()
