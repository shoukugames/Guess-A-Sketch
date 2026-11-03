"""Renders a word's drawing progressively, like a pencil sketching it."""

import math
import pygame

from . import drawings

PENCIL = (78, 78, 92)
OUTLINE = (52, 46, 58)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _poly_len(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


class Sketch:
    """Holds one drawing plus its reveal animation state."""

    def __init__(self, word, paper=(255, 252, 240)):
        self.word = word
        self.paper = paper
        src = drawings.get(word)["prims"]
        n = len(src)
        self.items = []
        cursor = 0.0
        for i, p in enumerate(src):
            stroke = list(p["pts"])
            if p["closed"]:
                stroke.append(stroke[0])
            length = max(_poly_len(stroke), 0.01)
            self.items.append({
                "p": p, "stroke": stroke, "len": length, "start": cursor,
                "stage": drawings.stage_of(i, n), "order": i,
            })
            cursor += length
        self.stage_end = []
        for s in range(drawings.STAGES):
            ends = [it["start"] + it["len"] for it in self.items if it["stage"] <= s]
            self.stage_end.append(max(ends) if ends else 0.0)
        self.total = cursor
        self.drawn = 0.0          # length drawn so far
        self.target = 0.0         # length we are animating toward
        self.speed = 1.0
        self.color = 0.0          # 0 = pencil, 1 = full colour
        self.color_target = 0.0
        self._cache = None
        self._cache_key = None

    # ----------------------------------------------------------- control
    def show_stages(self, count, duration=0.9):
        """Animate until `count` stages (1..6) are visible."""
        count = max(0, min(drawings.STAGES, count))
        tgt = self.stage_end[count - 1] if count > 0 else 0.0
        if tgt > self.target:
            self.target = tgt
            self.speed = max((self.target - self.drawn) / max(duration, 0.05), 1.0)

    def finish(self, colour=True, duration=1.0):
        self.show_stages(drawings.STAGES, duration)
        if colour:
            self.color_target = 1.0

    def complete_now(self, colour=True):
        self.drawn = self.target = self.total
        self.color = self.color_target = 1.0 if colour else 0.0

    @property
    def animating(self):
        return self.drawn < self.target or self.color < self.color_target

    def update(self, dt):
        if self.drawn < self.target:
            self.drawn = min(self.target, self.drawn + self.speed * dt)
        if self.drawn >= self.target and self.color < self.color_target:
            self.color = min(self.color_target, self.color + dt * 1.6)

    # ----------------------------------------------------------- drawing
    def render(self, size):
        """Return a Surface (size x size) with the sketch on transparent bg."""
        key = (size, round(self.drawn, 2), round(self.color, 3))
        if self._cache is not None and self._cache_key == key:
            return self._cache
        ss = 2  # supersample for smooth lines
        big = size * ss
        surf = pygame.Surface((big, big), pygame.SRCALPHA)
        scale = big / 100.0
        width = max(2, int(big / 125))
        t = self.color
        order = sorted(self.items, key=lambda it: (it["p"]["z"], it["order"]))
        for it in order:
            frac = (self.drawn - it["start"]) / it["len"]
            if frac <= 0:
                continue
            frac = min(frac, 1.0)
            p = it["p"]
            if frac >= 1.0 and p["closed"] and p["fill"] is not None and len(p["pts"]) >= 3:
                fill = _lerp(self.paper, p["fill"], t)
                pygame.draw.polygon(surf, fill, [(x * scale, y * scale) for x, y in p["pts"]])
            col = _lerp(PENCIL, p["col"] or OUTLINE, t)
            self._stroke(surf, it["stroke"], frac * it["len"], scale, width, col)
        if ss != 1:
            surf = pygame.transform.smoothscale(surf, (size, size))
        self._cache, self._cache_key = surf, key
        return surf

    @staticmethod
    def _stroke(surf, pts, length, scale, width, col):
        out = [(pts[0][0] * scale, pts[0][1] * scale)]
        remaining = length
        for i in range(len(pts) - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            seg = math.hypot(bx - ax, by - ay)
            if seg <= 0:
                continue
            if remaining >= seg:
                out.append((bx * scale, by * scale))
                remaining -= seg
            else:
                f = remaining / seg
                out.append(((ax + (bx - ax) * f) * scale, (ay + (by - ay) * f) * scale))
                break
        if len(out) >= 2:
            pygame.draw.lines(surf, col, False, out, width)
        r = width // 2
        if r >= 1:
            for x, y in out:
                pygame.draw.circle(surf, col, (int(x), int(y)), r)
