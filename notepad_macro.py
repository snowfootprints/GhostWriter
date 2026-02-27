# -*- coding: utf-8 -*-
import logging
import threading
import keyboard
import pystray
from PIL import Image, ImageDraw
from src.utils.keyboard_ops import type_unicode_text_human_like, send_vk
from src.utils.notepad_ops import (
    find_most_recent_notepad_hwnd,
    find_text_control_in_notepad,
    get_window_text_via_message,
    get_window_text_via_copy,
    get_notepad_text_via_activate_copy
)

# 전역 상태
stop_event = threading.Event()
typing_lock = threading.Lock()
tray_icon = None
LOGGER = logging.getLogger(__name__)

def get_notepad_text():
    # 메모장 텍스트 읽기 통합 로직
    hwnd = find_most_recent_notepad_hwnd()
    if not hwnd: raise RuntimeError("메모장을 찾을 수 없음")
    
    text_hwnd = find_text_control_in_notepad(hwnd)
    if not text_hwnd:
        text = get_notepad_text_via_activate_copy(hwnd)
        if text: return text
        raise RuntimeError("텍스트 컨트롤 탐색 실패")
        
    text = get_window_text_via_message(text_hwnd)
    if not text:
        text = get_window_text_via_copy(text_hwnd)
    if not text:
        text = get_notepad_text_via_activate_copy(hwnd)
        
    if text: return text
    raise RuntimeError("텍스트 읽기 최종 실패")

def on_hotkey():
    # 핫키 발동 시 동작
    lock_acquired = typing_lock.acquire(blocking=False)
    if stop_event.is_set() or not lock_acquired:
        LOGGER.debug("요청 무시: stop_event=%s, lock_acquired=%s", stop_event.is_set(), lock_acquired)
        if lock_acquired:
            typing_lock.release()
        return
    try:
        LOGGER.info("핫키 동작 시작")
        text = get_notepad_text()
        if not text: return
        
        # Modifier 키 해제 (입력 간섭 방지)
        send_vk(0x11, key_up=True) # Ctrl
        send_vk(0x10, key_up=True) # Shift
        
        type_unicode_text_human_like(text, should_stop=stop_event.is_set)
    except Exception as e:
        LOGGER.exception("핫키 동작 실패: %s", e)
    finally:
        typing_lock.release()

def create_tray_image():
    # 트레이 아이콘 생성
    img = Image.new("RGBA", (64, 64), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((8, 8, 56, 56), radius=10, fill=(70, 130, 180, 255))
    draw.text((20, 18), "H", fill=(255, 255, 255, 255))
    return img

def shutdown_program(icon, _):
    # 프로그램 종료
    LOGGER.info("종료 요청 수신")
    stop_event.set()
    keyboard.unhook_all_hotkeys()
    icon.stop()

def main():
    # 메인 실행부
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    keyboard.add_hotkey("ctrl+shift+h", lambda: threading.Thread(target=on_hotkey, daemon=True).start())
    
    menu = pystray.Menu(
        pystray.MenuItem("지금 실행 (테스트)", lambda icon, item: threading.Thread(target=on_hotkey, daemon=True).start()),
        pystray.MenuItem("프로그램 종료", shutdown_program)
    )
    icon = pystray.Icon("NotepadMacro", create_tray_image(), "Notepad Macro (Ctrl+Shift+H)", menu)
    icon.run()

if __name__ == "__main__":
    main()
