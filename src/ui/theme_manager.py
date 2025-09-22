# -*- coding: utf-8 -*-
"""
主题管理系统 - 现代化UI主题
基于EasyShow H5主题配色系统的PyQt6实现
"""

from PyQt6.QtCore import QObject, pyqtSignal

# 移除未使用的导入
from PyQt6.QtWidgets import QApplication


class ThemeManager(QObject):
    """主题管理器 - 管理应用程序的主题切换"""

    theme_changed = pyqtSignal(str)  # 主题改变信号

    def __init__(self):
        super().__init__()
        self.current_theme = 'default'
        self.is_dark_mode = False

        # 定义主题配色
        self.themes = {
            'default': {
                'name': '现代简约',
                'description': '经典黑白灰配色',
                'colors': {
                    'primary': '#1c1f23',
                    'primary_hover': '#343a40',
                    'primary_active': '#495057',
                    'primary_light': '#999999',
                    'primary_lighter': '#f8f9fa',
                    'secondary': '#666666',
                    'secondary_hover': '#495057',
                    'secondary_active': '#343a40',
                    'secondary_light': '#ced4da',
                    'secondary_lighter': '#f0f0f0',
                    'accent': '#999999',
                    'accent_light': '#ced4da',
                    'accent_lighter': '#e9ecef',
                },
            },
            'theme-1': {
                'name': '温柔粉色',
                'description': '温柔优雅的粉色系',
                'colors': {
                    'primary': '#ff9ab7',
                    'primary_hover': '#ff8bb0',
                    'primary_active': '#ff7ca8',
                    'primary_light': '#ffb3cc',
                    'primary_lighter': '#fff0f5',
                    'secondary': '#ff6b9d',
                    'secondary_hover': '#ff5c94',
                    'secondary_active': '#ff4d8b',
                    'secondary_light': '#ffb3cc',
                    'secondary_lighter': '#ffe1ec',
                    'accent': '#ffcce0',
                    'accent_light': '#ffd6e7',
                    'accent_lighter': '#ffe8f0',
                },
            },
            'theme-2': {
                'name': '青绿清新',
                'description': '清新自然的青绿色系',
                'colors': {
                    'primary': '#00bcd4',
                    'primary_hover': '#00acc1',
                    'primary_active': '#0097a7',
                    'primary_light': '#80deea',
                    'primary_lighter': '#e0f2f1',
                    'secondary': '#009688',
                    'secondary_hover': '#00897b',
                    'secondary_active': '#00796b',
                    'secondary_light': '#80cbc4',
                    'secondary_lighter': '#e0f2f1',
                    'accent': '#26c6da',
                    'accent_light': '#80deea',
                    'accent_lighter': '#e0f7fa',
                },
            },
            'theme-3': {
                'name': '蓝紫科技',
                'description': '科技感的蓝紫色系',
                'colors': {
                    'primary': '#2196f3',
                    'primary_hover': '#1976d2',
                    'primary_active': '#1565c0',
                    'primary_light': '#90caf9',
                    'primary_lighter': '#e3f2fd',
                    'secondary': '#673ab7',
                    'secondary_hover': '#512da8',
                    'secondary_active': '#4527a0',
                    'secondary_light': '#b39ddb',
                    'secondary_lighter': '#ede7f6',
                    'accent': '#3f51b5',
                    'accent_light': '#9fa8da',
                    'accent_lighter': '#e8eaf6',
                },
            },
            'theme-4': {
                'name': '橙红活力',
                'description': '充满活力的橙红色系',
                'colors': {
                    'primary': '#ff5722',
                    'primary_hover': '#e64a19',
                    'primary_active': '#d84315',
                    'primary_light': '#ffab91',
                    'primary_lighter': '#fbe9e7',
                    'secondary': '#f44336',
                    'secondary_hover': '#d32f2f',
                    'secondary_active': '#c62828',
                    'secondary_light': '#ef9a9a',
                    'secondary_lighter': '#ffebee',
                    'accent': '#ff9800',
                    'accent_light': '#ffcc02',
                    'accent_lighter': '#fff3e0',
                },
            },
            'theme-5': {
                'name': '多彩柔和',
                'description': '柔和的多彩渐变系',
                'colors': {
                    'primary': '#93bff5',
                    'primary_hover': '#84b3f2',
                    'primary_active': '#75a7ef',
                    'primary_light': '#b5d0f7',
                    'primary_lighter': '#f5f7ff',
                    'secondary': '#8ee0f9',
                    'secondary_hover': '#7fdaf7',
                    'secondary_active': '#70d4f5',
                    'secondary_light': '#afedb2',
                    'secondary_lighter': '#e8f5e9',
                    'accent': '#d6a6ed',
                    'accent_light': '#e2b8f1',
                    'accent_lighter': '#f3e5f8',
                },
            },
        }

        # 通用色彩定义
        self.common_colors = {
            'white': '#ffffff',
            'black': '#1c1f23',
            'gray_50': '#f8f9fa',
            'gray_100': '#f0f0f0',
            'gray_200': '#e9ecef',
            'gray_300': '#dee2e6',
            'gray_400': '#ced4da',
            'gray_500': '#999999',
            'gray_600': '#666666',
            'gray_700': '#495057',
            'gray_800': '#343a40',
            'gray_900': '#1c1f23',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8',
        }

    def get_theme_list(self):
        """获取所有可用主题"""
        return [(key, theme['name'], theme['description']) for key, theme in self.themes.items()]

    def set_theme(self, theme_name, dark_mode=False):
        """设置主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.is_dark_mode = dark_mode
            self.theme_changed.emit(theme_name)
            return True
        return False

    def get_current_colors(self):
        """获取当前主题的颜色"""
        theme = self.themes.get(self.current_theme, self.themes['default'])
        colors = theme['colors'].copy()

        # 添加通用色彩
        colors.update(self.common_colors)

        # 深色模式处理
        if self.is_dark_mode:
            colors = self._apply_dark_mode(colors)

        return colors

    def _apply_dark_mode(self, colors):
        """应用深色模式"""
        # 深色模式下的基础调整
        dark_adjustments = {
            'white': '#1a1a1a',
            'black': '#f0f0f0',
            'gray_50': '#2c2c2c',
            'gray_100': '#383838',
            'gray_200': '#404040',
            'gray_300': '#4a4a4a',
            'gray_400': '#666666',
            'gray_500': '#888888',
            'gray_600': '#aaaaaa',
            'gray_700': '#cccccc',
            'gray_800': '#e0e0e0',
            'gray_900': '#f0f0f0',
        }

        colors.update(dark_adjustments)
        return colors

    def generate_qss(self):
        """生成PyQt6的QSS样式表"""
        colors = self.get_current_colors()

        qss = f"""
        /* ========================================
           Cursor Tool Free - 现代化主题样式
           当前主题: {self.themes[self.current_theme]['name']}
           ======================================== */

        /* 主窗口样式 */
        QMainWindow {{
            background-color: {colors['gray_50']};
            color: {colors['black']};
            font-family: 'HarmonyOS Sans SC', 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
        }}

        /* 移除全局QWidget样式，避免覆盖主题按钮 */

               /* 状态栏 */
               QStatusBar {{
                   background-color: {colors['gray_50']};
                   color: {colors['gray_700']};
                   border-top: 1px solid {colors['gray_200']};
                   padding: 4px 8px;
               }}

               /* 顶部标题区域 */
               QWidget[class="header"] {{
                   background-color: {colors['primary']};
                   border-bottom: 2px solid {colors['primary_hover']};
               }}

               QLabel[class="header-title"] {{
                   color: #ffffff;
                   font-size: 48px;
                   font-weight: bold;
                   font-family: 'HarmonyOS Sans SC', 'Microsoft YaHei', sans-serif;
               }}


               QPushButton[class="header-setting-button"] {{
                   background-color: rgba(255, 255, 255, 0.15);
                   color: #ffffff;
                   border: 1px solid rgba(255, 255, 255, 0.3);
                   border-radius: 6px;
                   font-size: 12px;
                   padding: 6px 12px;
               }}

               QPushButton[class="header-setting-button"]:hover {{
                   background-color: rgba(255, 255, 255, 0.2);
                   border: 1px solid rgba(255, 255, 255, 0.4);
               }}

               /* 主题色彩按钮 - 覆盖全局QPushButton样式 */
               QPushButton[class="theme-color-button"] {{
                   min-width: 16px;
                   max-width: 16px;
                   min-height: 16px;
                   max-height: 16px;
                   padding: 0px;
                   margin: 0px;
               }}

               /* 账号信息面板卡片样式 */
               QWidget[class="account-panel"] {{
                   background-color: rgba(255, 255, 255, 0.1);
                   border-bottom: 1px solid rgba(255, 255, 255, 0.2);
               }}

               QWidget[class="account-info-card"] {{
                   background-color: {colors['primary_lighter']} !important;
                   border-radius: 8px;
                   border: 1px solid {colors['primary_light']};
               }}

               QWidget[class="usage-info-card"] {{
                   background-color: {colors['primary_lighter']} !important;
                   border-radius: 8px;
                   border: 1px solid {colors['primary_light']};
               }}

               QLabel[class="account-email"] {{
                   color: {colors['primary']} !important;
                   font-weight: bold;
               }}

               QLabel[class="account-subscription"] {{
                   color: {colors['primary_hover']} !important;
                   font-weight: bold;
               }}

               QLabel[class="usage-amount"] {{
                   color: {colors['primary']} !important;
                   font-weight: bold;
               }}

               /* 图标按钮样式 - 方形微圆角，主题色底，白色图标 */
               QPushButton[class="icon-button-warning"] {{
                   background-color: {colors['primary']} !important;
                   color: #ffffff !important;
                   border: none !important;
                   border-radius: 6px !important;
                   padding: 0px !important;
                   min-width: 40px !important;
                   max-width: 40px !important;
                   min-height: 40px !important;
                   max-height: 40px !important;
               }}

               QPushButton[class="icon-button-warning"]:hover {{
                   background-color: {colors['primary_hover']} !important;
               }}

               QPushButton[class="icon-button-info"] {{
                   background-color: {colors['primary']} !important;
                   color: #ffffff !important;
                   border: none !important;
                   border-radius: 6px !important;
                   padding: 0px !important;
                   min-width: 40px !important;
                   max-width: 40px !important;
                   min-height: 40px !important;
                   max-height: 40px !important;
               }}

               QPushButton[class="icon-button-info"]:hover {{
                   background-color: {colors['primary_hover']} !important;
               }}

               QPushButton[class="icon-button-success"] {{
                   background-color: {colors['primary']} !important;
                   color: #ffffff !important;
                   border: none !important;
                   border-radius: 6px !important;
                   padding: 0px !important;
                   min-width: 40px !important;
                   max-width: 40px !important;
                   min-height: 40px !important;
                   max-height: 40px !important;
               }}

               QPushButton[class="icon-button-success"]:hover {{
                   background-color: {colors['primary_hover']} !important;
               }}

        /* 菜单栏 */
        QMenuBar {{
            background-color: {colors['white']};
            color: {colors['black']};
            border-bottom: 1px solid {colors['gray_200']};
            padding: 4px;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            border-radius: 6px;
            margin: 2px;
        }}

        QMenuBar::item:selected {{
            background-color: {colors['primary_lighter']};
            color: {colors['primary']};
        }}

        QMenu {{
            background-color: {colors['white']};
            border: 1px solid {colors['gray_200']};
            border-radius: 8px;
            padding: 8px;
        }}

        QMenu::item {{
            padding: 8px 16px;
            border-radius: 6px;
            margin: 2px;
        }}

        QMenu::item:selected {{
            background-color: {colors['primary_lighter']};
            color: {colors['primary']};
        }}

        /* 移除全局按钮样式，避免与class选择器冲突 */

        QPushButton:disabled {{
            background-color: {colors['gray_300']};
            color: {colors['gray_500']};
        }}

        /* 主要按钮 - 使用主题色 */
        QPushButton[class="primary"] {{
            background-color: {colors['primary']} !important;
            color: {colors['white']} !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }}

        QPushButton[class="primary"]:hover {{
            background-color: {colors['primary_hover']} !important;
        }}

        QPushButton[class="primary"]:pressed {{
            background-color: {colors['primary_active']} !important;
        }}

        /* 次要按钮 - 使用主题色 */
        QPushButton[class="secondary"] {{
            background-color: {colors['secondary']} !important;
            color: {colors['white']} !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }}

        QPushButton[class="secondary"]:hover {{
            background-color: {colors['secondary_hover']} !important;
        }}

        QPushButton[class="secondary"]:pressed {{
            background-color: {colors['secondary_active']} !important;
        }}

        /* 成功/信息/警告/危险按钮 */
        QPushButton[class="success"] {{
            background-color: {colors['success']} !important;
            color: {colors['white']} !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }}

        QPushButton[class="success"]:hover {{
            background-color: #218838 !important;
        }}

        QPushButton[class="info"] {{
            background-color: {colors['info']} !important;
            color: {colors['white']} !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }}

        QPushButton[class="info"]:hover {{
            background-color: #138496 !important;
        }}

        QPushButton[class="warning"] {{
            background-color: {colors['warning']} !important;
            color: {colors['black']} !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }}

        QPushButton[class="warning"]:hover {{
            background-color: #e0a800 !important;
        }}

        QPushButton[class="danger"] {{
            background-color: {colors['danger']} !important;
            color: {colors['white']} !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }}

        QPushButton[class="danger"]:hover {{
            background-color: #c82333 !important;
        }}

        /* 组框（卡片风格） */
        QGroupBox {{
            background-color: {colors['white']};
            border: 2px solid {colors['gray_200']};
            border-radius: 12px;
            padding: 16px;
            margin-top: 16px;
            font-weight: 600;
            color: {colors['gray_700']};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 4px 8px;
            background-color: {colors['white']};
            color: {colors['primary']};
            border-radius: 6px;
        }}

        /* 表格容器和卡片样式 */
        QWidget[class="table-container"] {{
            background-color: transparent;
        }}

        QWidget[class="table-card"] {{
            background-color: {colors['white']};
            border: 2px solid {colors['gray_200']};
            border-radius: 12px;
            margin: 0px;
        }}

        /* 表格样式 */
        QTableWidget {{
            background-color: {colors['white']};
            alternate-background-color: {colors['gray_50']};
            gridline-color: {colors['gray_300']};
            border: 1px solid {colors['gray_300']};
            border-radius: 0px;
            selection-background-color: {colors['primary_lighter']};
            selection-color: {colors['primary']};
            outline: none;
        }}

        QTableWidget::item {{
            padding: 0px;
            border-bottom: 0.5px solid {colors['gray_200']};
            border-right: 0.5px solid {colors['gray_200']};
            text-align: center;
        }}

        QTableWidget::item:alternate {{
            background-color: {colors['gray_50']};
        }}

        QTableWidget::item:hover {{
            background-color: {colors['primary_lighter']};
        }}

        QHeaderView::section {{
            background-color: {colors['gray_100']};
            color: {colors['gray_700']};
            padding: 15px 12px;
            border: none;
            border-bottom: 1px solid {colors['gray_300']};
            font-weight: 600;
            text-align: center;
        }}

        QTableWidget::item:selected {{
            background-color: {colors['primary_lighter']};
            color: {colors['primary']};
        }}

        /* 输入框样式 */
        QLineEdit, QPlainTextEdit {{
            background-color: {colors['white']};
            color: {colors['black']};
            border: 1px solid {colors['gray_200']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
        }}

        QLineEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {colors['primary']};
        }}

        /* 复选框样式 */
        QCheckBox {{
            color: {colors['black']};
            font-size: 14px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors['gray_300']};
            border-radius: 4px;
            background-color: {colors['white']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
            /* 复选框图标 - 简化 */
        }}

        /* 标签样式 */
        QLabel {{
            color: {colors['black']};
            font-size: 14px;
        }}

        QLabel[class="title"] {{
            font-size: 18px;
            font-weight: 600;
            color: {colors['primary']};
        }}

        QLabel[class="subtitle"] {{
            font-size: 16px;
            font-weight: 500;
            color: {colors['gray_700']};
        }}

        QLabel[class="caption"] {{
            font-size: 12px;
            color: {colors['gray_500']};
        }}

        /* 对话框样式 */
        QDialog {{
            background-color: {colors['white']};
            border-radius: 12px;
            color: {colors['black']};
            font-family: 'HarmonyOS Sans SC', 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
        }}

        /* 导入对话框特殊样式 */
        QLabel[class="tip-info"] {{
            background-color: {colors['primary_lighter']};
            border-left: 4px solid {colors['primary']};
            color: {colors['primary']};
            padding: 12px;
            margin: 8px 0px;
            border-radius: 4px;
            font-size: 11px;
        }}

        QPlainTextEdit[class="result-success"] {{
            background-color: {colors['success']};
            color: {colors['white']};
            border: 2px solid {colors['success']};
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }}

        QPlainTextEdit[class="result-progress"] {{
            background-color: {colors['warning']};
            color: {colors['black']};
            border: 2px solid {colors['warning']};
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }}

        QPlainTextEdit[class="result-error"] {{
            background-color: {colors['danger']};
            color: {colors['white']};
            border: 2px solid {colors['danger']};
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }}

        QMessageBox {{
            background-color: {colors['white']};
            color: {colors['black']};
        }}

        QMessageBox QPushButton {{
            min-width: 80px;
            padding: 8px 16px;
        }}

        /* 分割器 */
        QSplitter::handle {{
            background-color: {colors['gray_200']};
        }}

        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        QSplitter::handle:vertical {{
            height: 2px;
        }}

        /* 滚动条 */
        QScrollBar:vertical {{
            background-color: {colors['gray_100']};
            width: 6px;
            border-radius: 3px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors['gray_400']};
            border-radius: 3px;
            min-height: 15px;
            margin: 1px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {colors['gray_500']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        /* 工具提示 */
        QToolTip {{
            background-color: {colors['gray_800']};
            color: {colors['white']};
            border: 1px solid {colors['gray_600']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 12px;
        }}
        """

        return qss

    def apply_theme(self, app=None):
        """应用主题到应用程序"""
        if app is None:
            app = QApplication.instance()

        if app:
            qss = self.generate_qss()
            app.setStyleSheet(qss)
            print(f"✅ 已应用主题: {self.themes[self.current_theme]['name']}")

    def toggle_dark_mode(self):
        """切换深色模式"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        return self.is_dark_mode
