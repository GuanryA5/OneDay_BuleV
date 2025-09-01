# -*- coding: utf-8 -*-
"""
SystemAdapter - 跨平台系统能力适配层

在 WSL2 环境下避免直接调用 OS 级 GUI/输入相关 API；
在 Windows 环境下提供真实实现。
"""

from __future__ import annotations

import platform
from typing import Any


class SystemAdapter:
    """系统调用适配器抽象基类"""

    def screenshot(self, region: tuple[int, int, int, int] | None = None) -> None:
        """截图。
        region: (x, y, w, h) 或 None 表示全屏
        返回: PIL.Image.Image
        """
        raise NotImplementedError

    def click(self, x: int, y: int, button: str = "left") -> None:
        """鼠标点击。"""
        raise NotImplementedError

    def get_screen_size(self) -> tuple[int, int]:
        """获取屏幕尺寸 (width, height)。"""
        raise NotImplementedError


class WindowsAdapter(SystemAdapter):
    """Windows 实现，使用 Pillow.ImageGrab 与 pyautogui。"""

    def _ensure_pyautogui(self) -> Any:
        import pyautogui  # type: ignore

        # 合理的默认安全设置
        pyautogui.FAILSAFE = True
        if getattr(pyautogui, "PAUSE", None) is not None:
            pyautogui.PAUSE = 0.1
        return pyautogui

    def screenshot(self, region: tuple[int, int, int, int] | None = None) -> Any:
        from PIL import ImageGrab

        bbox = None
        if region is not None:
            x, y, w, h = region
            bbox = (x, y, x + w, y + h)
        return ImageGrab.grab(bbox=bbox)

    def click(self, x: int, y: int, button: str = "left") -> None:
        pyautogui = self._ensure_pyautogui()
        # 归一化按键
        mapping = {
            "left": "left",
            "right": "right",
            "middle": "middle",
            "primary": "left",
            "secondary": "right",
        }
        btn = mapping.get(button.lower(), "left")
        pyautogui.click(x, y, button=btn)

    def get_screen_size(self) -> tuple[int, int]:
        pyautogui = self._ensure_pyautogui()
        size = pyautogui.size()
        return int(size.width), int(size.height)


class WSLAdapter(SystemAdapter):
    """WSL2 实现：不提供真实系统调用，抛出清晰异常。"""

    def screenshot(self, region: tuple[int, int, int, int] | None = None) -> None:
        raise RuntimeError

    def click(self, x: int, y: int, button: str = "left") -> None:
        raise RuntimeError

    def get_screen_size(self) -> tuple[int, int]:
        raise RuntimeError


def get_system_adapter() -> SystemAdapter:
    """根据平台返回合适的适配器实例。"""
    if platform.system() == "Windows":
        return WindowsAdapter()
    return WSLAdapter()
