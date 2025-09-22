# -*- coding: utf-8 -*-
"""
Cursor版本管理模块
"""

import json
import os
import platform


class CursorVersionDetector:
    """Cursor版本检测器"""

    @staticmethod
    def get_cursor_paths():
        """获取Cursor路径"""
        try:
            from ..config import Config
        except ImportError:
            # 直接导入模式（用于测试）
            import sys

            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from config import Config

        config = Config.get_instance()
        system = platform.system()

        # 1. 优先使用配置中保存的路径
        custom_path = config.get("cursor", "app_path")
        if custom_path and os.path.exists(custom_path):
            possible_paths = [custom_path]
        else:
            # 2. 使用默认路径
            if system == "Windows":
                possible_paths = [
                    os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "Cursor"),
                    os.path.join(os.getenv("PROGRAMFILES", ""), "Cursor"),
                    os.path.join(os.getenv("PROGRAMFILES(X86)", ""), "Cursor"),
                ]
            elif system == "Darwin":
                possible_paths = [
                    # 标准安装
                    "/Applications/Cursor.app/Contents/Resources/app",
                    # 用户安装
                    os.path.expanduser("~/Applications/Cursor.app/Contents/Resources/app"),
                    # Homebrew安装
                    "/usr/local/Caskroom/cursor/latest/Cursor.app/Contents/Resources/app",
                    "/opt/homebrew/Caskroom/cursor/latest/Cursor.app/Contents/Resources/app",
                    # 下载位置
                    os.path.expanduser("~/Downloads/Cursor.app/Contents/Resources/app"),
                    os.path.expanduser("~/Desktop/Cursor.app/Contents/Resources/app"),
                ]
            else:
                # Linux平台 - 完整路径支持
                possible_paths = [
                    # AppImage便携版本
                    os.path.expanduser("~/Applications/Cursor.AppImage"),
                    os.path.expanduser("~/.local/bin/cursor"),
                    # 系统安装版本
                    "/usr/local/bin/cursor",
                    "/usr/bin/cursor",
                    "/opt/cursor/cursor",
                    # Snap包管理
                    "/snap/bin/cursor",
                    # 用户自定义安装
                    os.path.expanduser("~/.local/share/cursor"),
                    os.path.expanduser("~/cursor"),
                    os.path.expanduser("~/Downloads/cursor"),
                    # Flatpak安装
                    os.path.expanduser("~/.var/app/com.cursor.Cursor"),
                ]

        for base_path in possible_paths:
            if "*" in base_path:
                continue  # 跳过通配符路径
            package_json_path = os.path.join(base_path, "resources", "app", "package.json")
            main_js_path = os.path.join(base_path, "resources", "app", "out", "main.js")

            if os.path.exists(package_json_path) and os.path.exists(main_js_path):
                return {
                    "base_path": base_path,
                    "package_json": package_json_path,
                    "main_js": main_js_path,
                    "workbench_js": os.path.join(
                        base_path, "resources", "app", "out", "vs", "workbench", "workbench.desktop.main.js"
                    ),
                }

        return None

    @staticmethod
    def get_cursor_version(formatted=False):
        """获取Cursor版本"""
        paths = CursorVersionDetector.get_cursor_paths()
        if not paths:
            print("⚠️ 未找到Cursor安装路径")
            return None

        try:
            with open(paths["package_json"], "r", encoding="utf-8") as f:
                package_data = json.load(f)
                version = package_data.get("version", "")

                if not version:
                    print("⚠️ package.json中未找到version字段")
                    return None

                if formatted:
                    # 1.3.9 -> v139
                    parts = version.split(".")
                    if len(parts) >= 3:
                        formatted_version = f"v{parts[0]}{parts[1]}{parts[2]}"
                        print(f"✅ 检测到Cursor版本: {version} -> {formatted_version}")
                        return formatted_version

                print(f"✅ 检测到Cursor版本: {version}")
                return version

        except Exception as e:
            print(f"❌ 获取Cursor版本失败: {e}")
            return None

    @staticmethod
    def increment_version(version_str):
        """版本号递增 - v139 → v140 → v141"""
        if not version_str.startswith("v"):
            return None

        try:
            # 移除v前缀并解析：v139 -> 139
            version_num = version_str[1:]

            # 根据长度解析版本号
            if len(version_num) == 3:
                # v139 -> 1.3.9
                major = int(version_num[0])
                minor = int(version_num[1])
                patch = int(version_num[2])
            elif len(version_num) == 4:
                # v0394 -> 0.39.4
                major = int(version_num[0])
                minor = int(version_num[1:3])
                patch = int(version_num[3])
            else:
                # 未知格式，简单递增
                num = int(version_num)
                return f"v{num + 1}"

            # 递增逻辑
            if patch < 9:
                patch += 1
            else:
                patch = 0
                if minor < 9:
                    minor += 1
                else:
                    minor = 0
                    major += 1

            # 重新格式化
            if major == 0:
                return f"v{major}{minor:02d}{patch}"  # 0.39.4 -> v0394
            else:
                return f"v{major}{minor}{patch}"  # 1.3.9 -> v139

        except Exception as e:
            print(f"❌ 版本号递增失败: {e}")
            return None

    @staticmethod
    def _format_version(version: str) -> str:
        """将版本号格式化为v139格式"""
        major, minor, patch = version.split(".")[:3]
        return f"v{major}{minor}{patch}"

    @staticmethod
    def is_cursor_installed():
        """检查Cursor是否已安装"""
        paths = CursorVersionDetector.get_cursor_paths()
        return bool(paths and os.path.exists(paths["package_json"]))

    @staticmethod
    def get_version_info():
        """获取完整的版本信息"""
        raw_version = CursorVersionDetector.get_cursor_version(formatted=False)
        formatted_version = CursorVersionDetector.get_cursor_version(formatted=True)
        installed = CursorVersionDetector.is_cursor_installed()
        paths = CursorVersionDetector.get_cursor_paths()

        return {
            "installed": installed,
            "version_raw": raw_version,
            "version_formatted": formatted_version,
            "paths": paths,
        }
