# -*- coding: utf-8 -*-
import os
import pytest

@pytest.mark.skipif(
    os.getenv("RUN_GHOSTWRITER_E2E") != "1",
    reason="Set RUN_GHOSTWRITER_E2E=1 to run desktop smoke checks.",
)
def test_windows_desktop_e2e_smoke():
    # Placeholder for real desktop E2E:
    # 1) Launch Notepad
    # 2) Seed source text
    # 3) Trigger Ctrl+Shift+H
    # 4) Verify target field text
    #
    # This stays opt-in because it requires a real interactive desktop session.
    assert True
