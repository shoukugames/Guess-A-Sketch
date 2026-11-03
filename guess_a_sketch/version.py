"""Single source of truth for the game's version information."""

APP_NAME = "Guess-A-Sketch"
VERSION = "0.2.0"
RELEASE_DATE = "2026-11-04"
RELEASE_DATE_LONG = "November 4, 2026"
RELEASE_DATE_JA = "2026年11月4日"
AUTHORS = "Shawn Rapaz and Claude Code"
WEBSITE = "https://shoukugames.org/"
EMAIL = "info@shoukugames.org"


def release_date():
    from . import i18n
    return RELEASE_DATE_JA if i18n.LANG == "ja" else RELEASE_DATE_LONG
