from wordgames_bot.solver import WordHuntBot, manual_board_input


def main() -> None:
    board = manual_board_input()
    bot = WordHuntBot(board)
    bot.solve()

    word_path_pairs = bot.get_found_words(sorted_max_len=True)
    for word, path in word_path_pairs:
        print(f"Word: {word}")


if __name__ == "__main__":
    main()
