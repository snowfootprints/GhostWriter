# -*- coding: utf-8 -*-
import pytest
from src.utils import notepad_ops

def test_find_most_recent_notepad_hwnd_does_not_match_title_only(monkeypatch):
    monkeypatch.setattr(notepad_ops.win32gui, "GetTopWindow", lambda _: 100)
    monkeypatch.setattr(notepad_ops.win32gui, "GetWindow", lambda hwnd, _: 0)
    monkeypatch.setattr(notepad_ops.win32gui, "IsWindowVisible", lambda hwnd: True)
    monkeypatch.setattr(notepad_ops.win32gui, "GetClassName", lambda hwnd: "Chrome_WidgetWin_1")
    monkeypatch.setattr(notepad_ops, "_get_window_process_name", lambda hwnd: "chrome.exe")

    assert notepad_ops.find_most_recent_notepad_hwnd() is None

def test_find_most_recent_notepad_hwnd_matches_process_name(monkeypatch):
    monkeypatch.setattr(notepad_ops.win32gui, "GetTopWindow", lambda _: 100)
    monkeypatch.setattr(notepad_ops.win32gui, "GetWindow", lambda hwnd, _: 0)
    monkeypatch.setattr(notepad_ops.win32gui, "IsWindowVisible", lambda hwnd: True)
    monkeypatch.setattr(notepad_ops.win32gui, "GetClassName", lambda hwnd: "ApplicationFrameWindow")
    monkeypatch.setattr(notepad_ops, "_get_window_process_name", lambda hwnd: "notepad.exe")

    assert notepad_ops.find_most_recent_notepad_hwnd() == 100

def test_get_notepad_text_via_activate_copy_requires_focus(monkeypatch):
    restored = {}
    send_count = {"value": 0}
    foreground_calls = {"value": 0}

    def fake_get_foreground():
        foreground_calls["value"] += 1
        if foreground_calls["value"] == 1:
            return 999
        return 111

    monkeypatch.setattr(notepad_ops, "_backup_clipboard", lambda: [(13, "orig")])
    monkeypatch.setattr(notepad_ops, "_restore_clipboard", lambda data: restored.setdefault("data", data))
    monkeypatch.setattr(notepad_ops.win32gui, "GetForegroundWindow", fake_get_foreground)
    monkeypatch.setattr(notepad_ops.win32gui, "SetForegroundWindow", lambda hwnd: None)
    monkeypatch.setattr(notepad_ops.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        notepad_ops,
        "send_ctrl_combo",
        lambda _: send_count.__setitem__("value", send_count["value"] + 1),
    )

    with pytest.raises(RuntimeError, match="포커스를 확보하지 못해"):
        notepad_ops.get_notepad_text_via_activate_copy(222)

    assert send_count["value"] == 0
    assert restored["data"] == [(13, "orig")]
