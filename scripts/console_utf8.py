"""
Shared console setup for scripts that print Vietnamese text.

WHY THIS EXISTS
On Windows, when a script's stdout is a pipe (dagu, cron, CI, `| head`),
Python falls back to the cp1252 codec and crashes with:

    UnicodeEncodeError: 'charmap' codec can't encode character '\u1eef' ...

That kills the whole workflow run, not just the print. Importing this module
forces UTF-8 on stdout/stderr so scripts survive being run from a runner.

Usage (top of any script that prints non-ASCII):
    from console_utf8 import ensure_utf8_console
    ensure_utf8_console()
"""
from __future__ import annotations

import sys


def ensure_utf8_console() -> None:
    """Force UTF-8 on stdout/stderr. Safe to call more than once."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            # Not a TextIOWrapper (e.g. already wrapped, or a test double).
            pass
