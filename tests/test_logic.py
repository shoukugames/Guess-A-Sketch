import random
import unittest

from guess_a_sketch import drawings, logic


class LogicTests(unittest.TestCase):
    def game(self, diff="Easy", level=1, seed=1):
        return logic.Game(diff, level, random.Random(seed))

    def test_word_lengths_and_timer(self):
        for lv in range(1, 15):
            g = self.game(level=lv)
            self.assertEqual(len(g.word), min(lv + 1, 10))
            self.assertEqual(g.time_limit, 60.0 if lv >= 9 else 99.0)

    def test_every_length_has_words_for_every_difficulty(self):
        for lv in range(1, 12):
            for d in logic.DIFFICULTIES:
                self.assertTrue(logic.pick_word(lv, d, set()))

    def test_all_drawings_have_six_stages(self):
        for w, d in drawings.WORDS.items():
            n = len(d["prims"])
            self.assertEqual({drawings.stage_of(i, n) for i in range(n)}, set(range(6)), w)

    def test_five_wrong_guesses_lose(self):
        g = self.game(level=3)
        wrong = [c for c in "ZQXJVKWY" if c not in g.word][:5]
        results = [g.guess(c) for c in wrong]
        self.assertEqual(results[:4], ["wrong"] * 4)
        self.assertEqual(results[4], "lost")
        self.assertEqual(g.lose_reason, "chances")

    def test_repeat_does_not_cost(self):
        g = self.game(level=3)
        c = next(c for c in "ZQXJ" if c not in g.word)
        g.guess(c)
        self.assertEqual(g.guess(c), "repeat")
        self.assertEqual(g.chances, 4)

    def test_win_scores_time_left(self):
        g = self.game("Hard", 2)
        g.tick(9.5)
        res = [g.guess(c) for c in sorted(set(g.word))]
        self.assertEqual(res[-1], "won")
        self.assertEqual(g.last_points, 90 * 10 * 3)

    def test_timeout(self):
        g = self.game()
        self.assertEqual(g.tick(100), "timeout")
        self.assertEqual(g.state, "lost")

    def test_hints_limited_per_game(self):
        g = self.game(level=9)
        used = 0
        while g.use_hint():
            used += 1
            if g.state == "won":
                g.advance()
        self.assertEqual(used, 3)
        self.assertEqual(g.hints_left, 0)

    def test_level_up_after_three_words(self):
        g = self.game(level=1)
        for i in range(3):
            for c in set(g.word):
                g.guess(c)
            r = g.advance()
        self.assertEqual(r, "level_up")
        self.assertEqual(g.level, 2)
        g.start_next_level()
        self.assertEqual(len(g.word), 3)

    def test_session_record(self):
        g = self.game(level=4)
        for c in "ZQXJVKWY":
            if g.state == "playing" and c not in g.word:
                g.guess(c)
        r = g.session_record()
        self.assertEqual(r["failed_word"], g.word)
        self.assertEqual(r["failed_level"], 4)
        self.assertEqual(r["result"], "Out of chances")


if __name__ == "__main__":
    unittest.main()


class I18nTests(unittest.TestCase):
    def test_every_word_has_japanese_name(self):
        from guess_a_sketch import i18n
        missing = [w for w in drawings.WORDS if not i18n.JA_NAMES.get(w)]
        self.assertEqual(missing, [])

    def test_both_languages_have_same_keys(self):
        from guess_a_sketch import i18n
        self.assertEqual(set(i18n.STRINGS["en"]), set(i18n.STRINGS["ja"]))

    def test_format_strings_match(self):
        from guess_a_sketch import i18n
        for k, en in i18n.STRINGS["en"].items():
            if isinstance(en, str):
                ja = i18n.STRINGS["ja"][k]
                self.assertEqual(en.count("%"), ja.count("%"), k)

    def test_translate_and_duration(self):
        from guess_a_sketch import i18n
        try:
            i18n.set_lang("ja")
            self.assertEqual(i18n.T("level", 3), "レベル 3")
            self.assertEqual(i18n.duration(125), "2分05秒")
            self.assertEqual(i18n.word_label("CAT"), "CAT（ねこ）")
            for r in ("Quit", "Time ran out", "Out of chances"):
                self.assertNotEqual(i18n.T("res_" + r), "res_" + r)
            i18n.set_lang("en")
            self.assertEqual(i18n.duration(125), "2m 05s")
            self.assertEqual(i18n.word_label("CAT"), "CAT")
        finally:
            i18n.set_lang("en")
