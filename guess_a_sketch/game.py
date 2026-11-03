"""Guess-A-Sketch: pygame front end (scenes, layout, window scaling)."""

import math
import os
import random
import sys
import webbrowser

import pygame

from . import drawings, logic, version
from .audio import Audio
from .progress import Progress, fmt_duration
from .sketch import Sketch

W, H = 1280, 720          # logical resolution; the window scales this
FPS = 60

INK = (44, 48, 72)
SOFT_INK = (98, 104, 130)
PAPER = (255, 252, 240)
ACCENT = (255, 128, 64)
GOOD = (76, 186, 110)
BAD = (232, 86, 86)
BLUEBTN = (86, 140, 236)
PURPLEBTN = (150, 110, 220)
GOLD = (246, 196, 60)
LETTERBOX = (24, 26, 40)


def resource_path(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, *parts)


# ====================================================================== text
class Fonts:
    def __init__(self):
        self.path = resource_path("assets", "fonts", "freesansbold.ttf")
        self._fonts = {}
        self._cache = {}

    def font(self, size):
        if size not in self._fonts:
            try:
                self._fonts[size] = pygame.font.Font(self.path, size)
            except (OSError, FileNotFoundError):
                self._fonts[size] = pygame.font.Font(None, int(size * 1.3))
        return self._fonts[size]

    def render(self, text, size, color):
        key = (text, size, color)
        surf = self._cache.get(key)
        if surf is None:
            if len(self._cache) > 600:
                self._cache.clear()
            surf = self.font(size).render(text, True, color)
            self._cache[key] = surf
        return surf


FONTS = None


def text(surf, s, size, color, pos, anchor="topleft", shadow=None):
    img = FONTS.render(s, size, color)
    r = img.get_rect(**{anchor: pos})
    if shadow:
        surf.blit(FONTS.render(s, size, shadow), r.move(2, 3))
    surf.blit(img, r)
    return r


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def heart_points(cx, cy, s):
    pts = []
    for i in range(40):
        t = 2 * math.pi * i / 40
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s, cy - y * s))
    return pts


def panel(surf, rect, color=(255, 255, 255), radius=22, border=INK, shadow=True):
    rect = pygame.Rect(rect)
    if shadow:
        sh = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 45), sh.get_rect(), border_radius=radius)
        surf.blit(sh, rect.move(4, 6))
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surf, border, rect, 3, border_radius=radius)


def paper_card(surf, rect):
    rect = pygame.Rect(rect)
    panel(surf, rect, PAPER, 18)
    for y in range(rect.top + 40, rect.bottom - 10, 32):
        pygame.draw.line(surf, (214, 228, 246), (rect.left + 12, y), (rect.right - 12, y), 1)
    pygame.draw.line(surf, (246, 190, 190), (rect.left + 46, rect.top + 8), (rect.left + 46, rect.bottom - 8), 2)


# ====================================================================== button
class Button:
    def __init__(self, rect, label, action, color=BLUEBTN, size=30, text_color=(255, 255, 255), sound="click"):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.color = color
        self.size = size
        self.text_color = text_color
        self.enabled = True
        self.selected = False
        self.visible = True
        self.sound = sound

    def draw(self, surf, mouse):
        if not self.visible:
            return
        hover = self.enabled and self.rect.collidepoint(mouse)
        base = self.color if self.enabled else (180, 182, 192)
        if self.selected:
            base = shade(base, 0.82)
        r = self.rect.move(0, -2 if hover else 0)
        pygame.draw.rect(surf, shade(base, 0.7), r.move(0, 5), border_radius=16)
        pygame.draw.rect(surf, shade(base, 1.12) if hover else base, r, border_radius=16)
        if self.selected:
            pygame.draw.rect(surf, (255, 255, 255), r.inflate(-6, -6), 3, border_radius=13)
        text(surf, self.label, self.size, self.text_color, r.center, "center")

    def hit(self, pos):
        return self.visible and self.enabled and self.rect.collidepoint(pos)


# ====================================================================== scenes
class Scene:
    music = "title"

    def __init__(self, app):
        self.app = app
        self.buttons = []

    def enter(self):
        self.app.audio.music(self.music)

    def on_click(self, pos):
        for b in self.buttons:
            if b.hit(pos):
                if b.sound:
                    self.app.audio.sfx(b.sound)
                b.action()
                return True
        return False

    def on_key(self, e):
        pass

    def update(self, dt):
        pass

    def draw(self, s):
        pass

    def draw_buttons(self, s):
        for b in self.buttons:
            b.draw(s, self.app.mouse)


# ---------------------------------------------------------------------- title
class TitleScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.showcase = None
        self.show_t = 0.0
        self.show_words = list(drawings.WORDS)
        random.shuffle(self.show_words)
        x = 720
        self.play_btn = Button((x, 200, 480, 78), "PLAY", self.start, ACCENT, 44)
        self.diff_btns = []
        for i, d in enumerate(logic.DIFFICULTIES):
            b = Button((x + i * 164, 330, 152, 56), d, lambda d=d: self.set_diff(d),
                       (GOOD, GOLD, BAD)[i], 26, INK if d == "Medium" else (255, 255, 255))
            self.diff_btns.append(b)
        self.lvl_down = Button((x, 432, 64, 56), "<", lambda: self.step_level(-1), BLUEBTN, 32)
        self.lvl_up = Button((x + 416, 432, 64, 56), ">", lambda: self.step_level(1), BLUEBTN, 32)
        self.buttons = [self.play_btn, *self.diff_btns, self.lvl_down, self.lvl_up,
                        Button((x, 520, 480, 56), "Parent Progress", lambda: app.go(ParentScene(app)), PURPLEBTN, 28),
                        Button((x, 588, 234, 56), "Credits", lambda: app.go(CreditsScene(app)), (90, 170, 190), 28),
                        Button((x + 246, 588, 234, 56), "Quit", app.quit, (130, 134, 150), 28)]
        self.refresh()
        self.next_showcase()

    def max_level(self):
        return max(10, self.app.progress.highest_level)

    def set_diff(self, d):
        self.app.settings["difficulty"] = d
        self.refresh()

    def step_level(self, k):
        lv = self.app.settings["start_level"] + k
        self.app.settings["start_level"] = max(1, min(self.max_level(), lv))
        self.refresh()

    def refresh(self):
        for b in self.diff_btns:
            b.selected = b.label == self.app.settings["difficulty"]
        lv = self.app.settings["start_level"]
        self.lvl_down.enabled = lv > 1
        self.lvl_up.enabled = lv < self.max_level()

    def start(self):
        self.app.go(PlayScene(self.app, logic.Game(self.app.settings["difficulty"], self.app.settings["start_level"])))

    def next_showcase(self):
        if not self.show_words:
            self.show_words = list(drawings.WORDS)
            random.shuffle(self.show_words)
        self.showcase = Sketch(self.show_words.pop())
        self.showcase.finish(colour=True, duration=2.6)
        self.show_t = 0.0

    def on_key(self, e):
        if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.app.audio.sfx("click")
            self.start()
        elif e.key == pygame.K_ESCAPE:
            self.app.quit()

    def update(self, dt):
        self.showcase.update(dt)
        if not self.showcase.animating:
            self.show_t += dt
            if self.show_t > 1.8:
                self.next_showcase()

    def draw(self, s):
        t = pygame.time.get_ticks() / 1000.0
        bob = math.sin(t * 2) * 4
        text(s, version.APP_NAME, 78, ACCENT, (W // 2, 70 + bob), "center", shadow=INK)
        text(s, "Spell the word before the sketch is finished!", 26, INK, (W // 2, 132), "center")
        # showcase card
        card = pygame.Rect(90, 180, 480, 480)
        paper_card(s, card)
        s.blit(self.showcase.render(420), (card.x + 30, card.y + 22))
        if self.showcase.color > 0.6:
            text(s, self.showcase.word, 34, INK, (card.centerx, card.bottom - 30), "center")
        # menu
        text(s, "Difficulty", 24, INK, (720, 300))
        mult = logic.SCORE_MULT[self.app.settings["difficulty"]]
        text(s, "points x%d" % mult, 22, SOFT_INK, (1200, 302), "topright")
        text(s, "Start level", 24, INK, (720, 402))
        lv = self.app.settings["start_level"]
        n = logic.word_length(lv)
        pygame.draw.rect(s, (255, 255, 255), (790, 432, 340, 56), border_radius=14)
        pygame.draw.rect(s, INK, (790, 432, 340, 56), 3, border_radius=14)
        label = "Level %d  -  %d letters" % (lv, n)
        text(s, label, 26, INK, (960, 460), "center")
        if lv >= logic.EXPERT_LEVEL:
            text(s, "Expert: 60-second timer", 20, BAD, (1200, 404), "topright")
        self.draw_buttons(s)
        text(s, "v%s  -  %s" % (version.VERSION, version.RELEASE_DATE_LONG), 18, SOFT_INK, (16, H - 12), "bottomleft")


# ---------------------------------------------------------------------- play
KEY_ROWS = ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")


class PlayScene(Scene):
    music = "play"

    def __init__(self, app, game):
        super().__init__(app)
        self.game = game
        self.phase = "play"     # play | won | lost | levelup | paused
        self.prev_phase = None
        self.phase_t = 0.0
        self.msg = ""
        self.msg_t = 0.0
        self.msg_color = INK
        self.shake = 0.0
        self.recorded = False
        self.keys = {}
        kw, gap, top = 56, 8, 352
        for r, row in enumerate(KEY_ROWS):
            width = len(row) * kw + (len(row) - 1) * gap
            x0 = 910 - width // 2
            for i, ch in enumerate(row):
                self.keys[ch] = pygame.Rect(x0 + i * (kw + gap), top + r * (kw + gap), kw, kw)
        self.hint_btn = Button((620, 590, 300, 66), "", self.use_hint, GOLD, 28, INK, sound=None)
        self.pause_btn = Button((940, 590, 270, 66), "Pause", self.pause, (130, 134, 150), 28)
        self.buttons = [self.hint_btn, self.pause_btn]
        # overlay buttons
        self.continue_btn = Button((W // 2 - 150, 470, 300, 66), "Continue", self.continue_level, ACCENT, 30)
        self.resume_btn = Button((W // 2 - 150, 330, 300, 66), "Resume", self.resume, GOOD, 30)
        self.quit_btn = Button((W // 2 - 150, 420, 300, 66), "Quit to Title", self.quit_to_title, BAD, 30)
        self.start_word()

    # ----------------------------------------------------------- flow
    def start_word(self):
        self.sketch = Sketch(self.game.word)
        self.sketch.show_stages(1, 1.2)
        self.phase = "play"
        self.phase_t = 0.0
        self.say("Level %d - word %d of %d" % (self.game.level, self.game.word_in_level + 1, logic.WORDS_PER_LEVEL), INK)

    def say(self, m, color=INK, t=2.2):
        self.msg, self.msg_color, self.msg_t = m, color, t

    def handle_result(self, res, letter):
        a = self.app.audio
        if res == "repeat":
            a.sfx("already")
            self.say("You already tried %s" % letter, SOFT_INK)
        elif res == "correct":
            a.sfx("correct")
            self.say(random.choice(("Nice!", "Good one!", "Yes!", "Great!")), GOOD, 1.2)
        elif res == "wrong":
            a.sfx("wrong")
            self.shake = 0.35
            self.sketch.show_stages(1 + self.game.wrong_count)
            left = self.game.chances
            self.say("No %s - %d chance%s left" % (letter, left, "" if left == 1 else "s"), BAD)
        elif res == "won":
            self.win()
        elif res == "lost":
            a.sfx("wrong")
            self.lose()

    def win(self):
        self.app.audio.sfx("win")
        self.app.audio.music("play")
        self.sketch.finish(colour=True, duration=1.0)
        self.phase, self.phase_t = "won", 0.0

    def lose(self):
        self.app.audio.stop_music()
        self.app.audio.sfx("lose")
        self.sketch.finish(colour=False, duration=0.8)
        self.phase, self.phase_t = "lost", 0.0

    def next_after_win(self):
        res = self.game.advance()
        if res == "level_up":
            self.app.audio.sfx("levelup")
            self.phase, self.phase_t = "levelup", 0.0
            self.app.progress.data["highest_level"] = max(self.app.progress.highest_level, self.game.level)
            self.app.progress.save()
        else:
            self.start_word()

    def continue_level(self):
        self.game.start_next_level()
        self.start_word()

    def to_game_over(self):
        self.record()
        self.app.go(GameOverScene(self.app, self.game, self.sketch))

    def record(self, quit_=False):
        if not self.recorded:
            self.recorded = True
            self.app.progress.record(self.game.session_record(quit_))

    def use_hint(self):
        if self.phase != "play":
            return
        letter = self.game.use_hint()
        if letter:
            self.app.audio.sfx("hint")
            self.say("Hint: the word has a %s" % letter, (200, 140, 0))
            if self.game.state == "won":
                self.win()
        else:
            self.app.audio.sfx("already")
            self.say("No hints left!", SOFT_INK)

    def pause(self):
        if self.phase in ("play", "won", "levelup"):
            self.prev_phase, self.phase = self.phase, "paused"

    def resume(self):
        if self.phase == "paused":
            self.phase = self.prev_phase

    def quit_to_title(self):
        self.record(quit_=True)
        self.app.go(TitleScene(self.app))

    def on_close(self):
        if self.phase != "lost":
            self.record(quit_=True)
        else:
            self.record()

    # ----------------------------------------------------------- input
    def on_click(self, pos):
        a = self.app.audio
        if self.phase == "paused":
            for b in (self.resume_btn, self.quit_btn):
                if b.hit(pos):
                    a.sfx("click")
                    b.action()
            return True
        if self.phase == "levelup":
            if self.phase_t > 0.6 and self.continue_btn.hit(pos):
                a.sfx("click")
                self.continue_level()
            return True
        if self.phase == "won":
            if self.phase_t > 1.2:
                self.next_after_win()
            return True
        if self.phase == "lost":
            if self.phase_t > 1.5:
                self.to_game_over()
            return True
        if super().on_click(pos):
            return True
        for ch, r in self.keys.items():
            if r.collidepoint(pos):
                self.handle_result(self.game.guess(ch), ch)
                return True
        return False

    def on_key(self, e):
        if e.key == pygame.K_ESCAPE:
            if self.phase == "paused":
                self.resume()
            else:
                self.pause()
            return
        enter = e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
        if self.phase == "paused":
            if enter:
                self.resume()
        elif self.phase == "won":
            if enter and self.phase_t > 1.2:
                self.next_after_win()
        elif self.phase == "levelup":
            if enter and self.phase_t > 0.6:
                self.continue_level()
        elif self.phase == "lost":
            if enter and self.phase_t > 1.5:
                self.to_game_over()
        elif self.phase == "play":
            ch = (e.unicode or "").upper()
            if len(ch) == 1 and "A" <= ch <= "Z":
                self.handle_result(self.game.guess(ch), ch)

    # ----------------------------------------------------------- update
    def update(self, dt):
        if self.phase == "paused":
            return
        self.phase_t += dt
        self.sketch.update(dt)
        self.msg_t = max(0.0, self.msg_t - dt)
        self.shake = max(0.0, self.shake - dt)
        if self.phase == "play" and self.game.tick(dt) == "timeout":
            self.lose()
        elif self.phase != "play":
            self.game.elapsed += dt
        if self.phase == "play":
            t = self.game.time_left
            self.app.audio.music("play" if t > 10 else "hurry1" if t > 6 else "hurry2" if t > 3 else "hurry3")
        elif self.phase == "won" and self.phase_t > 4.5:
            self.next_after_win()
        elif self.phase == "lost" and self.phase_t > 5.0:
            self.to_game_over()
        self.hint_btn.label = "Hint  (%d left)" % self.game.hints_left
        self.hint_btn.enabled = self.phase == "play" and self.game.hints_left > 0

    # ----------------------------------------------------------- draw
    def draw(self, s):
        g = self.game
        # top bar
        panel(s, (20, 14, W - 40, 72), (255, 255, 255), 20)
        text(s, "Level %d" % g.level, 34, INK, (44, 24))
        sub = "%d-letter words  -  word %d of %d  -  %s" % (len(g.word), g.word_in_level + 1, logic.WORDS_PER_LEVEL, g.difficulty)
        text(s, sub, 18, SOFT_INK, (46, 62))
        text(s, "Score", 18, SOFT_INK, (W - 44, 24), "topright")
        text(s, "%d" % g.score, 34, INK, (W - 44, 44), "topright")
        self.draw_timer(s, (W // 2 + 60, 50))

        # drawing card
        ox = int(math.sin(self.shake * 60) * 10 * (self.shake / 0.35)) if self.shake else 0
        card = pygame.Rect(40 + ox, 104, 520, 520)
        paper_card(s, card)
        s.blit(self.sketch.render(460), (card.x + 30, card.y + 28))
        wrong = " ".join(g.wrong) if g.wrong else "-"
        text(s, "Wrong letters:  " + wrong, 22, BAD if g.wrong else SOFT_INK, (44, 640))

        # chances
        text(s, "Chances", 24, INK, (620, 112))
        for i in range(logic.MAX_CHANCES):
            alive = i < g.chances
            cx = 780 + i * 46
            pts = heart_points(cx, 124, 1.15)
            pygame.draw.polygon(s, BAD if alive else (220, 220, 228), pts)
            pygame.draw.polygon(s, INK, pts, 2)
        # hints indicator
        for i in range(logic.HINTS_PER_GAME):
            c = GOLD if i < g.hints_left else (220, 220, 228)
            pygame.draw.circle(s, c, (1108 + i * 34, 124), 12)
            pygame.draw.circle(s, INK, (1108 + i * 34, 124), 12, 2)
        text(s, "Hints", 18, SOFT_INK, (1108 - 16, 142))

        self.draw_blanks(s)
        if self.msg_t > 0 and self.phase == "play":
            text(s, self.msg, 26, self.msg_color, (910, 310), "center")
        self.draw_keyboard(s)
        self.draw_buttons(s)

        if self.phase == "won":
            self.overlay_banner(s, "Great job!", "+%d points" % g.last_points, GOOD,
                                "Click or press Enter to continue" if self.phase_t > 1.2 else "")
        elif self.phase == "lost":
            head = "Time's up!" if g.lose_reason == "time" else "Out of chances!"
            self.overlay_banner(s, head, "The word was  %s" % g.word, BAD,
                                "Click or press Enter" if self.phase_t > 1.5 else "")
        elif self.phase == "levelup":
            self.draw_levelup(s)
        elif self.phase == "paused":
            self.dim(s)
            panel(s, (W // 2 - 220, 200, 440, 330), (255, 255, 255))
            text(s, "Paused", 48, INK, (W // 2, 260), "center")
            for b in (self.resume_btn, self.quit_btn):
                b.draw(s, self.app.mouse)

    def draw_timer(self, s, c):
        g = self.game
        t = g.time_left
        frac = t / g.time_limit
        urgent = t <= 10 and self.phase == "play"
        r = 30
        pulse = 1 + (0.08 * math.sin(pygame.time.get_ticks() / 70.0) if urgent else 0)
        col = BAD if urgent else (GOLD if t <= 30 else GOOD)
        pygame.draw.circle(s, (238, 240, 246), c, r)
        if frac > 0:
            pts = [c] + [(c[0] + r * math.sin(2 * math.pi * frac * i / 40), c[1] - r * math.cos(2 * math.pi * frac * i / 40)) for i in range(41)]
            pygame.draw.polygon(s, col, pts)
        pygame.draw.circle(s, INK, c, r, 3)
        pygame.draw.circle(s, (255, 255, 255), c, r - 9)
        text(s, "%d" % math.ceil(t), int(24 * pulse), BAD if urgent else INK, c, "center")
        text(s, "Time", 18, SOFT_INK, (c[0] - 44, c[1]), "midright")

    def draw_blanks(self, s):
        g = self.game
        n = len(g.word)
        gap = 8
        sw = min(58, (620 - (n - 1) * gap) // n)
        total = n * sw + (n - 1) * gap
        x0 = 910 - total // 2
        y = 178
        size = int(sw * 0.78)
        for i, ch in enumerate(g.word):
            r = pygame.Rect(x0 + i * (sw + gap), y, sw, 92)
            pygame.draw.rect(s, (255, 255, 255), r, border_radius=10)
            pygame.draw.line(s, INK, (r.left + 4, r.bottom - 10), (r.right - 4, r.bottom - 10), 4)
            if ch in g.guessed:
                text(s, ch, size, INK, (r.centerx, r.centery - 4), "center")
            elif g.state == "lost":
                text(s, ch, size, BAD, (r.centerx, r.centery - 4), "center")

    def draw_keyboard(self, s):
        g = self.game
        for ch, r in self.keys.items():
            if ch in g.guessed:
                col, tc = GOOD, (255, 255, 255)
            elif ch in g.wrong:
                col, tc = (226, 150, 150), (255, 255, 255)
            else:
                col, tc = (255, 255, 255), INK
            hover = r.collidepoint(self.app.mouse) and self.phase == "play" and col == (255, 255, 255)
            rr = r.move(0, -2) if hover else r
            pygame.draw.rect(s, shade(col, 0.75), rr.move(0, 4), border_radius=10)
            pygame.draw.rect(s, (255, 236, 200) if hover else col, rr, border_radius=10)
            pygame.draw.rect(s, INK, rr, 2, border_radius=10)
            text(s, ch, 28, tc, rr.center, "center")

    def dim(self, s):
        d = pygame.Surface((W, H), pygame.SRCALPHA)
        d.fill((20, 22, 40, 150))
        s.blit(d, (0, 0))

    def overlay_banner(self, s, head, sub, color, foot):
        r = pygame.Rect(600, 330, 620, 240)
        panel(s, r, (255, 255, 255))
        pygame.draw.rect(s, color, (r.x, r.y, r.w, 74), border_top_left_radius=22, border_top_right_radius=22)
        text(s, head, 44, (255, 255, 255), (r.centerx, r.y + 38), "center")
        text(s, sub, 34, INK, (r.centerx, r.y + 128), "center")
        if foot:
            text(s, foot, 20, SOFT_INK, (r.centerx, r.bottom - 34), "center")

    def draw_levelup(self, s):
        self.dim(s)
        g = self.game
        r = pygame.Rect(W // 2 - 330, 150, 660, 420)
        panel(s, r, (255, 255, 255))
        text(s, "Level %d complete!" % (g.level - 1), 52, ACCENT, (W // 2, 220), "center", shadow=INK)
        text(s, "Score: %d" % g.score, 32, INK, (W // 2, 290), "center")
        n = logic.word_length(g.level)
        text(s, "Next: Level %d  -  %d-letter words" % (g.level, n), 28, INK, (W // 2, 350), "center")
        if g.level == logic.EXPERT_LEVEL:
            text(s, "Expert mode! Tougher words and only 60 seconds.", 24, BAD, (W // 2, 400), "center")
        elif g.level > logic.EXPERT_LEVEL:
            text(s, "Words keep getting tougher. 60 seconds each.", 24, BAD, (W // 2, 400), "center")
        else:
            text(s, "%d seconds per word" % int(logic.time_limit(g.level)), 24, SOFT_INK, (W // 2, 400), "center")
        self.continue_btn.draw(s, self.app.mouse)


# ---------------------------------------------------------------------- game over
class GameOverScene(Scene):
    def __init__(self, app, game, sketch):
        super().__init__(app)
        self.game = game
        self.sketch = sketch
        self.sketch.finish(colour=True, duration=0.6)
        self.buttons = [
            Button((700, 560, 240, 70), "Play Again", self.again, ACCENT, 30),
            Button((960, 560, 240, 70), "Main Menu", lambda: app.go(TitleScene(app)), BLUEBTN, 30),
        ]

    def again(self):
        g = self.game
        self.app.go(PlayScene(self.app, logic.Game(g.difficulty, g.start_level)))

    def on_key(self, e):
        if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.app.audio.sfx("click")
            self.again()
        elif e.key == pygame.K_ESCAPE:
            self.app.go(TitleScene(self.app))

    def update(self, dt):
        self.sketch.update(dt)

    def draw(self, s):
        g = self.game
        card = pygame.Rect(80, 110, 500, 500)
        paper_card(s, card)
        s.blit(self.sketch.render(440), (card.x + 30, card.y + 20))
        text(s, g.word, 40, INK, (card.centerx, card.bottom + 40), "center")
        text(s, "Game Over", 72, BAD, (950, 150), "center", shadow=INK)
        why = "Time ran out on" if g.lose_reason == "time" else "Out of chances on"
        lines = [
            ("%s:  %s" % (why, g.word), INK),
            ("Final score:  %d" % g.score, INK),
            ("Level reached:  %d   (%s)" % (g.level, g.difficulty), INK),
            ("Words spelled:  %d" % g.words_solved, INK),
            ("Time played:  %s" % fmt_duration(g.elapsed), INK),
        ]
        panel(s, (700, 230, 500, 300), (255, 255, 255))
        for i, (ln, c) in enumerate(lines):
            text(s, ln, 26, c, (730, 262 + i * 52))
        self.draw_buttons(s)


# ---------------------------------------------------------------------- parents
class ParentScene(Scene):
    PER_PAGE = 7

    def __init__(self, app):
        super().__init__(app)
        self.page = 0
        self.confirm = False
        self.prev_btn = Button((40, 640, 150, 56), "< Newer", lambda: self.turn(-1), BLUEBTN, 24)
        self.next_btn = Button((200, 640, 150, 56), "Older >", lambda: self.turn(1), BLUEBTN, 24)
        self.clear_btn = Button((720, 640, 270, 56), "Clear History", self.clear, BAD, 24)
        self.buttons = [self.prev_btn, self.next_btn, self.clear_btn,
                        Button((1006, 640, 190, 56), "Back", lambda: app.go(TitleScene(app)), (130, 134, 150), 26)]

    def pages(self):
        return max(1, (len(self.app.progress.sessions) + self.PER_PAGE - 1) // self.PER_PAGE)

    def turn(self, k):
        self.page = max(0, min(self.pages() - 1, self.page + k))

    def clear(self):
        if not self.confirm:
            self.confirm = True
            self.clear_btn.label = "Click again to confirm"
        else:
            self.app.progress.clear()
            self.confirm = False
            self.clear_btn.label = "Clear History"
            self.page = 0

    def on_key(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.go(TitleScene(self.app))

    def update(self, dt):
        self.prev_btn.enabled = self.page > 0
        self.next_btn.enabled = self.page < self.pages() - 1
        self.clear_btn.enabled = bool(self.app.progress.sessions)

    def draw(self, s):
        text(s, "Parent Progress", 52, PURPLEBTN, (W // 2, 46), "center", shadow=INK)
        sm = self.app.progress.summary()
        cards = [("Total time played", fmt_duration(sm["total_seconds"])), ("Games played", str(sm["games"])),
                 ("Best score", str(sm["best_score"])), ("Highest level", str(sm["highest_level"])),
                 ("Words spelled", str(sm["words_solved"]))]
        cw = (W - 80 - 4 * 16) // 5
        for i, (lab, val) in enumerate(cards):
            r = pygame.Rect(40 + i * (cw + 16), 92, cw, 92)
            panel(s, r, (255, 255, 255), 16)
            text(s, lab, 18, SOFT_INK, (r.centerx, r.y + 22), "center")
            text(s, val, 34, INK, (r.centerx, r.y + 60), "center")

        practice = ", ".join("%s (%d)" % (w, n) for w, n in sm["practice"]) or "none yet"
        text(s, "Words to practice (missed):  " + practice, 22, INK, (44, 200))

        tbl = pygame.Rect(40, 236, W - 80, 392)
        panel(s, tbl, (255, 255, 255), 16)
        cols = [("Date", 60), ("Played", 250), ("Score", 380), ("Mode", 490), ("Level", 610),
                ("Result", 720), ("Missed word (level)", 920)]
        for name, x in cols:
            text(s, name, 20, SOFT_INK, (x, tbl.y + 16))
        pygame.draw.line(s, (220, 222, 232), (tbl.x + 12, tbl.y + 46), (tbl.right - 12, tbl.y + 46), 2)
        rows = list(reversed(self.app.progress.sessions))
        chunk = rows[self.page * self.PER_PAGE:(self.page + 1) * self.PER_PAGE]
        if not chunk:
            text(s, "No games played yet. Progress appears here after each game.", 24, SOFT_INK, tbl.center, "center")
        for i, r in enumerate(chunk):
            y = tbl.y + 60 + i * 47
            if i % 2 == 0:
                pygame.draw.rect(s, (246, 247, 252), (tbl.x + 10, y - 8, tbl.w - 20, 42), border_radius=8)
            lvl = "%d" % r.get("level_reached", 1)
            if r.get("start_level", 1) != r.get("level_reached", 1):
                lvl = "%d -> %d" % (r.get("start_level", 1), r.get("level_reached", 1))
            missed = "-"
            if r.get("failed_word"):
                missed = "%s  (level %d)" % (r["failed_word"], r.get("failed_level") or r.get("level_reached", 1))
            vals = [r.get("started_at", "?"), fmt_duration(r.get("duration_sec", 0)), str(r.get("score", 0)),
                    r.get("difficulty", "?"), lvl, r.get("result", "?"), missed]
            for (name, x), v in zip(cols, vals):
                c = BAD if name.startswith("Missed") and v != "-" else INK
                text(s, v, 22, c, (x, y))
        text(s, "Page %d of %d" % (self.page + 1, self.pages()), 20, SOFT_INK, (370, 668), "midleft")
        self.draw_buttons(s)


# ---------------------------------------------------------------------- credits
class CreditsScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.buttons = [Button((W // 2 - 120, 630, 240, 60), "Back", lambda: app.go(TitleScene(app)), (130, 134, 150), 28)]
        self.links = {}
        self.sketch = Sketch("PENCIL")
        self.sketch.finish(True, 1.5)

    def on_click(self, pos):
        if super().on_click(pos):
            return True
        for url, r in self.links.items():
            if r.collidepoint(pos):
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
                return True
        return False

    def on_key(self, e):
        if e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.app.go(TitleScene(self.app))

    def update(self, dt):
        self.sketch.update(dt)

    def draw(self, s):
        r = pygame.Rect(W // 2 - 400, 40, 800, 570)
        panel(s, r, (255, 255, 255))
        s.blit(self.sketch.render(110), (r.x + 30, r.y + 20))
        s.blit(self.sketch.render(110), (r.right - 140, r.y + 20))
        text(s, "Credits", 56, ACCENT, (W // 2, 90), "center", shadow=INK)
        text(s, version.APP_NAME, 36, INK, (W // 2, 170), "center")
        text(s, "Version %s" % version.VERSION, 26, INK, (W // 2, 220), "center")
        text(s, "Released %s" % version.RELEASE_DATE_LONG, 24, SOFT_INK, (W // 2, 256), "center")
        text(s, "Created by", 22, SOFT_INK, (W // 2, 312), "center")
        text(s, version.AUTHORS, 32, INK, (W // 2, 348), "center")
        hover = self.app.mouse
        lr = text(s, version.WEBSITE, 28, BLUEBTN, (W // 2, 420), "center")
        self.links[version.WEBSITE] = lr
        er = text(s, version.EMAIL, 28, BLUEBTN, (W // 2, 470), "center")
        self.links["mailto:" + version.EMAIL] = er
        for rr in (lr, er):
            if rr.collidepoint(hover):
                pygame.draw.line(s, BLUEBTN, (rr.left, rr.bottom), (rr.right, rr.bottom), 2)
        text(s, "Website", 18, SOFT_INK, (W // 2, 394), "center")
        text(s, "Email", 18, SOFT_INK, (W // 2, 446), "center")
        text(s, "Original music & sound effects generated for this game.", 20, SOFT_INK, (W // 2, 530), "center")
        text(s, "Made with Python and pygame.", 20, SOFT_INK, (W // 2, 560), "center")
        self.draw_buttons(s)


# ====================================================================== app
class App:
    def __init__(self):
        global FONTS
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption("%s v%s" % (version.APP_NAME, version.VERSION))
        try:
            pygame.display.set_icon(pygame.image.load(resource_path("assets", "icons", "icon-256.png")))
        except (pygame.error, FileNotFoundError):
            pass
        info = pygame.display.Info()
        w, h = W, H
        if info.current_w and info.current_w < W + 80:   # small screens
            k = (info.current_w - 80) / W
            w, h = int(W * k), int(H * k)
        self.windowed_size = (w, h)
        self.fullscreen = False
        self.window = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.canvas = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        FONTS = Fonts()
        self.audio = Audio(resource_path("assets", "audio"))
        self.progress = Progress()
        self.settings = {"difficulty": "Easy", "start_level": 1}
        self.mouse = (0, 0)
        self.running = True
        self.background = self.make_background()
        self.mute_btn = pygame.Rect(W - 60, H - 52, 44, 40)
        self.scene = None
        self.go(TitleScene(self))

    # ------------------------------------------------------------ helpers
    def make_background(self):
        bg = pygame.Surface((W, H))
        top, bot = (206, 232, 255), (255, 236, 214)
        for y in range(H):
            t = y / (H - 1)
            pygame.draw.line(bg, tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)), (0, y), (W, y))
        rng = random.Random(4)
        for _ in range(26):
            x, y = rng.randint(0, W), rng.randint(0, H)
            c = (255, 255, 255)
            kind = rng.random()
            if kind < 0.4:
                pygame.draw.circle(bg, c, (x, y), rng.randint(4, 10), 2)
            elif kind < 0.7:
                r = rng.randint(6, 12)
                pygame.draw.line(bg, c, (x - r, y), (x + r, y), 2)
                pygame.draw.line(bg, c, (x, y - r), (x, y + r), 2)
            else:
                pts = [(x + i * 8, y + (6 if i % 2 else -6)) for i in range(5)]
                pygame.draw.lines(bg, c, False, pts, 2)
        return bg

    def go(self, scene):
        self.scene = scene
        scene.enter()

    def quit(self):
        self.running = False

    def viewport(self):
        ww, wh = self.window.get_size()
        k = min(ww / W, wh / H) if ww and wh else 1
        vw, vh = max(1, int(W * k)), max(1, int(H * k))
        return pygame.Rect((ww - vw) // 2, (wh - vh) // 2, vw, vh), k

    def to_logical(self, pos):
        vp, k = self.viewport()
        return ((pos[0] - vp.x) / k, (pos[1] - vp.y) / k)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.windowed_size = self.window.get_size()
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

    # ------------------------------------------------------------ loop
    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.1)
            self.window = pygame.display.get_surface()
            self.mouse = self.to_logical(pygame.mouse.get_pos())
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    pos = self.to_logical(e.pos)
                    if self.mute_btn.collidepoint(pos):
                        self.audio.toggle_mute()
                    else:
                        self.scene.on_click(pos)
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif e.key == pygame.K_F1 or (e.key == pygame.K_m and not isinstance(self.scene, PlayScene)):
                        self.audio.toggle_mute()
                    else:
                        self.scene.on_key(e)
                elif e.type == pygame.WINDOWFOCUSLOST and isinstance(self.scene, PlayScene):
                    self.scene.pause()
            self.scene.update(dt)
            self.render()
        if hasattr(self.scene, "on_close"):
            self.scene.on_close()
        pygame.quit()

    def render(self):
        c = self.canvas
        c.blit(self.background, (0, 0))
        self.scene.draw(c)
        self.draw_mute(c)
        vp, k = self.viewport()
        self.window.fill(LETTERBOX)
        if vp.size == (W, H):
            self.window.blit(c, vp)
        else:
            self.window.blit(pygame.transform.smoothscale(c, vp.size), vp)
        pygame.display.flip()

    def draw_mute(self, s):
        r = self.mute_btn
        hover = r.collidepoint(self.mouse)
        pygame.draw.rect(s, (255, 255, 255) if hover else (240, 242, 248), r, border_radius=10)
        pygame.draw.rect(s, INK, r, 2, border_radius=10)
        cx, cy = r.x + 15, r.centery
        pygame.draw.polygon(s, INK, [(cx - 6, cy - 5), (cx - 1, cy - 5), (cx + 6, cy - 11), (cx + 6, cy + 11), (cx - 1, cy + 5), (cx - 6, cy + 5)])
        if self.audio.muted:
            pygame.draw.line(s, BAD, (cx + 11, cy - 7), (cx + 23, cy + 7), 3)
            pygame.draw.line(s, BAD, (cx + 23, cy - 7), (cx + 11, cy + 7), 3)
        else:
            for rad in (8, 14):
                pygame.draw.arc(s, INK, (cx + 4 - rad, cy - rad, rad * 2, rad * 2), -0.8, 0.8, 2)


def main():
    App().run()


if __name__ == "__main__":
    main()
