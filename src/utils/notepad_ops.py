# -*- coding: utf-8 -*-
import logging
import time
import win32gui
import win32con
import win32clipboard
import ctypes
from .keyboard_ops import send_ctrl_combo

LOGGER = logging.getLogger(__name__)

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

OpenProcess = ctypes.windll.kernel32.OpenProcess
CloseHandle = ctypes.windll.kernel32.CloseHandle
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
QueryFullProcessImageNameW = ctypes.windll.kernel32.QueryFullProcessImageNameW

def _get_window_process_name(hwnd):
    # 윈도우 핸들에서 실행 파일명 추출
    pid = ctypes.c_ulong(0)
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ""

    process_handle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not process_handle:
        return ""

    try:
        buf_size = ctypes.c_ulong(260)
        exe_path = ctypes.create_unicode_buffer(buf_size.value)
        if not QueryFullProcessImageNameW(process_handle, 0, exe_path, ctypes.byref(buf_size)):
            return ""
        return exe_path.value.rsplit("\\", 1)[-1].lower()
    finally:
        CloseHandle(process_handle)

def _is_notepad_window(hwnd):
    # 고전/신형 메모장 모두 고려: 클래스명 또는 프로세스명으로 판정
    try:
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "Notepad":
            return True
    except:
        pass

    return _get_window_process_name(hwnd) == "notepad.exe"

def find_most_recent_notepad_hwnd():
    # Z-Order 기준으로 가장 최상단 메모장 찾기
    hwnd = win32gui.GetTopWindow(None)
    while hwnd:
        if win32gui.IsWindowVisible(hwnd) and _is_notepad_window(hwnd):
            return hwnd
        hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
    return None

def _open_clipboard_with_retry(max_retries=5, retry_delay=0.02):
    # 다른 프로세스가 점유 중일 수 있어 짧게 재시도
    for _ in range(max_retries):
        try:
            win32clipboard.OpenClipboard()
            return
        except:
            time.sleep(retry_delay)
    LOGGER.warning("클립보드 점유가 길어 마지막 OpenClipboard 재시도 수행")
    win32clipboard.OpenClipboard()

def _backup_clipboard():
    # 가능한 클립보드 포맷을 모두 백업
    formats = []
    try:
        _open_clipboard_with_retry()
        fmt = 0
        while True:
            fmt = win32clipboard.EnumClipboardFormats(fmt)
            if fmt == 0:
                break
            try:
                formats.append((fmt, win32clipboard.GetClipboardData(fmt)))
            except:
                LOGGER.debug("클립보드 포맷 백업 실패: %s", fmt)
                pass
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
    return formats

def _restore_clipboard(formats):
    # 백업된 클립보드 포맷 복원
    try:
        _open_clipboard_with_retry()
        win32clipboard.EmptyClipboard()
        for fmt, data in formats:
            try:
                win32clipboard.SetClipboardData(fmt, data)
            except:
                LOGGER.debug("클립보드 포맷 복원 실패: %s", fmt)
                pass
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass

def _get_clipboard_unicode_text():
    # 클립보드에서 텍스트 읽기
    text = ""
    try:
        _open_clipboard_with_retry()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
    return text

def find_text_control_in_notepad(notepad_hwnd):
    # 메모장 내부 텍스트 컨트롤 찾기
    candidates = []
    def enum_child(hwnd, _):
        try:
            cls = win32gui.GetClassName(hwnd).lower()
            if "edit" in cls or "richedit" in cls:
                candidates.append(hwnd)
        except:
            pass
        return True
    win32gui.EnumChildWindows(notepad_hwnd, enum_child, None)
    return candidates[0] if candidates else None

def get_window_text_via_message(hwnd):
    # WM_GETTEXT로 텍스트 읽기
    text_len = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
    if text_len <= 0: return ""
    buf = ctypes.create_unicode_buffer(text_len + 1)
    win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, text_len + 1, buf)
    return buf.value

def get_window_text_via_copy(hwnd):
    # 복사 메시지로 텍스트 읽기 (폴백)
    backup = _backup_clipboard()
    try:
        win32gui.SendMessage(hwnd, 0x00B1, 0, -1) # EM_SETSEL
        win32gui.SendMessage(hwnd, 0x0301, 0, 0)  # WM_COPY
        time.sleep(0.05)
        return _get_clipboard_unicode_text()
    finally:
        _restore_clipboard(backup)

def get_notepad_text_via_activate_copy(notepad_hwnd):
    # 메모장 활성화 후 복사 (최종 폴백)
    backup = _backup_clipboard()
    prev_foreground = win32gui.GetForegroundWindow()
    try:
        win32gui.SetForegroundWindow(notepad_hwnd)
        time.sleep(0.08)
        if win32gui.GetForegroundWindow() != notepad_hwnd:
            raise RuntimeError("메모장 포커스를 확보하지 못해 복사를 중단함")
        send_ctrl_combo(0x41) # A
        time.sleep(0.03)
        send_ctrl_combo(0x43) # C
        time.sleep(0.08)
        return _get_clipboard_unicode_text()
    finally:
        if prev_foreground:
            try:
                win32gui.SetForegroundWindow(prev_foreground)
            except:
                LOGGER.debug("원래 포그라운드 윈도우 복원 실패")
        _restore_clipboard(backup)
