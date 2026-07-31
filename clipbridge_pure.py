"""ClipBridge — Pure Encoding Recovery Module

Zero-dependency encoding recovery for Windows clipboard CJK corruption.

When Chromium/Electron apps stuff UTF-8 bytes into CF_UNICODETEXT
(which expects UTF-16LE), this module detects and recovers the original
text through two complementary patterns.

Usage:
    from clipbridge_pure import has_cjk, recover_clipboard

    raw_bytes = get_clipboard_data()  # from Win32 API
    fixed = recover_clipboard(raw_bytes)
    if fixed:
        put_clipboard_data(fixed)
"""

import re

# CJK character detection

CJK_RE = re.compile(
    r'[一-鿿'
    r'㐀-䶿'
    r'豈-﫿'
    r'　-〿'
    r'＀-￯'
    r'⺀-⻿'
    r']'
)


def has_cjk(text: str) -> bool:
    """Return True if text contains CJK characters."""
    return bool(CJK_RE.search(text))


# Encoding recovery


def _recover_utf8_mojibake(text: str) -> str | None:
    """Detect and recover Latin-1 mojibake of UTF-8 CJK text.

    When UTF-8 bytes are misinterpreted as Latin-1, CJK text renders
    as accented gibberish. This detects the pattern and reverses it.

    Returns None if the text doesn't match the mojibake pattern.
    """
    if not text or has_cjk(text):
        return None

    # Count Latin-1 high bytes (0xC0-0xFF); if >30% of non-ASCII chars
    # fall in this range, likely mojibake
    non_ascii = [c for c in text if ord(c) >= 128]
    if not non_ascii:
        return None
    latin1_high = sum(1 for c in non_ascii if 0xC0 <= ord(c) <= 0xFF)
    if latin1_high / len(non_ascii) < 0.3:
        return None

    # Reverse: encode as Latin-1 bytes, decode as UTF-8
    try:
        raw = text.encode('latin-1')
        recovered = raw.decode('utf-8')
        if has_cjk(recovered):
            return recovered
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return None


def _recover_utf8_in_utf16le(raw: bytes) -> str | None:
    """Recover text when UTF-8 bytes are dumped directly into CF_UNICODETEXT.

    Two patterns are handled:

    Pattern A — byte-expanded: each UTF-8 byte stored as a 16-bit char
    (non-zero even bytes, 0x00 odd bytes).

    Pattern B — raw UTF-8: no padding, just the UTF-8 stream verbatim.

    Pattern B safety guard: only applied when decoded text is pure ASCII
    with >50% alphabetic characters. This avoids mis-correcting real
    UTF-16LE CJK text whose bytes happen to also be valid UTF-8.
    """
    if len(raw) < 2:
        return None

    # Pattern A: byte-expanded (alternating 0x00)
    # At least 80% of odd bytes must be 0x00, and at least 50% of even
    # bytes non-zero, to qualify as byte-expanded UTF-8-in-UTF16LE.
    sample_size = min(len(raw), 100)
    odd_zeros = sum(1 for i in range(1, sample_size, 2) if raw[i] == 0)
    odd_total = sample_size // 2
    even_nonzero = sum(1 for i in range(0, sample_size, 2) if raw[i] != 0)
    even_total = (sample_size + 1) // 2

    if odd_total > 0 and odd_zeros / odd_total >= 0.8:
        if even_nonzero / even_total >= 0.5:
            # Extract even bytes (the UTF-8 stream), strip trailing nulls
            extracted = bytes(raw[i] for i in range(0, len(raw), 2))
            extracted = extracted.rstrip(b'\x00')
            try:
                return extracted.decode('utf-8')
            except UnicodeDecodeError:
                pass
        return None

    # Pattern B: raw UTF-8 (no 0x00 alternation)
    # Raw UTF-8 bytes dropped directly into CF_UNICODETEXT.
    # Decode as UTF-8 if the result is pure ASCII English (alpha ratio >50%).
    raw_stripped = raw.rstrip(b'\x00')
    if raw_stripped:
        try:
            recovered = raw_stripped.decode('utf-8')
            if recovered.isascii():
                alpha_ratio = sum(c.isalpha() for c in recovered) / max(len(recovered), 1)
                if alpha_ratio > 0.5:
                    return recovered
        except UnicodeDecodeError:
            pass

    return None


def recover_clipboard(raw_bytes: bytes) -> str | None:
    """Attempt to recover garbled CJK text from raw CF_UNICODETEXT data.

    This is the main entry point. Call it with raw bytes obtained from
    Win32 GetClipboardData(CF_UNICODETEXT):
        - If the data is corrupt, returns recovered str for re-writing
        - If the data is already valid UTF-16LE, returns None

    Steps:
    1. Try standard UTF-16LE decode (valid data, no fix needed)
    2. Try Pattern A/B recovery on the raw bytes
    3. Try mojibake recovery on whatever decoded

    If any step recovers CJK text, that text is returned for re-injection
    into the clipboard. Otherwise None.
    """
    # Step 1: standard UTF-16LE decode
    try:
        text = raw_bytes.decode('utf-16-le')
        if has_cjk(text):
            return None  # already good
    except UnicodeDecodeError:
        pass

    # Step 2: Pattern A/B recovery from raw bytes
    recovered = _recover_utf8_in_utf16le(raw_bytes)
    if recovered is not None:
        return recovered

    # Step 3: try to decode as UTF-16LE and run mojibake recovery
    try:
        text = raw_bytes.decode('utf-16-le', errors='replace')
        recovered = _recover_utf8_mojibake(text)
        if recovered is not None:
            return recovered
    except UnicodeDecodeError:
        pass

    return None
