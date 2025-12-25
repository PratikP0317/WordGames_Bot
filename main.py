from pathlib import Path
from Screen_Stuff import take_screenshot, CalibrationConfig, trace_word_path
from Word_Hunt_Bot import Word_Hunt_Bot, llm_image_to_board, manuel_board_input
import time


def main():
    config = CalibrationConfig.load_json("./calibration.json")
    #take_screenshot(config)
    #image_path = str(Path(__file__).with_name("curr_board.png"))
    #board = llm_image_to_board(image_path=image_path)

    board = manuel_board_input()

    # countdown timer
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)
    time.sleep(1)
    print("Go!")
    start_time = time.time()

    bot = Word_Hunt_Bot(board)
    bot.solve()

    elapsed_time = time.time() - start_time
    print(f"Solved after: {elapsed_time:.2f} seconds")

    word_path_pairs = bot.get_found_words(sorted_max_len=True)
    for word, path in word_path_pairs:
        print(f"Word: {word}")
        trace_word_path(path, config)
        if time.time() - start_time > 70:
            print("Stopping tracing to avoid long execution.")
            break
    


    


    



if __name__ == "__main__":
    main()
