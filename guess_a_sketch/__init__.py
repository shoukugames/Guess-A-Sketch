"""Guess-A-Sketch - a drawing-based spelling game."""
from .version import VERSION as __version__  # noqa: F401

# True when running in a web browser (pygbag / WebAssembly).
import sys as _sys
WEB = _sys.platform == "emscripten"
