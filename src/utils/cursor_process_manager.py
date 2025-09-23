# -*- coding: utf-8 -*-
"""
Cursor进程管理模块 - 完整实现
"""

import logging
import sys


class CursorProcessManager:
    """Cursor进程管理器"""

    def __init__(self):
        """初始化Cursor进程管理器"""
        self.logger = logging.getLogger(__name__)
        self.platform = sys.platform

    def is_cursor_running(self) -> bool:
        """
        检查Cursor是否在运行 - 多平台支持

        Returns:
            bool: Cursor是否正在运行
        """
        try:
            import subprocess

            if self.platform == "darwin":
                # macOS平台检查
                result = subprocess.run(["ps", "-A"], capture_output=True, text=True)
                processes = result.stdout.splitlines()
                is_running = any("/Applications/Cursor.app/Contents/MacOS/Cursor" in proc for proc in processes)
                self.logger.info(f"Cursor主进程是否运行: {is_running}")
                return is_running

            elif self.platform == "win32":
                # Windows平台检查
                result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Cursor.exe"], capture_output=True, text=True)
                is_running = "Cursor.exe" in result.stdout
                self.logger.info(f"Cursor主进程是否运行: {is_running}")
                return is_running

            else:
                # Linux平台检查
                result = subprocess.run(["ps", "-A"], capture_output=True, text=True)
                processes = result.stdout.splitlines()
                is_running = any(
                    "cursor" in proc.lower()
                    and "cursorservice" not in proc.lower()
                    and (proc.lower().strip().endswith(" cursor") or "cursor.app" in proc.lower())
                    for proc in processes
                )
                self.logger.info(f"Cursor主进程是否运行: {is_running}")
                return is_running

        except Exception as e:
            self.logger.error(f"检查Cursor进程时出错: {str(e)}")
        return False

    def close_cursor(self, wait_time: float = 1.5) -> tuple:
        """
        关闭Cursor进程 - 完整实现

        Args:
            wait_time: 等待进程关闭的时间（秒）

        Returns:
            tuple: (是否成功, 结果消息)
        """
        try:
            import subprocess
            import time

            if not self.is_cursor_running():
                return (True, "未检测到Cursor进程，无需关闭")

            success = False
            message = ""

            if self.platform == "darwin":
                # macOS关闭逻辑
                result = subprocess.run(["pkill", "-x", "Cursor"], capture_output=True, text=True)
                if result.returncode == 0:
                    success = True
                    message = "已关闭Cursor进程"
                else:
                    # 尝试备用方法
                    result = subprocess.run(["killall", "Cursor"], capture_output=True, text=True)
                    if result.returncode == 0:
                        success = True
                        message = "已关闭Cursor进程"
                    else:
                        success = False
                        message = "关闭Cursor进程失败"

            elif self.platform == "win32":
                # Windows关闭逻辑
                result = subprocess.run(["taskkill", "/F", "/IM", "Cursor.exe"], capture_output=True, text=True)
                if result.returncode == 0:
                    success = True
                    message = "已关闭Cursor进程"
                else:
                    success = False
                    message = "关闭Cursor进程失败"

            else:
                # Linux关闭逻辑
                result = subprocess.run(["pkill", "-x", "cursor"], capture_output=True, text=True)
                if result.returncode == 0:
                    success = True
                    message = "已关闭Cursor进程"
                else:
                    # 尝试更广泛的匹配
                    result = subprocess.run(["pkill", "-f", "cursor"], capture_output=True, text=True)
                    if result.returncode == 0:
                        success = True
                        message = "已关闭Cursor进程"
                    else:
                        success = False
                        message = "关闭Cursor进程失败"

            # 等待并验证进程是否真的关闭
            if success and wait_time > 0:
                time.sleep(wait_time)
                if self.is_cursor_running():
                    self.logger.warning("Cursor进程可能未完全关闭")
                    message += "，但进程可能仍在运行"

            return (success, message)

        except Exception as e:
            error_message = f"关闭Cursor进程时出错: {str(e)}"
            self.logger.error(error_message)
            return (False, error_message)

    @staticmethod
    def kill_cursor_processes():
        """兼容性方法：关闭所有Cursor进程"""
        manager = CursorProcessManager()
        success, message = manager.close_cursor()
        return 1 if success else 0
