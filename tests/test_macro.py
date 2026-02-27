# -*- coding: utf-8 -*-
from src.utils import keyboard_ops

def test_type_unicode_text_human_like_truncation(capsys):
    # 텍스트 길이 제한 테스트
    sent_units = []
    original_sender = keyboard_ops._send_unicode_utf16_unit
    keyboard_ops._send_unicode_utf16_unit = sent_units.append
    try:
        long_text = "a" * 11000
        keyboard_ops.type_unicode_text_human_like(long_text, delay=0)
    finally:
        keyboard_ops._send_unicode_utf16_unit = original_sender

    assert len(sent_units) == 10000
    captured = capsys.readouterr()
    assert "[경고] 텍스트가 너무 길어서 잘림" in captured.out

def test_type_unicode_text_human_like_stop_signal():
    sent_units = []
    original_sender = keyboard_ops._send_unicode_utf16_unit
    keyboard_ops._send_unicode_utf16_unit = sent_units.append
    try:
        keyboard_ops.type_unicode_text_human_like(
            "abcdef",
            delay=0,
            should_stop=lambda: len(sent_units) >= 3,
        )
    finally:
        keyboard_ops._send_unicode_utf16_unit = original_sender

    assert len(sent_units) == 3
