"""Generate the game's original music and sound effects as WAV files.

Dev-time tool (needs numpy). Output goes to assets/audio/ and is committed,
so the game itself never needs numpy.

    python3 tools/gen_audio.py
"""
import os
import wave

import numpy as np

SR = 22050
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")

NOTE_IDX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def midi(name):
    n, octv = name[:-1], int(name[-1])
    return 12 * (octv + 1) + NOTE_IDX[n]


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


# ------------------------------------------------------------ instruments
def env(n, a=0.005, d=0.1, s=0.6, r=0.1, dur=None):
    t = np.arange(n) / SR
    dur = dur if dur is not None else n / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel_start = max(dur - r, a)
    e = np.where(t > rel_start, e * np.clip(1 - (t - rel_start) / r, 0, 1), e)
    return e


def musicbox(f, dur):
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    w = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
         + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 9))
    return w * np.exp(-t * 2.6) * np.minimum(1, t / 0.004)


def marimba(f, dur):
    n = int((dur + 0.6) * SR)
    t = np.arange(n) / SR
    w = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 18)
    return w * np.exp(-t * 5.0) * np.minimum(1, t / 0.003)


def soft_lead(f, dur):
    n = int((dur + 0.15) * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.5 * t)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    w = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    return w * env(n, a=0.02, d=0.25, s=0.55, r=0.12, dur=dur + 0.15)


def bass(f, dur):
    n = int((dur + 0.05) * SR)
    t = np.arange(n) / SR
    tri = 2 * np.abs(2 * ((f * t) % 1) - 1) - 1
    w = 0.75 * np.sin(2 * np.pi * f * t) + 0.25 * tri
    return w * env(n, a=0.008, d=0.18, s=0.5, r=0.05, dur=dur + 0.05)


def pad(freqs, dur):
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    w = np.zeros(n)
    for f in freqs:
        for det in (0.997, 1.003):
            w += np.sin(2 * np.pi * f * det * t)
    w /= len(freqs) * 2
    return w * env(n, a=0.35, d=1.0, s=0.8, r=0.4, dur=dur + 0.4)


def hat(dur=0.05):
    n = int(dur * SR)
    rng = np.random.default_rng(7)
    x = rng.standard_normal(n)
    x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-np.arange(n) / SR * 70) * 0.5


def kick():
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    f = 50 + 70 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 14)


def shaker():
    n = int(0.03 * SR)
    rng = np.random.default_rng(3)
    x = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
    return x * np.exp(-np.arange(n) / SR * 120) * 0.4


# ------------------------------------------------------------ mixing
class Track:
    def __init__(self, seconds):
        self.n = int(round(seconds * SR))
        self.buf = np.zeros(self.n)

    def add(self, sig, at, gain=1.0, wrap=True):
        i = int(round(at * SR))
        end = i + len(sig)
        if end <= self.n:
            self.buf[i:end] += sig * gain
        else:
            k = self.n - i
            self.buf[i:] += sig[:k] * gain
            if wrap:   # wrap tails to the start for a seamless loop
                rest = sig[k:] * gain
                while len(rest):
                    m = min(len(rest), self.n)
                    self.buf[:m] += rest[:m]
                    rest = rest[m:]


def chord_notes(name):
    roots = {"C": ("C3", [0, 4, 7]), "Am": ("A2", [0, 3, 7]), "F": ("F2", [0, 4, 7]),
             "G": ("G2", [0, 4, 7]), "Dm": ("D3", [0, 3, 7]), "Em": ("E3", [0, 3, 7])}
    root, iv = roots[name]
    m = midi(root)
    return m, [m + 12 + i for i in iv]


def save(name, data, peak=0.8):
    data = data / (np.max(np.abs(data)) + 1e-9) * peak
    pcm = (data * 32767).astype("<i2")
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", name, "%.1fs" % (len(data) / SR))


def render_song(bpm, chords, melody, lead, lead_gain, drums="soft", arps=False, bars_per_chord=1):
    beat = 60.0 / bpm
    bars = len(chords) * bars_per_chord
    tr = Track(bars * 4 * beat)
    # pad + bass
    for ci, ch in enumerate(chords):
        root, notes = chord_notes(ch)
        start = ci * bars_per_chord * 4 * beat
        length = bars_per_chord * 4 * beat
        tr.add(pad([freq(m) for m in notes], length), start, 0.22)
        if arps:
            pattern = [0, 1, 2, 1] * 4
            for k in range(int(bars_per_chord * 16)):
                m = notes[pattern[k % len(pattern)]] + 12
                tr.add(marimba(freq(m), beat / 4), start + k * beat / 4, 0.2)
            for k in range(int(bars_per_chord * 8)):
                m = root if k % 2 == 0 else root + 12
                tr.add(bass(freq(m), beat / 2 * 0.9), start + k * beat / 2, 0.42)
        else:
            for k in range(int(bars_per_chord * 4)):
                m = root if k % 2 == 0 else root + 7
                tr.add(bass(freq(m), beat * 0.9), start + k * beat, 0.38)
    # melody
    t = 0.0
    for note, beats in melody:
        if note:
            tr.add(lead(freq(midi(note)), beats * beat), t * beat, lead_gain)
        t += beats
    # drums
    total_beats = bars * 4
    if drums == "soft":
        for b in range(total_beats):
            if b % 2 == 0:
                tr.add(kick(), b * beat, 0.25)
            tr.add(shaker(), (b + 0.5) * beat, 0.18)
    elif drums == "drive":
        for b in range(total_beats):
            tr.add(kick(), b * beat, 0.35)
            tr.add(hat(), (b + 0.5) * beat, 0.22)
            tr.add(shaker(), (b + 0.25) * beat, 0.08)
            tr.add(shaker(), (b + 0.75) * beat, 0.08)
    return tr.buf


def main():
    # Title: gentle music box, 84 bpm
    title_mel = [
        ("G5", 1.5), ("E5", .5), ("C5", 1), ("E5", 1),
        ("D5", 1.5), ("B4", .5), ("G4", 1), ("B4", 1),
        ("C5", 1.5), ("E5", .5), ("A5", 1), ("G5", 1),
        ("F5", 1), ("E5", 1), ("C5", 1), ("A4", 1),
        ("G5", 1.5), ("E5", .5), ("C6", 1), ("G5", 1),
        ("B5", 1), ("A5", .5), ("G5", .5), ("D5", 2),
        ("E5", 1), ("A5", 1), ("G5", 1), ("E5", 1),
        ("F5", 1), ("E5", .5), ("D5", .5), ("C5", 2),
    ]
    save("title.wav", render_song(84, ["C", "G", "Am", "F"] * 2, title_mel, musicbox, 0.32, drums=None), 0.75)

    # Play: relaxed, bouncy, 100 bpm
    play_mel = [
        ("E5", .5), ("G5", .5), ("A5", .5), ("G5", .5), ("E5", 1), ("C5", 1),
        ("A4", .5), ("C5", .5), ("E5", .5), ("D5", .5), ("C5", 1), ("A4", 1),
        ("F4", .5), ("A4", .5), ("C5", .5), ("D5", .5), ("C5", .5), ("A4", .5), ("F4", 1),
        ("G4", .5), ("B4", .5), ("D5", .5), ("G5", .5), ("F5", 1), ("D5", 1),
        ("E5", .5), ("G5", .5), ("C6", .5), ("B5", .5), ("G5", 1), ("E5", 1),
        ("A5", .5), ("G5", .5), ("E5", .5), ("C5", .5), ("D5", 1), ("E5", 1),
        ("F5", .5), ("E5", .5), ("D5", .5), ("C5", .5), ("A4", 1), ("D5", 1),
        ("B4", .5), ("D5", .5), ("G5", .5), ("F5", .5), ("D5", 1), ("B4", .5), (None, .5),
    ]
    save("play.wav", render_song(100, ["C", "Am", "F", "G", "C", "Am", "Dm", "G"], play_mel, marimba, 0.42), 0.7)

    # Hurry: same harmony, driving arpeggios, faster each step
    hurry_mel = [
        ("E5", 1), ("G5", 1), ("C6", 1), ("G5", 1),
        ("E5", 1), ("A5", 1), ("C6", 1), ("A5", 1),
        ("F5", 1), ("A5", 1), ("C6", 1), ("A5", 1),
        ("G5", 1), ("B5", 1), ("D6", 1), ("B5", 1),
    ]
    for i, bpm in enumerate((138, 168, 200), start=1):
        save("hurry%d.wav" % i, render_song(bpm, ["C", "Am", "F", "G"], hurry_mel, soft_lead, 0.25,
                                            drums="drive", arps=True), 0.72)

    # ---------------- sound effects
    def seq(notes, step, inst=marimba, gain=1.0, tail=0.6):
        tr = Track(len(notes) * step + tail)
        for i, nm in enumerate(notes):
            if nm:
                tr.add(inst(freq(midi(nm)), step), i * step, gain, wrap=False)
        return tr.buf

    save("correct.wav", seq(["E5", "A5"], 0.08, tail=0.4), 0.6)
    save("wrong.wav", seq(["D3", "A2"], 0.12, inst=bass, tail=0.2), 0.6)
    save("win.wav", seq(["C5", "E5", "G5", "C6", "E6"], 0.09, tail=0.9), 0.65)
    save("lose.wav", seq(["G4", "E4", "C4", "G3"], 0.22, inst=soft_lead, tail=0.4), 0.55)
    save("levelup.wav", seq(["C5", "G5", "E5", "C6", None, "G5", "C6", "E6", "G6"], 0.1, inst=musicbox, tail=1.2), 0.65)
    save("click.wav", seq(["A5"], 0.03, inst=marimba, tail=0.08), 0.35)
    save("hint.wav", seq(["C6", "G6", "E6", "C7"], 0.06, inst=musicbox, tail=0.6), 0.5)
    save("already.wav", seq(["E4"], 0.06, inst=marimba, tail=0.12), 0.4)


if __name__ == "__main__":
    main()
