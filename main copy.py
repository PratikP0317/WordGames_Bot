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

    bot = Word_Hunt_Bot(board)
    bot.solve()

    word_path_pairs = bot.get_found_words(sorted_max_len=True)
    for word, path in word_path_pairs:
        print(f"Word: {word}")
    
    



if __name__ == "__main__":
    main()
