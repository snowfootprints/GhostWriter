#Requires AutoHotkey v2.0
#SingleInstance Force
Persistent

; ============================================================
; Notepad -> Type Macro (Ctrl+Shift+H)
; - 최근 활성(화면 상단 Z-order) Notepad 창의 텍스트를 읽음
; - 현재 커서 위치에 유니코드 텍스트를 한 글자씩 타이핑
; - 글자당 50ms 딜레이
; ============================================================

A_IconTip := "Notepad Macro (Ctrl+Shift+H)"
A_TrayMenu.Delete()
A_TrayMenu.Add("지금 실행 (테스트)", (*) => RunMacro())
A_TrayMenu.Add()
A_TrayMenu.Add("프로그램 종료", (*) => ExitApp())
A_TrayMenu.Default := "지금 실행 (테스트)"

^+h:: {
    RunMacro()
}

RunMacro() {
    static isRunning := false
    if isRunning {
        return
    }
    isRunning := true

    try {
        text := GetMostRecentNotepadText()
        if (text = "") {
            ; 메모장 텍스트가 비었거나 찾지 못한 경우 조용히 종료
            return
        }

        ; 단축키 modifier 해제 대기
        KeyWait("Ctrl")
        KeyWait("Shift")
        Sleep(30)

        ; 한 글자씩 유니코드 입력 (한글 포함)
        for ch in StrSplit(text) {
            SendText(ch)
            Sleep(50)
        }
    } catch {
        ; 오류 시에도 크래시 없이 복귀
    } finally {
        isRunning := false
    }
}

GetMostRecentNotepadText() {
    hwnd := FindMostRecentNotepadHwnd()
    if !hwnd {
        return ""
    }

    ; 1) 컨트롤 직접 읽기 시도
    txt := ""
    for ctrlName in ["Edit1", "RichEditD2DPT1", "RichEdit20W1"] {
        try {
            txt := ControlGetText(ctrlName, "ahk_id " hwnd)
            if (txt != "") {
                return txt
            }
        }
    }

    ; 2) 폴백: 메모장 활성화 후 Ctrl+A / Ctrl+C로 클립보드 읽기
    oldClip := A_Clipboard
    oldWin := WinExist("A")

    try {
        A_Clipboard := ""
        WinActivate("ahk_id " hwnd)
        WinWaitActive("ahk_id " hwnd, , 0.4)
        Sleep(60)

        Send("^a")
        Sleep(20)
        Send("^c")
        if !ClipWait(0.5) {
            return ""
        }
        copied := A_Clipboard
    } catch {
        copied := ""
    }

    ; 원래 창 복귀 시도
    try {
        if oldWin {
            WinActivate("ahk_id " oldWin)
        }
    }

    ; 클립보드 복구
    A_Clipboard := oldClip
    return copied
}

FindMostRecentNotepadHwnd() {
    ; WinGetList는 Z-order(위에서 아래) 기준으로 반환됨
    list := WinGetList()
    for hwnd in list {
        try {
            if !WinExist("ahk_id " hwnd) {
                continue
            }
            if !DllCall("user32\IsWindowVisible", "ptr", hwnd, "int") {
                continue
            }
            class := WinGetClass("ahk_id " hwnd)
            title := WinGetTitle("ahk_id " hwnd)

            if (class = "Notepad") {
                return hwnd
            }
            if InStr(StrLower(title), "notepad") || InStr(title, "메모장") {
                return hwnd
            }
        }
    }
    return 0
}
