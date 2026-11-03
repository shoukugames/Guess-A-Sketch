"""Pure game rules (no pygame) so they are easy to test."""

import math
import random
import time

from . import drawings

DIFFICULTIES = ("Easy", "Medium", "Hard")
SCORE_MULT = {"Easy": 1, "Medium": 2, "Hard": 3}
WORDS_PER_LEVEL = 3
MAX_CHANCES = 5
HINTS_PER_GAME = 3
MAX_LETTERS = 10
EXPERT_LEVEL = MAX_LETTERS - 1   # level 9 is the first 10-letter level


def word_length(level):
    return min(level + 1, MAX_LETTERS)


def time_limit(level):
    return 60.0 if word_length(level) >= MAX_LETTERS else 99.0


def allowed_tiers(level, difficulty):
    base = {"Easy": (1,), "Medium": (1, 2), "Hard": (2, 3)}[difficulty]
    if level > EXPERT_LEVEL:  # beyond the first 10-letter level: harder still
        base = {"Easy": (1, 2), "Medium": (2, 3), "Hard": (3,)}[difficulty]
    return base


def pick_word(level, difficulty, used, rng=random):
    pool = drawings.words_of_length(word_length(level))
    tiers = allowed_tiers(level, difficulty)
    for cands in (
        [w for w in pool if drawings.WORDS[w]["tier"] in tiers and w not in used],
        [w for w in pool if w not in used],
        [w for w in pool if drawings.WORDS[w]["tier"] in tiers],
        pool,
    ):
        if cands:
            return rng.choice(sorted(cands))
    raise RuntimeError("no words of length %d" % word_length(level))


class Game:
    def __init__(self, difficulty="Easy", start_level=1, rng=None):
        self.rng = rng or random.Random()
        self.difficulty = difficulty
        self.start_level = start_level
        self.level = start_level
        self.word_in_level = 0          # 0..WORDS_PER_LEVEL-1
        self.score = 0
        self.hints_left = HINTS_PER_GAME
        self.hints_used = 0
        self.words_solved = 0
        self.used = set()
        self.started_at = time.strftime("%Y-%m-%d %H:%M")
        self.elapsed = 0.0              # seconds of actual play
        self.last_points = 0
        self.lose_reason = None
        self.new_word()

    # ------------------------------------------------------------ word flow
    def new_word(self):
        self.word = pick_word(self.level, self.difficulty, self.used, self.rng)
        self.used.add(self.word)
        self.guessed = set()
        self.wrong = []
        self.chances = MAX_CHANCES
        self.time_limit = time_limit(self.level)
        self.time_left = self.time_limit
        self.state = "playing"

    @property
    def wrong_count(self):
        return MAX_CHANCES - self.chances

    def is_revealed(self, ch):
        return ch in self.guessed

    @property
    def solved(self):
        return all(c in self.guessed for c in self.word)

    def guess(self, letter):
        """Returns 'correct', 'wrong', 'repeat', 'won', 'lost' or None."""
        if self.state != "playing":
            return None
        letter = letter.upper()
        if len(letter) != 1 or not ("A" <= letter <= "Z"):
            return None
        if letter in self.guessed or letter in self.wrong:
            return "repeat"
        if letter in self.word:
            self.guessed.add(letter)
            if self.solved:
                self._win()
                return "won"
            return "correct"
        self.wrong.append(letter)
        self.chances -= 1
        if self.chances <= 0:
            self._lose("chances")
            return "lost"
        return "wrong"

    def use_hint(self):
        if self.state != "playing" or self.hints_left <= 0:
            return None
        hidden = sorted(set(c for c in self.word if c not in self.guessed))
        if not hidden:
            return None
        letter = self.rng.choice(hidden)
        self.hints_left -= 1
        self.hints_used += 1
        self.guessed.add(letter)
        if self.solved:
            self._win()
        return letter

    def tick(self, dt):
        self.elapsed += dt
        if self.state == "playing":
            self.time_left = max(0.0, self.time_left - dt)
            if self.time_left <= 0:
                self._lose("time")
                return "timeout"
        return None

    def _win(self):
        self.state = "won"
        self.words_solved += 1
        self.last_points = int(math.ceil(self.time_left)) * 10 * SCORE_MULT[self.difficulty]
        self.score += self.last_points

    def _lose(self, reason):
        self.state = "lost"
        self.lose_reason = reason

    def advance(self):
        """After a won word. Returns 'next_word' or 'level_up'."""
        self.word_in_level += 1
        if self.word_in_level >= WORDS_PER_LEVEL:
            self.level += 1
            self.word_in_level = 0
            return "level_up"
        self.new_word()
        return "next_word"

    def start_next_level(self):
        self.new_word()

    # ------------------------------------------------------------ reporting
    def session_record(self, quit_=False):
        if quit_:
            result = "Quit"
        elif self.lose_reason == "time":
            result = "Time ran out"
        else:
            result = "Out of chances"
        failed = None if quit_ else self.word
        return {
            "started_at": self.started_at,
            "duration_sec": int(round(self.elapsed)),
            "score": self.score,
            "difficulty": self.difficulty,
            "start_level": self.start_level,
            "level_reached": self.level,
            "words_solved": self.words_solved,
            "hints_used": self.hints_used,
            "result": result,
            "failed_word": failed,
            "failed_level": None if quit_ else self.level,
        }
