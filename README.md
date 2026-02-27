# GhostWriter

[![Windows](https://img.shields.io/badge/OS-Windows%2010%2F11-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Test](https://img.shields.io/badge/Test-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Status](https://img.shields.io/badge/Project-Active-2EA043)](https://github.com/snowfootprints/GhostWriter)

윈도우 메모장(Notepad)의 텍스트를 읽어 현재 커서 위치에 사람처럼 타이핑해주는 자동 입력 매크로입니다.  
시스템 트레이에서 실행되며, 단축키 `Ctrl + Shift + H` 한 번으로 동작합니다.

## 실행 흐름

1. `GhostWriter`를 실행하면 시스템 트레이에 상주합니다.
2. 가장 최근 메모장 창을 찾아 텍스트를 읽습니다.
3. 현재 활성 입력창에 유니코드(한글 포함)로 자연스럽게 타이핑합니다.

## 주요 기능

- 전역 단축키로 즉시 실행 (`Ctrl + Shift + H`)
- 최신 메모장 창 자동 탐지 (클래식/신형 Notepad 대응)
- 유니코드(한글 포함) 입력 지원
- 텍스트 읽기 다중 폴백:
  - `WM_GETTEXT`
  - 컨트롤 복사(`WM_COPY`)
  - 창 활성화 후 `Ctrl+A`, `Ctrl+C`
- 시스템 트레이 메뉴 제공:
  - `지금 실행 (테스트)`
  - `프로그램 종료`

## 프로젝트 구조

```text
GhostWriter/
├─ notepad_macro.py              # 메인 실행 스크립트
├─ src/
│  └─ utils/
│     ├─ win_api.py              # Win32 SendInput 구조체/API 정의
│     ├─ keyboard_ops.py         # 키 입력/유니코드 타이핑 로직
│     └─ notepad_ops.py          # 메모장 탐지/텍스트 추출 로직
├─ tests/                        # 단위 테스트 + 선택적 E2E 스모크 테스트
├─ requirements.txt              # Python 의존성
├─ GhostWriterMacro.spec         # PyInstaller 빌드 스펙
└─ HELP.txt                      # 사용자 도움말
```

## 빠른 시작

### 1) 개발 환경 실행

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python notepad_macro.py
```

실행 후 트레이 아이콘이 나타나면 준비 완료입니다.

### 2) 사용 방법

1. 메모장에 원하는 원문을 작성합니다.
2. 텍스트를 입력할 대상 창(채팅, 문서, 폼 등)에 커서를 둡니다.
3. `Ctrl + Shift + H`를 누르면 메모장 내용을 자동 입력합니다.

## 데모 / 스크린샷

- 데모 GIF를 추가하려면 `assets/demo.gif` 파일을 커밋한 뒤 아래 링크를 활성화하세요.
- 예시:

```md
![GhostWriter Demo](./assets/demo.gif)
```

## 테스트

```bash
pytest -q
```

데스크톱 환경이 필요한 E2E 스모크 테스트는 아래처럼 선택 실행합니다.

```bash
set RUN_GHOSTWRITER_E2E=1
pytest -q tests/test_e2e_smoke.py
```

## 빌드 (선택)

```bash
pyinstaller GhostWriterMacro.spec
```

빌드 결과물은 `dist/` 폴더에 생성됩니다.

## 배포 팁

- `dist/GhostWriterMacro/` 폴더 전체를 함께 배포하세요.
- 단일 `.exe`만 전달하면 누락 DLL로 실행 실패할 수 있습니다.

## 문제 해결

- 단축키가 동작하지 않으면:
  - 관리자 권한으로 실행
  - 앱 재시작 후 트레이 메뉴의 `지금 실행 (테스트)`로 확인
- 메모장 텍스트를 읽지 못하면:
  - 실제 `notepad.exe` 창인지 확인
  - 보안 정책/포커스 전환 차단 여부 확인

## 라이선스

원하시는 라이선스 정책(MIT 등)에 맞춰 `LICENSE` 파일을 추가해 사용하세요.
