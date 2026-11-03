"""Build the app icon (PNG sizes + Windows .ico) from the PENCIL sketch."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()
from guess_a_sketch.sketch import Sketch
from PIL import Image

out = os.path.join(ROOT, "assets", "icons")
os.makedirs(out, exist_ok=True)
S = 512
img = pygame.Surface((S, S), pygame.SRCALPHA)
pygame.draw.rect(img, (255, 128, 64), (16, 16, S - 32, S - 32), border_radius=96)
pygame.draw.rect(img, (255, 252, 240), (48, 48, S - 96, S - 96), border_radius=72)
sk = Sketch("PENCIL"); sk.complete_now(True)
pic = pygame.transform.rotate(sk.render(400), 35)
img.blit(pic, pic.get_rect(center=(S // 2, S // 2)))
# question-mark style dashed blanks
for i in range(3):
    pygame.draw.line(img, (44, 48, 72), (130 + i * 92, 420), (200 + i * 92, 420), 14)
big = os.path.join(out, "icon-512.png")
pygame.image.save(img, big)
im = Image.open(big)
for sz in (256, 128, 64, 48):
    im.resize((sz, sz), Image.LANCZOS).save(os.path.join(out, "icon-%d.png" % sz))
im.save(os.path.join(out, "icon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icons written")
