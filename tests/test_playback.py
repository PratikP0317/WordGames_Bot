import unittest
from unittest.mock import Mock, patch

from wordgames_bot.main import SPEEDS, choose_playback_options
from wordgames_bot.solver import WordHuntBot


class PlaybackTests(unittest.TestCase):
    def make_bot(self):
        words = {"aaa", "aaaa"}
        trie = Mock()
        trie.is_prefix.side_effect = lambda word: any(w.startswith(word) for w in words)
        trie.is_word.side_effect = lambda word: word in words
        with patch("wordgames_bot.solver.DictionaryTrie", return_value=trie):
            return WordHuntBot([list("aaaa")] * 4)

    def test_multiple_paths_and_repeated_solves_do_not_duplicate_words(self):
        bot = self.make_bot()
        for _ in range(2):
            bot.solve()
            results = bot.get_found_words()
            self.assertEqual([word for word, path in results], ["aaaa", "aaa"])
            for word, path in results:
                self.assertEqual(len(path), len(word))
                self.assertEqual(len(set(path)), len(path))
                for (r, c), (nr, nc) in zip(path, path[1:]):
                    self.assertLessEqual(max(abs(r - nr), abs(c - nc)), 1)

    def test_orders_and_random_do_not_mutate_stored_results(self):
        bot = self.make_bot()
        bot.solve()
        original = bot.found_words.copy()
        self.assertEqual([w for w, _ in bot.get_found_words(order="shortest")], ["aaa", "aaaa"])
        self.assertEqual([w for w, _ in bot.get_found_words(order="longest")], ["aaaa", "aaa"])
        with patch("wordgames_bot.solver.random.shuffle", side_effect=lambda words: words.reverse()) as shuffle:
            results = bot.get_found_words(order="random")
        shuffle.assert_called_once()
        self.assertEqual(results, original[::-1])
        self.assertEqual(bot.found_words, original)

    def test_option_defaults(self):
        with patch("builtins.input", side_effect=["", ""]), patch("builtins.print"):
            self.assertEqual(choose_playback_options(), (SPEEDS["2"], "longest"))

    def test_invalid_options_retry_and_select_fast_random(self):
        with patch("builtins.input", side_effect=["bad", "3", "4", "3"]), patch("builtins.print"):
            self.assertEqual(choose_playback_options(), (SPEEDS["3"], "random"))
