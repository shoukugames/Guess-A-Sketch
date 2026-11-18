"""Entry point: `python3 main.py` and PyInstaller on the desktop, and pygbag in a web browser.

Web build:  python3 tools/build_web.py     (writes build/web/)
"""
import sys

import pygame  # noqa: F401  (imported here so pygbag loads pygame for the web build)

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
