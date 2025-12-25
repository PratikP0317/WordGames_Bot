from __future__ import annotations


class DictionaryTrie:
    """Prefix trie for fast word/prefix checks (lowercase a-z only).

    Optimized for DFS-style board traversal:
    - Fixed-size child arrays (26) per node for quick transitions
    - Optional full word stored at terminal nodes to avoid rebuilding strings
    """
    class _Node:
        """Internal trie node."""

        __slots__ = ("children", "is_terminal", "word")

        def __init__(self) -> None:
            # children[i] holds the index of the next node for chr(ord('a') + i)
            # -1 means "no edge".
            self.children: list[int] = [-1] * 26
            self.is_terminal: bool = False
            self.word: str | None = None

    __slots__ = ("_nodes",)

    def __init__(self, word_list_path: str | None = None) -> None:
        # Node 0 is always the root.
        self._nodes: list[DictionaryTrie._Node] = [DictionaryTrie._Node()]

        # Optional convenience: build directly from a file with one word per line.
        if word_list_path is not None:
            with open(word_list_path, "r", encoding="utf-8") as f:
                for line in f:
                    self.insert(line.strip())

    @staticmethod
    def _is_valid_token(token: str) -> bool:
        """Return True iff token contains only lowercase a-z characters."""
        if not token:
            return False
        for ch in token:
            o = ord(ch)
            if o < 97 or o > 122:  # 'a'..'z'
                return False
        return True

    @staticmethod
    def _idx(ch: str) -> int:
        return ord(ch) - 97

    def insert(self, word: str) -> None:
        """Insert a word into the trie (ignores words shorter than 3)."""
        if not word:
            return

        word = word.strip().lower()
        if len(word) < 3:
            return
        if not self._is_valid_token(word):
            return

        node_index = 0
        for ch in word:
            child_slot = self._idx(ch)
            next_index = self._nodes[node_index].children[child_slot]
            if next_index == -1:
                next_index = len(self._nodes)
                self._nodes[node_index].children[child_slot] = next_index
                self._nodes.append(DictionaryTrie._Node())
            node_index = next_index

        terminal = self._nodes[node_index]
        terminal.is_terminal = True
        terminal.word = word

    def is_word(self, word: str) -> bool:
        """Return True if word exists in the trie."""
        if not word:
            return False

        word = word.strip().lower()
        if len(word) < 3:
            return False
        if not self._is_valid_token(word):
            return False

        node_index = 0
        for ch in word:
            next_index = self._nodes[node_index].children[self._idx(ch)]
            if next_index == -1:
                return False
            node_index = next_index

        return self._nodes[node_index].is_terminal

    def is_prefix(self, prefix: str) -> bool:
        """Return True if prefix is a prefix of any inserted word."""
        if prefix is None:
            return False

        prefix = prefix.strip().lower()
        if prefix == "":
            return True
        if not self._is_valid_token(prefix):
            return False

        node_index = 0
        for ch in prefix:
            next_index = self._nodes[node_index].children[self._idx(ch)]
            if next_index == -1:
                return False
            node_index = next_index

        return True


def main() -> None:
    """Small demonstration of building and querying the trie."""
    from pathlib import Path

    # Prefer loading the real word list if it's available next to this file.
    word_list = Path(__file__).with_name("enable1.txt")
    if word_list.exists():
        trie = DictionaryTrie(str(word_list))
        print(f"Loaded trie from {word_list.name}")
    else:
        trie = DictionaryTrie()
        for w in ("eat", "ear", "ears", "eaten", "tea", "tear", "rate"):
            trie.insert(w)
        print("Loaded trie from a small in-code sample word list")

    # Prefix checks (useful during DFS traversal).
    for p in ("e", "ea", "ear", "ears", "eas", "z"):
        print(f"is_prefix({p!r}) -> {trie.is_prefix(p)}")

    # Whole-word checks.
    for w in ("ear", "ears", "e", "at", "rate", "rates"):
        print(f"is_word({w!r}) -> {trie.is_word(w)}")


if __name__ == "__main__":
    main()
