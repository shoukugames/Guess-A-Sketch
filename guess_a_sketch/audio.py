"""Background music and sound effects. Fails silently if no audio device."""

import os
import pygame

MUSIC = ("title", "play", "hurry1", "hurry2", "hurry3")
SFX = ("correct", "wrong", "win", "lose", "levelup", "click", "hint", "already")


class Audio:
    def __init__(self, asset_dir):
        self.ok = False
        self.muted = False
        self.current = None
        self.sounds = {}
        self.music_volume = 0.45
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            pygame.mixer.set_num_channels(12)
            pygame.mixer.set_reserved(1)
            self.channel = pygame.mixer.Channel(0)
            for name in MUSIC + SFX:
                path = os.path.join(asset_dir, name + ".wav")
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
            for name in SFX:
                if name in self.sounds:
                    self.sounds[name].set_volume(0.7)
            self.ok = True
        except pygame.error:
            self.ok = False

    def music(self, name):
        """Switch background loop (no-op if already playing it)."""
        if not self.ok or name == self.current:
            return
        self.current = name
        if name is None or name not in self.sounds:
            self.channel.fadeout(300)
            return
        self.channel.play(self.sounds[name], loops=-1, fade_ms=250)
        self.channel.set_volume(0 if self.muted else self.music_volume)

    def stop_music(self):
        self.music(None)

    def sfx(self, name):
        if self.ok and not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.ok:
            self.channel.set_volume(0 if self.muted else self.music_volume)
        return self.muted
