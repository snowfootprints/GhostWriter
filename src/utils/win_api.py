# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes

# ============================================
# Windows SendInput용 구조체/상상수 정의
# ============================================

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

class KEYBDINPUT(ctypes.Structure):
    # 키보드 입력 구조체
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]

class _INPUT_UNION(ctypes.Union):
    # 입력 합체 구조체
    _fields_ = [("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    # 입력 구조체
    _fields_ = [("type", wintypes.DWORD), ("union", _INPUT_UNION)]

class MSG(ctypes.Structure):
    # 메시지 구조체
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
        ("lPrivate", wintypes.DWORD),
    ]

# Win32 API 함수 정의
SendInput = ctypes.windll.user32.SendInput
MessageBoxW = ctypes.windll.user32.MessageBoxW
RegisterHotKey = ctypes.windll.user32.RegisterHotKey
UnregisterHotKey = ctypes.windll.user32.UnregisterHotKey
GetMessageW = ctypes.windll.user32.GetMessageW
TranslateMessage = ctypes.windll.user32.TranslateMessage
DispatchMessageW = ctypes.windll.user32.DispatchMessageW
PostThreadMessageW = ctypes.windll.user32.PostThreadMessageW
