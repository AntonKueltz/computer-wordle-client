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

    def partial_matches(self, known_values: List[Tuple[int, str]]):
        matches = []

        for word in self.candidates:
            if all([word[i] == c for (i, c) in known_values]):
                matches.append(word)

        self.candidates = matches

    def known_letters_at_different_index(self, known_letters: Dict[str, List[int]]):
        matches = []

        for word in self.candidates:
            for letter, indices in known_letters.items():
                if letter not in word:
                    break
                if any([word[i] == letter for i in indices]):
                    break
            else:
                matches.append(word)

        self.candidates = matches

    def remove_known_invalid_words(self, known_invalid_letters: Set[str]):
        matches = []

        for word in self.candidates:
            if not any([letter in word for letter in known_invalid_letters]):
                matches.append(word)

        self.candidates = matches

    def top_frequencies(self, length: int) -> List[str]:
        words = [w for w in self.candidates if len(w) == length]
        counter = Counter()

        for word in words:
            for letter in word:
                counter[letter] += 1

        return [letter for (letter, count) in counter.most_common()]


def main():
    game = computer_wordle.Game()

    while game.current_hint() is not None:
        solver = Solver(len(game.current_hint()))

        known_letters: List[Tuple[int, str]] = []
        invalid_letters: Set[str] = set()
        partial_matches: Dict[str, List[int]] = defaultdict(list)

        while True:
            guess_word = random.choice(solver.candidates)
            response = game.guess(guess_word)
            guess_response = response['guess_response']
            print(f"{guess_word} -> {guess_response}")

            if 'next_hint' in response.keys():
                # Solved the word, on to the next one!
                print(f"SOLVED! Target word = {guess_word}")
                break

            for i, clue in enumerate(guess_response):
                letter = guess_word[i]

                if clue == computer_wordle.GRAY:
                    if (
                            letter not in partial_matches and
                            letter not in {c for (_, c) in known_letters}
                    ):
                        invalid_letters.add(letter)

                if clue == computer_wordle.GREEN:
                    known_letters.append((i, letter))
                    if letter in partial_matches:
                        del partial_matches[letter]
                    if letter in invalid_letters:
                        invalid_letters.remove(letter)

                if clue == computer_wordle.YELLOW:
                    partial_matches[letter].append(i)

            solver.remove_known_invalid_words(invalid_letters)
            solver.partial_matches(known_letters)
            solver.known_letters_at_different_index(partial_matches)

    webbrowser.open(game.url())


if __name__ == '__main__':
    main()
