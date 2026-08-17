import time

from .paths import DEFAULT_CALIBRATION_PATH
from .screen import CalibrationConfig, trace_word_path
from .solver import WordHuntBot, manual_board_input


def main() -> None:
    config = CalibrationConfig.load_json(DEFAULT_CALIBRATION_PATH)
    board = manual_board_input()

    # countdown timer
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)
    time.sleep(1)
    print("Go!")
    start_time = time.time()

    bot = WordHuntBot(board)
    bot.solve()

    elapsed_time = time.time() - start_time
    print(f"Solved after: {elapsed_time:.2f} seconds")

    delay = 0.5  # Adjust this value to control the delay between tracing each word

    word_path_pairs = bot.get_found_words(sorted_max_len=True)
    for word, path in word_path_pairs:
        print(f"Word: {word}")
        trace_word_path(path, config)
        time.sleep(delay)  # Add delay between tracing each word
        if time.time() - start_time > 70:
            print("Stopping tracing to avoid long execution.")
            break


if __name__ == "__main__":
    main()
