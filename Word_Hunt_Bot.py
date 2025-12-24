from Dictionary_Trie import DictionaryTrie

import json
from pathlib import Path
from ollama import chat
from PIL import Image

def Ollama_Test():
    model_name = "qwen3-vl:8b"
    ollama_response = chat(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
    )
    print(ollama_response['message']['content'])


def image_to_board(image_path: str) -> list[list[str]]: 
    model_name = "qwen3-vl:4b"
    # Read from this current dir path @ propmpt.txt
    prompt_path = Path(__file__).with_name("prompt.txt")
    with open(prompt_path, "r") as f:
        prompt = f.read()
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
        ]
    )
    board_str = ollama_response['message']['content']
    print("Ollama Response:")
    print(board_str)
    ### String is json format like:
    #{
    #"grid": [
    #["a","b","c","d"],
    #["e","f","g","h"],
    #["i","j","k","l"],
    #["m","n","o","p"]
    #]
    #j}
     ###
    board_json = json.loads(board_str)
    board = board_json["grid"]  
    print("Extracted Board from Image:")
    for row in board:
        print(" ".join(row))    
    return board

class Word_Hunt_Bot:
    def __init__(self, board: list[list[str]]):
        self.trie = DictionaryTrie(str(Path(__file__).with_name("enable1.txt")))
        self.found_words : list[tuple[str, list[tuple[int, int]]]] =  []
        self.board_size = 4
        self.board = board


    def solve(self) -> None:
        # Board is 4x4 2d char array
        for i in range(self.board_size):
            for j in range(self.board_size):
                visited = []
                self.dfs(i, j, "", visited)
    def dfs(self, x: int, y: int, current_word: str, visited: list[tuple[int, int]]) -> None:    
        directions = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1),          (0, 1),
                    (1, -1),  (1, 0), (1, 1)]
    
        visited.append((x, y))
        current_word += self.board[x][y]

        if not self.trie.is_prefix(current_word):
            visited.remove((x, y))
            return

        if self.trie.is_word(current_word):
            self.found_words.append((current_word, visited.copy()))

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.is_valid(new_x, new_y, visited):
                self.dfs(new_x, new_y, current_word, visited)

        visited.remove((x, y))

    def is_valid(self, x: int, y: int, visited: list[tuple[int, int]]) -> bool:
        return  0 <= x < self.board_size and \
                0 <= y < self.board_size and \
                (x, y) not in visited
    def get_found_words(self, sorted_max_len= True) -> list[tuple[str, list[tuple[int, int]]]]:
        if sorted_max_len:
            return sorted(self.found_words, key=lambda item: (-len(item[0]), item[0]))
        else:
            return  self.found_words.copy()
        
if __name__ == "__main__":
    import time
    start_time = time.time()
    image_path = str(Path(__file__).with_name("board.png"))
    board = image_to_board(image_path=image_path)

    print("Board:")
    for row in board:
        print(" ".join(row))

    bot = Word_Hunt_Bot(board)
    bot.solve()

    # Sort by word length desc, then word asc.
    words_path_pairs = sorted({w for w, _ in bot.found_words}, key=lambda w: (-len(w), w))
    paths = []
    words = []
    for w, path in bot.get_found_words(sorted_max_len=True):
        paths.append((w, path))
        words.append(w)
    unique_words = sorted(set(words), key=lambda w: (-len(w), w))

    print(f"\nFound {len(paths)} word paths")
    print(f"Unique words: {len(unique_words)}")

    print("Top 25 unique words (longest first):")
    for w in unique_words[:25]:
        print(w)

    print("\nTop 10 paths (word -> coordinates):")
    for w, path in paths[:10]:
        print(f"{w} -> {path}")
    print(len(paths))

    end_time = time.time()
    print(f"Image to board extraction took {end_time - start_time:.2f} seconds.")


    