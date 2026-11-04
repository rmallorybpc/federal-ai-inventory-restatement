"""Report encoding problems in inventory CSV files.

Usage:
    python check-encoding.py <file> [<file> ...]

For each file it reports whether the bytes decode cleanly as UTF-8,
and if not, where each invalid byte sits and what surrounds it.
"""

import sys


CONTEXT = 50
MAX_SHOWN = 20


def invalid_positions(data):
    """Return every byte offset where strict UTF-8 decoding fails."""
    bad = []
    start = 0
    while start < len(data):
        try:
            data[start:].decode("utf-8")
            break
        except UnicodeDecodeError as err:
            pos = start + err.start
            bad.append(pos)
            start = pos + 1
    return bad


def context(data, pos):
    """Return readable text around a byte offset."""
    lo = max(0, pos - CONTEXT)
    hi = min(len(data), pos + CONTEXT)
    before = data[lo:pos].decode("utf-8", errors="replace")
    after = data[pos + 1:hi].decode("utf-8", errors="replace")
    return before, after


def report(path):
    with open(path, "rb") as handle:
        data = handle.read()

    print(f"file: {path}")
    print(f"bytes: {len(data):,}")

    bad = invalid_positions(data)
    if not bad:
        print("utf-8: clean")
        print()
        return

    print(f"utf-8: {len(bad)} invalid byte(s)")
    print()

    for pos in bad[:MAX_SHOWN]:
        before, after = context(data, pos)
        print(f"  offset {pos:,}  byte {hex(data[pos])}")
        print(f"    ...{before}[BAD]{after}...")
        print()

    if len(bad) > MAX_SHOWN:
        print(f"  ({len(bad) - MAX_SHOWN} more not shown)")
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    for path in sys.argv[1:]:
        report(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
