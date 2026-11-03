"""Render every drawing to a PNG grid for visual QA (dev tool)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()
from guess_a_sketch import drawings
from guess_a_sketch.sketch import Sketch

out = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "color"
words = sorted(drawings.WORDS, key=lambda w: (len(w), w))
cell, cols = 170, 12
rows = (len(words) + cols - 1) // cols
img = pygame.Surface((cols * cell, rows * cell))
img.fill((255, 252, 240))
font = pygame.font.Font(None, 22)
for i, w in enumerate(words):
    s = Sketch(w)
    if mode == "stage0":
        s.show_stages(1); s.drawn = s.target
    else:
        s.complete_now(True)
    x, y = (i % cols) * cell, (i // cols) * cell
    img.blit(s.render(cell - 20), (x + 10, y + 4))
    img.blit(font.render("%s t%d (%d)" % (w, drawings.WORDS[w]["tier"], len(drawings.WORDS[w]["prims"])), True, (0, 0, 0)), (x + 6, y + cell - 18))
pygame.image.save(img, out)
print(len(words), "words")
for n in range(2, 11):
    ws = drawings.words_of_length(n)
    print(n, len(ws), {t: sum(1 for w in ws if drawings.WORDS[w]["tier"] == t) for t in (1, 2, 3)})
