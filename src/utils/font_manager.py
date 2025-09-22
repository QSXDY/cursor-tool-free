# -*- coding: utf-8 -*-
"""
字体管理模块 - 内置字体加载系统
"""

import os
import sys

from PyQt6.QtGui import QFontDatabase


class FontManager:
    """字体管理器，负责加载内置字体"""

    def __init__(self):
        self.loaded_fonts = {}
        self.base_path = self._get_base_path()

    def _get_base_path(self):
        """获取基础路径，兼容开发和打包环境"""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包环境
            return sys._MEIPASS
        else:
            # 开发环境
            return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    def load_font(self, font_name, font_file):
        """加载指定字体文件

        Args:
            font_name: 字体名称（用于标识）
            font_file: 字体文件路径（相对于resources/fonts/）

        Returns:
            str: 字体家族名称，失败返回None
        """
        font_path = os.path.join(self.base_path, "resources", "fonts", font_file)

        if not os.path.exists(font_path):
            print(f"⚠️ 字体文件不存在: {font_path}")
            return None

        try:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id == -1:
                print(f"❌ 字体加载失败: {font_name}")
                return None

            # 获取字体家族名称
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                family_name = font_families[0]
                self.loaded_fonts[font_name] = family_name
                print(f"✅ 字体加载成功: {font_name} -> {family_name}")
                return family_name
            else:
                print(f"❌ 无法获取字体家族: {font_name}")
                return None

        except Exception as e:
            print(f"❌ 字体加载异常: {font_name} - {e}")
            return None

    def get_font_family(self, font_name):
        """获取已加载字体的家族名称"""
        return self.loaded_fonts.get(font_name)

    def load_all_fonts(self):
        """加载所有内置字体"""
        fonts_to_load = [
            ("HarmonyOS_Sans_SC", "HarmonyOS_Sans_SC_Regular.ttf"),
            ("HarmonyOS_Sans_SC_Bold", "HarmonyOS_Sans_SC_Bold.ttf"),
        ]

        loaded_count = 0
        for font_name, font_file in fonts_to_load:
            if self.load_font(font_name, font_file):
                loaded_count += 1

        print(f"📦 字体加载完成: {loaded_count}/{len(fonts_to_load)} 个字体")
        return loaded_count > 0

    def get_primary_font_family(self):
        """获取主字体家族名称"""
        # 优先使用内置鸿蒙字体
        harmony_font = self.get_font_family("HarmonyOS_Sans_SC")
        if harmony_font:
            return harmony_font

        # 回退到系统字体
        fallback_fonts = [
            "HarmonyOS Sans SC",  # 系统鸿蒙字体
            "Microsoft YaHei",  # 微软雅黑
            "PingFang SC",  # 苹方
            "Segoe UI",  # Windows
            "Arial",  # 通用
        ]

        for font_name in fallback_fonts:
            if QFontDatabase.families().__contains__(font_name):
                print(f"🔄 使用系统字体: {font_name}")
                return font_name

        print("⚠️ 使用默认字体")
        return "Arial"


# 全局字体管理器实例
font_manager = FontManager()
