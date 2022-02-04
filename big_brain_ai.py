#!/usr/bin/env python3

from collections import Counter, defaultdict
import computer_wordle
import random
from typing import Dict, List, Set, Tuple
import webbrowser


class Solver:
    def __init__(self, length):
        self.length = length
        self.candidates = [w for w in computer_wordle.wordlist if len(w) == length]

        self.green_letters: List[Tuple[int, str]] = []
        self.gray_letters: Set[str] = set()
        self.yellow_letters: Dict[str, List[int]] = defaultdict(list)

    def partial_matches(self):
        matches = []

        for word in self.candidates:
            if all([word[i] == c for (i, c) in self.green_letters]):
                matches.append(word)

        self.candidates = matches

    def known_letters_at_different_index(self):
        matches = []

        for word in self.candidates:
            for letter, indices in self.yellow_letters.items():
                if letter not in word:
                    break
                if any([word[i] == letter for i in indices]):
                    break
            else:
                matches.append(word)

        self.candidates = matches

    def remove_known_invalid_words(self):
        matches = []

        for word in self.candidates:
            if not any([letter in word for letter in self.gray_letters]):
                matches.append(word)

        self.candidates = matches

    def update_with_round_results(self, guess_word: str, guess_response: str):
        self.candidates.remove(guess_word)

        for i, clue in enumerate(guess_response):
            letter = guess_word[i]

            if clue == computer_wordle.GRAY:
                if (
                        letter not in self.yellow_letters and
                        letter not in {c for (_, c) in self.green_letters}
                ):
                    self.gray_letters.add(letter)

            if clue == computer_wordle.GREEN:
                self.green_letters.append((i, letter))
                if letter in self.yellow_letters:
                    del self.yellow_letters[letter]
                if letter in self.gray_letters:
                    self.gray_letters.remove(letter)

            if clue == computer_wordle.YELLOW:
                self.yellow_letters[letter].append(i)

    def frequencies(self) -> Counter:
        words = [w for w in self.candidates if len(w) == self.length]
        counter = Counter()

        for word in words:
            for letter in word:
                counter[letter] += 1

        return counter

    def highest_score_word(self) -> str:
        frequencies = self.frequencies()
        best_word, best_score = None, 0

        for word in self.candidates:
            score = sum([frequencies[c] for c in set(word)])
            if score > best_score:
                best_word = word
                best_score = score

        return best_word


def main():
    game = computer_wordle.Game()

    while game.current_hint() is not None:
        solver = Solver(len(game.current_hint()))

        while True:
            guess_word = solver.highest_score_word()
            response = game.guess(guess_word)
            guess_response = response['guess_response']
            print(f"{guess_word} -> {guess_response}")

            if 'next_hint' in response.keys():
                # Solved the word, on to the next one!
                print(f"SOLVED! Target word = {guess_word}")
                break

            solver.update_with_round_results(guess_word, guess_response)
            solver.remove_known_invalid_words()
            solver.partial_matches()
            solver.known_letters_at_different_index()

    webbrowser.open(game.url())


if __name__ == '__main__':
    main()
