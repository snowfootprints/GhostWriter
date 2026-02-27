# -*- coding: utf-8 -*-
import ctypes
import time
from ctypes import wintypes
from .win_api import SendInput, INPUT, _INPUT_UNION, KEYBDINPUT, INPUT_KEYBOARD, KEYEVENTF_UNICODE, KEYEVENTF_KEYUP

def _send_unicode_utf16_unit(unit):
    # UTF-16 유닛 전송 (한글 대응)
    extra = ctypes.pointer(wintypes.ULONG(0))
    down = INPUT(
        type=INPUT_KEYBOARD,
        union=_INPUT_UNION(
            ki=KEYBDINPUT(wVk=0, wScan=unit, dwFlags=KEYEVENTF_UNICODE, time=0, dwExtraInfo=extra)
        ),
    )
    up = INPUT(
        type=INPUT_KEYBOARD,
        union=_INPUT_UNION(
            ki=KEYBDINPUT(wVk=0, wScan=unit, dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, time=0, dwExtraInfo=extra)
        ),
    )
    SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))

def send_vk(vk_code, key_up=False):
    # 가상키 전송
    extra = ctypes.pointer(wintypes.ULONG(0))
    flags = KEYEVENTF_KEYUP if key_up else 0
    inp = INPUT(
        type=INPUT_KEYBOARD,
        union=_INPUT_UNION(
            ki=KEYBDINPUT(wVk=vk_code, wScan=0, dwFlags=flags, time=0, dwExtraInfo=extra)
        ),
    )
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def send_ctrl_combo(vk_code):
    # Ctrl 키 조합 전송
    VK_CONTROL = 0x11
    send_vk(VK_CONTROL, key_up=False)
    send_vk(vk_code, key_up=False)
    send_vk(vk_code, key_up=True)
    send_vk(VK_CONTROL, key_up=True)

def type_unicode_text_human_like(text, delay=0.05, should_stop=None):
    # 사람이 입력하는 것처럼 텍스트 전송
    # 보안: 입력값 길이 제한 및 이상 문자 필터링 고려 필요
    if len(text) > 10000:
        print("[경고] 텍스트가 너무 길어서 잘림")
        text = text[:10000]
        
    for ch in text:
        if should_stop and should_stop():
            break
        data = ch.encode("utf-16-le")
        for i in range(0, len(data), 2):
            if should_stop and should_stop():
                return
            unit = int.from_bytes(data[i:i + 2], "little")
            _send_unicode_utf16_unit(unit)
        time.sleep(delay)
