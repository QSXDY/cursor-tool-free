# -*- coding: utf-8 -*-
"""
主题切换器控件 - 用户界面主题选择
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .theme_manager import ThemeManager


class ThemeSwitcherWidget(QWidget):
    """主题切换器控件"""

    theme_changed = pyqtSignal(str)

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 标题
        title = QLabel("🎨 界面主题")
        title.setProperty("class", "title")
        layout.addWidget(title)

        # 主题选择器
        themes_layout = QHBoxLayout()
        themes_layout.setSpacing(8)

        # 创建主题选项按钮
        self.theme_buttons = {}
        themes = self.theme_manager.get_theme_list()

        for theme_id, name, description in themes:
            button = ThemeOptionButton(theme_id, name, description)
            button.clicked.connect(lambda checked, tid=theme_id: self.switch_theme(tid))
            self.theme_buttons[theme_id] = button
            themes_layout.addWidget(button)

        themes_layout.addStretch()
        layout.addLayout(themes_layout)

        # 深色模式切换
        dark_mode_layout = QHBoxLayout()
        self.dark_mode_btn = QPushButton("🌙 深色模式")
        self.dark_mode_btn.setCheckable(True)
        self.dark_mode_btn.toggled.connect(self.toggle_dark_mode)
        dark_mode_layout.addWidget(self.dark_mode_btn)
        dark_mode_layout.addStretch()

        layout.addLayout(dark_mode_layout)

        # 设置当前主题为激活状态
        self.update_active_theme()

    def switch_theme(self, theme_id):
        """切换主题"""
        success = self.theme_manager.set_theme(theme_id, self.theme_manager.is_dark_mode)
        if success:
            self.update_active_theme()
            self.theme_changed.emit(theme_id)

    def toggle_dark_mode(self, checked):
        """切换深色模式"""
        self.theme_manager.is_dark_mode = checked
        self.theme_manager.apply_theme()

        # 更新按钮文本
        if checked:
            self.dark_mode_btn.setText("☀️ 浅色模式")
        else:
            self.dark_mode_btn.setText("🌙 深色模式")

    def update_active_theme(self):
        """更新激活的主题按钮"""
        for theme_id, button in self.theme_buttons.items():
            button.set_active(theme_id == self.theme_manager.current_theme)


class ThemeOptionButton(QPushButton):
    """主题选项按钮"""

    def __init__(self, theme_id, name, description, parent=None):
        super().__init__(parent)
        self.theme_id = theme_id
        self.theme_name = name
        self.description = description
        self.is_active = False

        self.setFixedSize(50, 50)
        self.setToolTip(f"{name}\n{description}")

        # 设置主题预览颜色
        self.preview_colors = self._get_preview_colors(theme_id)

    def _get_preview_colors(self, theme_id):
        """获取主题预览颜色"""
        color_map = {
            'default': ['#1c1f23', '#999999'],
            'theme-1': ['#ff9ab7', '#ff6b9d'],
            'theme-2': ['#00bcd4', '#009688'],
            'theme-3': ['#2196f3', '#673ab7'],
            'theme-4': ['#ff5722', '#f44336'],
            'theme-5': ['#93bff5', '#d6a6ed'],
        }
        return color_map.get(theme_id, ['#1c1f23', '#999999'])

    def set_active(self, active):
        """设置激活状态"""
        self.is_active = active
        self.update()

    def paintEvent(self, event):
        """自定义绘制主题预览"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(4, 4, -4, -4)

        # 绘制渐变背景
        color1 = QColor(self.preview_colors[0])
        color2 = QColor(self.preview_colors[1])

        painter.fillRect(rect.adjusted(0, 0, -rect.width() // 2, 0), color1)
        painter.fillRect(rect.adjusted(rect.width() // 2, 0, 0, 0), color2)

        # 激活状态边框
        if self.is_active:
            pen = QPen(QColor("#333333"), 3)
            painter.setPen(pen)
            painter.drawRoundedRect(rect, 8, 8)

        painter.end()
