import json
import random
from pathlib import Path
from threading import Event

from ollama import chat

from .paths import DEFAULT_DICTIONARY_PATH, DEFAULT_PROMPT_PATH
from .trie import DictionaryTrie


def ollama_test() -> None:
    model_name = "qwen3-vl:8b"
    ollama_response = chat(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
        ],
    )
    print(ollama_response["message"]["content"])


def llm_image_to_board(image_path: str | Path) -> list[list[str]]:
    model_name = "qwen3-vl:4b"
    prompt = DEFAULT_PROMPT_PATH.read_text(encoding="utf-8")
    img_bytes = Path(image_path).read_bytes()
    print("Sending image to Ollama for board extraction...")
    ollama_response = chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [img_bytes],
            }
        ],
    )
    board_str = ollama_response["message"]["content"]
    print("Ollama Response:")
    print(board_str)
    board_json = json.loads(board_str)
    board = board_json["grid"]
    print("Extracted Board from Image:")
    for row in board:
        print(" ".join(row))
    return board


def manual_board_input() -> list[list[str]]:
    print(
        "Please input single string of 16 letters (row-wise) for the 4x4 board (e.g., abcd efgh ijkl mnop):"
    )
    # just remove spaces when read in
    board_input = input().strip().replace(" ", "").lower()
    if len(board_input) != 16 or not board_input.isalpha():
        raise ValueError("Invalid board input. Please enter exactly 16 letters.")
    board = []
    for i in range(4):
        row = list(board_input[i * 4 : (i + 1) * 4])
        board.append(row)
    print("Manually Inputted Board:")
    for row in board:
        print(" ".join(row))
    return board


class WordHuntBot:
    def __init__(self, board: list[list[str]]):
        self.trie = DictionaryTrie(str(DEFAULT_DICTIONARY_PATH))
        self.found_words: list[tuple[str, list[tuple[int, int]]]] = []
        self._found_word_names: set[str] = set()
        self.board_size = 4
        self.board = board

    def solve(self, stop_event: Event | None = None) -> None:
        self.found_words.clear()
        self._found_word_names.clear()
        # Board is 4x4 2d char array
        for i in range(self.board_size):
            for j in range(self.board_size):
                if stop_event is not None and stop_event.is_set():
                    return
                visited = []
                self.dfs(i, j, "", visited, stop_event)

    def dfs(
        self, x: int, y: int, current_word: str, visited: list[tuple[int, int]],
        stop_event: Event | None = None,
    ) -> None:
        if stop_event is not None and stop_event.is_set():
            return
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        visited.append((x, y))
        current_word += self.board[x][y]

        if not self.trie.is_prefix(current_word):
            visited.remove((x, y))
            return

        if current_word not in self._found_word_names and self.trie.is_word(current_word):
            self._found_word_names.add(current_word)
            self.found_words.append((current_word, visited.copy()))

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.is_valid(new_x, new_y, visited):
                self.dfs(new_x, new_y, current_word, visited, stop_event)

        visited.remove((x, y))

    def is_valid(self, x: int, y: int, visited: list[tuple[int, int]]) -> bool:
        return (
            0 <= x < self.board_size
            and 0 <= y < self.board_size
            and (x, y) not in visited
        )

    def get_found_words(
        self, sorted_max_len=True, *, order: str | None = None,
    ) -> list[tuple[str, list[tuple[int, int]]]]:
        words = self.found_words.copy()
        if order is None:
            order = "longest" if sorted_max_len else "discovery"
        if order == "longest":
            return sorted(words, key=lambda item: (-len(item[0]), item[0]))
        if order == "shortest":
            return sorted(words, key=lambda item: (len(item[0]), item[0]))
        if order == "random":
            random.shuffle(words)
            return words
        if order == "discovery":
            return words
        raise ValueError(f"Unknown word order: {order}")


if __name__ == "__main__":
    bot = WordHuntBot(manual_board_input())
    bot.solve()
    for found_word, found_path in bot.get_found_words():
        print(f"{found_word}: {found_path}")
