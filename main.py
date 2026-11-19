"""Entry point: `python3 main.py` and PyInstaller on the desktop, and pygbag in a web browser.

Web build:  python3 tools/build_web.py     (writes build/web/)
"""
import sys

import pygame  # noqa: F401  (imported here so pygbag loads pygame for the web build)

# Browser audio: the page mixes sound on its main thread, between the game's frames, so a small
# mixer buffer runs dry whenever a frame takes a little longer, and the sound crackles and drops
# out. 2048 samples (43 ms at the browser's 48 kHz) rides over slow frames. Browser only.
if sys.platform == "emscripten":
    WEB_AUDIO_BUFFER = 2048

    def _web_audio_buffer(fn):
        def call(*args, **kwargs):
            if len(args) >= 4:
                args = args[:3] + (WEB_AUDIO_BUFFER,) + args[4:]
            else:
                kwargs["buffer"] = WEB_AUDIO_BUFFER
            return fn(*args, **kwargs)
        return call

    pygame.mixer.pre_init = _web_audio_buffer(pygame.mixer.pre_init)
    pygame.mixer.init = _web_audio_buffer(pygame.mixer.init)
    pygame.mixer.pre_init()

if sys.platform == "emscripten":
    import asyncio

    from guess_a_sketch.game import App

    async def main():
        await App().run_web()

    asyncio.run(main())
else:
    from guess_a_sketch.game import main

    if __name__ == "__main__":
        main()
