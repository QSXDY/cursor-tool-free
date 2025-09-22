# -*- coding: utf-8 -*-
"""
图标绘制工具 - 创建简洁的矢量图标
"""

from PyQt6.QtGui import QIcon


class IconPainter:
    """图标绘制器，创建简洁的矢量图标"""

    @staticmethod
    def create_refresh_icon(size=20, color="#ffffff"):
        """创建刷新图标 - 使用PNG图标"""
        import os
        import sys

        try:
            # 获取图标路径
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

            icon_path = os.path.join(base_path, "resources", "icons", "refresh.png")

            if os.path.exists(icon_path):
                return QIcon(icon_path)
            else:
                print(f"⚠️ 刷新图标不存在: {icon_path}")
        except Exception as e:
            print(f"❌ 刷新图标加载失败: {e}")

        # 回退到文字图标
        return None

    @staticmethod
    def create_globe_icon(size=20, color="#ffffff"):
        """创建地球图标 - 使用PNG图标"""
        import os
        import sys

        try:
            # 获取图标路径
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

            icon_path = os.path.join(base_path, "resources", "icons", "globe.png")

            if os.path.exists(icon_path):
                return QIcon(icon_path)
            else:
                print(f"⚠️ 地球图标不存在: {icon_path}")
        except Exception as e:
            print(f"❌ 地球图标加载失败: {e}")

        # 回退到文字图标
        return None

    @staticmethod
    def create_plus_icon(size=20, color="#ffffff"):
        """创建加号图标 - 使用PNG图标"""
        import os
        import sys

        try:
            # 获取图标路径
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

            icon_path = os.path.join(base_path, "resources", "icons", "plus.png")

            if os.path.exists(icon_path):
                return QIcon(icon_path)
            else:
                print(f"⚠️ 加号图标不存在: {icon_path}")
        except Exception as e:
            print(f"❌ 加号图标加载失败: {e}")

        # 回退到文字图标
        return None
