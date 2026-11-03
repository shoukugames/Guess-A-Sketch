"""Parent progress log: saved to a JSON file in the user's data folder."""

import json
import os
import sys
import time
from collections import Counter


def data_dir():
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        path = os.path.join(base, "GuessASketch")
    elif sys.platform == "darwin":
        path = os.path.expanduser("~/Library/Application Support/GuessASketch")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        path = os.path.join(base, "guess-a-sketch")
    os.makedirs(path, exist_ok=True)
    return path


class Progress:
    MAX_SESSIONS = 500

    def __init__(self, path=None):
        self.path = path or os.path.join(data_dir(), "progress.json")
        self.data = {"sessions": [], "highest_level": 1}
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict) and isinstance(d.get("sessions"), list):
                self.data = d
                self.data.setdefault("highest_level", 1)
        except (OSError, ValueError):
            pass

    def save(self):
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=1)
            os.replace(tmp, self.path)
        except OSError:
            pass

    @property
    def sessions(self):
        return self.data["sessions"]

    @property
    def highest_level(self):
        return int(self.data.get("highest_level", 1))

    def record(self, session):
        """session: dict with keys described in game.Game.session_record()."""
        session.setdefault("ended_at", time.strftime("%Y-%m-%d %H:%M"))
        self.sessions.append(session)
        del self.sessions[:-self.MAX_SESSIONS]
        self.data["highest_level"] = max(self.highest_level, int(session.get("level_reached", 1)))
        self.save()

    def clear(self):
        """Erase play history but keep settings such as the language."""
        self.data = {"sessions": [], "highest_level": 1, "settings": self.data.get("settings", {})}
        self.save()

    def summary(self):
        s = self.sessions
        return {
            "games": len(s),
            "total_seconds": sum(x.get("duration_sec", 0) for x in s),
            "best_score": max((x.get("score", 0) for x in s), default=0),
            "highest_level": max((x.get("level_reached", 1) for x in s), default=1),
            "words_solved": sum(x.get("words_solved", 0) for x in s),
            "practice": Counter(x["failed_word"] for x in s if x.get("failed_word")).most_common(6),
        }


def fmt_duration(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return "%dh %02dm" % (h, m)
    if m:
        return "%dm %02ds" % (m, s)
    return "%ds" % s
