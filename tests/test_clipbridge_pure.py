"""Tests for ClipBridge encoding recovery functions.

These tests only exercise the pure-Python encoding logic � No Win32 API calls.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clipbridge_pure import (
    has_cjk,
    _recover_utf8_mojibake,
    _recover_utf8_in_utf16le,
)


class TestHasCJK:
    """CJK detection tests."""

    def test_chinese(self):
        assert has_cjk("\u4f60\u597d\u4e16\u754c")

    def test_japanese(self):
        assert has_cjk("\u65e5\u672c\u8a9e")

    def test_korean(self):
        assert has_cjk("\u5927\u97d3\u6c11\u570b")

    def test_ascii_only(self):
        assert not has_cjk("Hello World")

    def test_ascii_with_numbers(self):
        assert not has_cjk("test 123 ABC")

    def test_mixed_cjk_ascii(self):
        assert has_cjk("Hello \u4e16\u754c")

    def test_empty(self):
        assert not has_cjk("")


class TestRecoverUtf8Mojibake:
    """Latin-1 to UTF-8 mojibake recovery."""

    def test_chinese_mojibake(self):
        text = "\u8fd0\u884c\u4e2d".encode('utf-8').decode('latin-1')
        result = _recover_utf8_mojibake(text)
        assert result == "\u8fd0\u884c\u4e2d"

    def test_already_valid_cjk(self):
        result = _recover_utf8_mojibake("\u4f60\u597d\u4e16\u754c")
        assert result is None

    def test_ascii_text(self):
        result = _recover_utf8_mojibake("Hello World")
        assert result is None

    def test_empty_text(self):
        result = _recover_utf8_mojibake("")
        assert result is None

    def test_garbled_text(self):
        mojibake = "\u8fd0\u884c\u4e2d".encode('utf-8').decode('latin-1')
        result = _recover_utf8_mojibake(mojibake)
        assert result == "\u8fd0\u884c\u4e2d"


class TestRecoverUtf8InUtf16LE:
    """Pattern A + Pattern B recovery from raw CF_UNICODETEXT bytes."""

    def test_pattern_a_chinese(self):
        utf8 = "\u63a7\u5236".encode('utf-8')
        raw = bytes(b for byte in utf8 for b in (byte, 0))
        result = _recover_utf8_in_utf16le(raw)
        assert result == "\u63a7\u5236"

    def test_pattern_a_ascii_alternating(self):
        utf8 = "abc".encode('utf-8')
        raw = bytes(b for byte in utf8 for b in (byte, 0))
        result = _recover_utf8_in_utf16le(raw)
        assert result == "abc"

    def test_pattern_b_english(self):
        raw = "Anthropic API".encode('utf-8')
        result = _recover_utf8_in_utf16le(raw)
        assert result == "Anthropic API"

    def test_pattern_b_code_keywords(self):
        raw = "function import return class".encode('utf-8')
        result = _recover_utf8_in_utf16le(raw)
        assert result == "function import return class"

    def test_empty_bytes(self):
        result = _recover_utf8_in_utf16le(b'')
        assert result is None

    def test_single_byte(self):
        result = _recover_utf8_in_utf16le(b'A')
        assert result is None

    def test_short_utf16le_not_expanded(self):
        raw = "Hi".encode('utf-16-le')
        result = _recover_utf8_in_utf16le(raw)
        assert result == "Hi"

    def test_proper_utf16le_cjk_not_mistriggered(self):
        raw = "\u4f60\u597d".encode('utf-16-le')
        result = _recover_utf8_in_utf16le(raw)
        assert result is None