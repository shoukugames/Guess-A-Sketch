# Guess-A-Sketch

A hangman-style spelling game for kids. Instead of a hangman, every wrong letter
sketches more of the mystery object. Spell the word before the drawing is finished!

**Version 0.1.0** · released November 3, 2026 · created by Shawn Rapaz and Claude Code
· https://shoukugames.org/ · info@shoukugames.org

## How to play
- The first stroke(s) of a drawing appear as a hint. Type letters (or click the on-screen keyboard).
- 5 chances per word: each wrong letter draws more; on the 5th the drawing is complete and the game ends.
- 99 seconds per word (60 seconds at the 10-letter levels). Points = seconds left x 10 x difficulty (Easy x1, Medium x2, Hard x3).
- 3 hints per game; each reveals a letter.
- 3 words per level. Level 1 = 2-letter words, level 2 = 3 letters, ... level 9+ = 10 letters with harder words. Levels are unlimited.
- Music speeds up when the timer reaches 10 seconds (again at 6 and 3).
- Keys: `Esc` pause/back, `Enter` continue, `F11` fullscreen, `F1` mute. Drag window edges/corners to resize; the game scales to fit.

The **Parent Progress** screen shows total play time, scores, level reached, and which word (and level) each game ended on.
Saved to `~/.local/share/guess-a-sketch/progress.json` (Linux) or `%APPDATA%\GuessASketch\progress.json` (Windows).

## Run from source
```
pip install pygame
python3 main.py
python3 -m unittest discover -s tests
```

## Build release packages
```
bash packaging/windows/setup_wine.sh   # one time: Windows Python in a Wine prefix
./build.sh                             # -> dist/guess-a-sketch_<ver>_amd64.deb, dist/GuessASketch-<ver>-win64.exe
```
The version comes from `guess_a_sketch/version.py`. Dev tools: `tools/gen_audio.py` (regenerates the original
music/SFX, needs numpy), `tools/make_icon.py`, `tools/contact_sheet.py` (renders all drawings for review).
