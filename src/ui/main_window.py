# -*- coding: utf-8 -*-
"""
主窗口模块 - 应用程序主界面
"""

import json
import os
import sys
from datetime import datetime

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

# 导入新的模块化组件
from ..config import Config
from ..utils.browser_manager import BrowserManager
from ..utils.cursor_manager import CursorManager
from ..utils.cursor_process_manager import CursorProcessManager
from ..utils.single_refresh_thread import SingleRefreshThread
from ..utils.usage_update_thread import UsageUpdateThread


class CursorAccountManagerPro(QMainWindow):
    """Cursor账号管理器专业版 - 功能完整的管理界面"""

    def __init__(self):
        super().__init__()

        # 🔧 适配新架构：使用Config替代AccountDatabase
        self.config = Config.get_instance()
        self.cursor_manager = CursorManager(self.config)

        # 线程管理
        self.apply_threads = {}  # 应用线程字典，按行号索引
        self.refresh_threads = {}  # 🆕 单账号刷新线程字典，按行号索引

        # 使用额度更新相关
        self._is_updating = False
        self._current_update_thread = None

        # 路径配置
        self.cursor_installation_path = None

        self.setWindowTitle("Cursor Tool Free - 免费精简版")
        self.setGeometry(100, 100, 900, 600)

        self.init_ui()
        self.create_menu_bar()
        self.load_accounts()

        # 每次启动都检查Cursor路径配置（严格模式，跨平台）
        QTimer.singleShot(1000, self.check_cursor_installation_paths)

        # 启动时自动刷新当前账号信息 - 让用户立即看到当前状态
        QTimer.singleShot(2000, self.update_usage_data)

    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 🔝 当前账号信息面板 - 用户要求放最上面
        current_account_panel = self.create_current_account_panel()
        main_layout.addWidget(current_account_panel)

        # 🔧 账号列表工具栏 - 用户要求放在当前账号信息下面
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)

        # 主表格
        self.create_account_table()
        main_layout.addWidget(self.account_table)

        # 底部按钮栏
        bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(bottom_bar)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # 应用样式
        self.setStyleSheet(self.get_professional_style())

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #3c3c3c;")

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(15, 10, 15, 10)

        # 标题
        title_label = QLabel("账号列表")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)

        # 导入按钮
        import_btn = QPushButton("📥 导入账号")
        import_btn.clicked.connect(self.show_import_dialog)
        import_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #5294e2;
                border: none;
                font-size: 14px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                color: #5c9eec;
                background-color: rgba(82, 148, 226, 0.1);
            }
        """
        )
        layout.addWidget(import_btn)

        # 全选Pro
        self.select_pro_cb = QCheckBox("🎯 全选Pro")
        self.select_pro_cb.setToolTip("勾选所有pro专业版状态的账号")
        self.select_pro_cb.setStyleSheet(
            """
            QCheckBox {
                color: #4caf50;
                font-size: 14px;
                padding: 5px;
            }
            QCheckBox:hover {
                color: #66bb6a;
            }
        """
        )
        self.select_pro_cb.stateChanged.connect(self.select_all_pro)
        layout.addWidget(self.select_pro_cb)

        layout.addStretch()

        layout.addSpacing(10)

        # 统计信息
        self.stats_label = QLabel("已应用: 0 | 待应用: 0")
        self.stats_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.stats_label)

        return toolbar

    def create_current_account_panel(self):
        """创建当前账号信息面板的顶部信息显示"""
        panel = QWidget()
        panel.setFixedHeight(80)
        panel.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e2e2e, stop:1 #1e1e1e);
                border-bottom: 1px solid #3c3c3c;
            }
        """
        )

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)

        # 左侧：当前账号信息
        account_info_container = QWidget()
        account_info_layout = QVBoxLayout(account_info_container)
        account_info_layout.setContentsMargins(0, 0, 0, 0)
        account_info_layout.setSpacing(2)

        # 当前邮箱标签 - 和原项目完全一样的样式
        self.current_email_label = QLabel("当前账号: 检测中...")
        self.current_email_label.setFont(QFont("", 12, QFont.Weight.Bold))
        self.current_email_label.setStyleSheet("color: white;")

        # 订阅信息标签
        self.current_subscription_label = QLabel("订阅类型: 查询中...")
        self.current_subscription_label.setFont(QFont("", 10))
        self.current_subscription_label.setStyleSheet("color: #cccccc;")

        account_info_layout.addWidget(self.current_email_label)
        account_info_layout.addWidget(self.current_subscription_label)

        # 右侧：使用额度和操作按钮
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # 使用额度标签(a+b=c$)格式
        self.current_usage_label = QLabel("使用额度: 计算中...")
        self.current_usage_label.setFont(QFont("", 11, QFont.Weight.Bold))
        self.current_usage_label.setStyleSheet("color: #00FF00;")  # 默认绿色

        # 刷新按钮 - 🔄 刷新当前登录账号信息
        self.refresh_account_button = QPushButton("🔄")
        self.refresh_account_button.setToolTip("刷新当前登录账号使用额度")
        self.refresh_account_button.setFixedSize(32, 32)
        self.refresh_account_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 152, 0, 0.2);
                color: #FF9800;
                border: none;
                font-size: 14px;
                border-radius: 16px;
                font-weight: bold;
            }
            QPushButton:hover:!disabled {
                background-color: rgba(255, 152, 0, 0.3);
                color: #FFB74D;
            }
            QPushButton:pressed:!disabled {
                background-color: rgba(255, 152, 0, 0.4);
                color: #F57C00;
            }
            QPushButton:disabled {
                background-color: rgba(128, 128, 128, 0.1);
                color: rgba(128, 128, 128, 0.4);
                border: 1px solid rgba(128, 128, 128, 0.2);
            }
        """
        )
        self.refresh_account_button.clicked.connect(self.update_usage_data)

        # Dashboard登录按钮 - 🌐 浏览器登录到Dashboard
        dashboard_button = QPushButton("🌐")
        dashboard_button.setToolTip("浏览器登录到Dashboard")
        dashboard_button.setFixedSize(32, 32)
        dashboard_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(76, 175, 80, 0.2);
                color: #4CAF50;
                border: none;
                font-size: 14px;
                border-radius: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.3);
                color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.4);
                color: #45a049;
            }
        """
        )
        dashboard_button.clicked.connect(self.login_to_dashboard)

        # 添加当前账号按钮 - ➕ 添加当前账号到账号管理列表
        add_current_button = QPushButton("➕")
        add_current_button.setToolTip("添加当前账号到账号管理列表")
        add_current_button.setFixedSize(32, 32)
        add_current_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(33, 150, 243, 0.2);
                color: #2196F3;
                border: none;
                font-size: 14px;
                border-radius: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.3);
                color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: rgba(33, 150, 243, 0.4);
                color: #1976D2;
            }
        """
        )
        add_current_button.clicked.connect(self.add_current_account_to_list)

        right_layout.addWidget(self.current_usage_label)
        right_layout.addWidget(self.refresh_account_button)
        right_layout.addWidget(dashboard_button)
        right_layout.addWidget(add_current_button)

        layout.addWidget(account_info_container, 1)  # 左侧占用更多空间
        layout.addWidget(right_container, 0)  # 右侧按钮紧凑

        return panel

    def create_account_table(self):
        """创建账号表格"""
        self.account_table = QTableWidget()

        headers = ["选择", "邮箱", "订阅类型", "备注", "状态", "操作", "详情"]
        self.account_table.setColumnCount(len(headers))
        self.account_table.setHorizontalHeaderLabels(headers)

        self.account_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.account_table.setAlternatingRowColors(True)
        self.account_table.verticalHeader().setVisible(False)

        # 设置行高
        self.account_table.verticalHeader().setDefaultSectionSize(45)

        # 设置列宽
        header = self.account_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 选择
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 邮箱
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 订阅类型
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # 备注
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # 状态
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # 操作
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # 详情

        self.account_table.setColumnWidth(0, 50)
        self.account_table.setColumnWidth(2, 100)
        self.account_table.setColumnWidth(3, 120)  # 备注列增加一倍宽度：60 -> 120
        self.account_table.setColumnWidth(4, 80)
        self.account_table.setColumnWidth(5, 100)
        self.account_table.setColumnWidth(6, 40)

        # 连接表格点击事件 - 订阅类型点击刷新功能
        self.account_table.cellClicked.connect(self.on_table_cell_clicked)

    def create_bottom_bar(self):
        """创建底部按钮栏"""
        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(80)
        bottom_bar.setStyleSheet("background-color: #2b2b2b; border-top: 1px solid #3c3c3c;")

        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(20, 15, 20, 15)

        # 三个主要按钮
        copy_btn = QPushButton("复制选中")
        copy_btn.setMinimumSize(120, 50)
        copy_btn.setStyleSheet(self.get_button_style("#28a745", "#218838"))
        copy_btn.clicked.connect(self.copy_selected)
        layout.addWidget(copy_btn)

        delete_btn = QPushButton("删除选中")
        delete_btn.setMinimumSize(120, 50)
        delete_btn.setStyleSheet(self.get_button_style("#dc3545", "#c82333"))
        delete_btn.clicked.connect(self.delete_selected)
        layout.addWidget(delete_btn)

        clear_btn = QPushButton("清除已应用")
        clear_btn.setMinimumSize(120, 50)
        clear_btn.setStyleSheet(self.get_button_style("#dc3545", "#c82333"))
        clear_btn.clicked.connect(self.clear_applied)
        layout.addWidget(clear_btn)

        layout.addStretch()

        return bottom_bar

    def load_accounts(self):
        """加载账号列表 - ，包含线程清理"""
        # 🔧 1. 清理旧的刷新线程 -
        for row, thread in list(self.refresh_threads.items()):
            if thread and thread.isRunning():
                thread.stop()
                if not thread.wait(1000):
                    print(f"⚠️ 强制终止刷新线程 row={row}")
                    thread.terminate()
                    thread.wait(500)
        self.refresh_threads.clear()

        # 🔧 2. 清空表格
        self.account_table.setRowCount(0)

        # 🔧 3. 重新加载配置 - 确保数据最新
        # config._load_config() 确保获取最新数据

        # 🔧 4. 加载账号数据
        accounts = self.config.get_accounts()
        if not accounts:
            self.status_bar.showMessage("没有找到已保存的账号")
            return

        print(f"📋 加载 {len(accounts)} 个账号")
        self.populate_table(accounts)
        self.update_statistics(accounts)

    def populate_table(self, accounts):
        """填充账号表格 - 保持原有的复杂布局"""
        self.account_table.setRowCount(len(accounts))

        for row, account in enumerate(accounts):
            # 🔧 适配新架构：account现在是dict而不是数据库行

            # 选择框
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            checkbox = QCheckBox()
            checkbox_layout.addWidget(checkbox)
            self.account_table.setCellWidget(row, 0, checkbox_widget)

            # 邮箱
            email = account.get("email", "N/A")
            email_item = QTableWidgetItem(email)
            email_item.setToolTip(email)
            self.account_table.setItem(row, 1, email_item)

            # 订阅类型
            subscription_type = account.get("subscription_type", "未知")
            subscription_item = QTableWidgetItem(subscription_type)

            # 🎨 设置订阅类型颜色
            subscription_color = self.get_subscription_color(subscription_type)
            subscription_item.setForeground(subscription_color)
            self.account_table.setItem(row, 2, subscription_item)

            # 备注
            note = account.get("note", "")
            note_item = QTableWidgetItem(note)
            note_item.setToolTip(note)
            self.account_table.setItem(row, 3, note_item)

            # 状态
            status = account.get("status", "待应用")
            status_item = QTableWidgetItem(status)

            # 🎨 设置状态颜色 - 支持完整状态
            if status == "已应用":
                status_item.setForeground(QColor(76, 175, 80))  # 绿色
            elif status == "应用中":
                status_item.setForeground(QColor(255, 165, 0))  # 橙色
            elif status == "待应用":
                status_item.setForeground(QColor(255, 193, 7))  # 黄色
            else:
                status_item.setForeground(QColor(255, 255, 255))  # 白色

            self.account_table.setItem(row, 4, status_item)

            # 🔧 动态操作按钮
            self._update_action_button_for_row(row, account)

            # 详情按钮
            detail_btn = QPushButton("详情")
            detail_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """
            )
            detail_btn.clicked.connect(lambda checked, r=row: self.auto_login_browser(r))
            self.account_table.setCellWidget(row, 6, detail_btn)

    # ================= 样式方法  =================

    def get_subscription_color(self, subscription_type):
        """获取订阅类型颜色"""
        color_map = {
            "未知": QColor(128, 128, 128),
            "仅auto": QColor(255, 255, 0),
            "废卡": QColor(255, 0, 0),
            "获取失败": QColor(139, 0, 0),
            "pro试用版": QColor(255, 0, 255),
            "pro专业版": QColor(40, 167, 69),
            "企业版": QColor(40, 167, 69),
            "团队版": QColor(40, 167, 69),
        }
        return color_map.get(subscription_type, QColor(255, 255, 255))

    def get_button_style(self, bg_color, hover_color):
        """获取按钮样式"""
        return f"""
        QPushButton {{
            background-color: {bg_color};
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        """

    def get_apply_button_style(self):
        """应用按钮样式"""
        return """
        QPushButton {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #218838;
        }
        """

    def get_professional_style(self):
        """专业样式"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        QTableWidget {
            background-color: #2b2b2b;
            gridline-color: #404040;
            selection-background-color: #0078d4;
            border: none;
        }

        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #404040;
        }

        QHeaderView::section {
            background-color: #1e1e1e;
            color: #ffffff;
            padding: 12px 8px;
            border: none;
            border-right: 1px solid #404040;
            border-bottom: 1px solid #404040;
            font-weight: bold;
        }

        QCheckBox {
            color: #ffffff;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 2px solid #404040;
            border-radius: 3px;
            background-color: #2b2b2b;
        }

        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        """

    # ================= 功能方法 - 适配新架构 =================

    def show_import_dialog(self):
        """显示导入对话框"""
        from .import_dialog import ImportDialog

        dialog = ImportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.account_data:
            # 添加账号到配置文件
            success = self.config.add_account(dialog.account_data)
            if success:
                QMessageBox.information(self, "导入成功", f"账号 {dialog.account_data.get('email', 'N/A')} 导入成功")
                self.load_accounts()  # 刷新列表
            else:
                QMessageBox.critical(self, "导入失败", "账号保存到配置文件失败")

    def apply_account_async(self, row):
        """异步应用账号 - 适配新架构"""
        accounts = self.config.get_accounts()
        if row >= len(accounts):
            return

        account = accounts[row]

        # 检查是否已经在处理中
        if row in self.apply_threads and self.apply_threads[row].isRunning():
            return

        # 检查Cursor进程
        if not self.check_and_handle_cursor_process():
            return

        display_name = account.get("email") or account.get("user_id", "")[:25]
        self.status_bar.showMessage(f"开始应用账号 {display_name}...")

        # 🔧 1. 先设置为"应用中"状态
        try:
            # 更新状态为"应用中"
            account["status"] = "应用中"
            account["updated_at"] = datetime.now().isoformat()
            accounts[row] = account
            self.config.config["accounts"] = accounts
            self.config._save_config(self.config.config)

            # 🎨 立即更新UI显示"应用中"状态
            status_item = self.account_table.item(row, 4)
            if status_item:
                status_item.setText("应用中")
                status_item.setForeground(QColor(255, 165, 0))  # 橙色

            # 🔧 更新操作按钮为"应用中"状态
            apply_btn = QPushButton("应用中")
            apply_btn.setEnabled(False)  # 禁用按钮
            apply_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #ffc107;
                    color: #000;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """
            )
            self.account_table.setCellWidget(row, 5, apply_btn)

            # 🔧 2. 重要：从token中提取真实邮箱地址 - 统一字段
            access_token = account.get("access_token") or account.get("cookie_token")  # 兼容性
            real_email = None
            if access_token:
                real_email = self._extract_email_from_token(access_token)
                if real_email:
                    account["email"] = real_email
                    accounts[row] = account
                    self.config.config["accounts"] = accounts
                    self.config._save_config(self.config.config)
                    print(f"📧 更新真实邮箱: {real_email}")

            display_email = account.get("email", "N/A")

            # 🔧 3. 后台执行应用操作
            # 生成账号专属机器ID
            storage_machine_ids, machine_id_file_value = self.cursor_manager.generate_account_machine_ids(
                display_email, force_new=False
            )

            # 应用配置
            success = self._apply_account_config(account, storage_machine_ids, machine_id_file_value)

            # 🔧 3. 根据结果更新最终状态
            if success:
                # 🔧 重要：先更新其他账号为"已应用"
                for i, acc in enumerate(accounts):
                    if acc.get("status") == "应用中" and i != row:
                        acc["status"] = "已应用"
                        print(f"📝 更新其他账号为已应用: {acc.get('email', 'N/A')}")

                        # 🎨 同时更新这些账号的UI状态
                        other_status_item = self.account_table.item(i, 4)
                        if other_status_item:
                            other_status_item.setText("已应用")
                            other_status_item.setForeground(QColor(76, 175, 80))  # 绿色

                # 当前账号设置为"应用中" (注意：不是"已应用"!)
                account["status"] = "应用中"  # 🔧 ：当前账号是"应用中"
                account["last_used_at"] = datetime.now().isoformat()
                accounts[row] = account
                self.config.config["accounts"] = accounts
                self.config._save_config(self.config.config)

                # 🎨 更新UI为"应用中"状态 (逻辑)
                if status_item:
                    status_item.setText("应用中")
                    status_item.setForeground(QColor(255, 165, 0))  # 橙色 - 表示当前活跃

                # 🔧 使用统一的按钮更新方法
                self._update_action_button_for_row(row, account)

                self.status_bar.showMessage(f"✅ 账号 {display_name} 应用成功")

                # 🔧 联动更新：通知主窗口刷新当前账号显示
                QTimer.singleShot(500, self.update_usage_data)

            else:
                # 应用失败 - 恢复为"待应用"
                account["status"] = "待应用"
                accounts[row] = account
                self.config.config["accounts"] = accounts
                self.config._save_config(self.config.config)

                # 🎨 恢复UI状态
                if status_item:
                    status_item.setText("待应用")
                    status_item.setForeground(QColor(255, 193, 7))  # 黄色

                # 恢复应用按钮
                self._update_action_button_for_row(row, account)

                self.status_bar.showMessage(f"❌ 账号 {display_name} 应用失败")

        except Exception as e:
            # 异常情况 - 恢复为"待应用"
            account["status"] = "待应用"
            accounts[row] = account
            self.config.config["accounts"] = accounts
            self.config._save_config(self.config.config)

            # 恢复UI状态
            status_item = self.account_table.item(row, 4)
            if status_item:
                status_item.setText("待应用")
                status_item.setForeground(QColor(255, 193, 7))

            self._update_action_button_for_row(row, account)
            self.status_bar.showMessage(f"❌ 应用账号时出错: {str(e)}")

    def check_and_handle_cursor_process(self):
        """检查并处理Cursor进程"""
        cursor_manager = CursorProcessManager()
        cursor_running = cursor_manager.is_cursor_running()

        if not cursor_running:
            return True  # Cursor未运行，继续

        # Cursor正在运行，弹出对话框
        reply = QMessageBox.question(
            self,
            "需要关闭Cursor",
            "检测到Cursor正在运行。应用账号前需要关闭Cursor。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 用户选择关闭Cursor
            self.status_bar.showMessage("正在关闭Cursor进程...")
            success, message = cursor_manager.close_cursor()

            if success:
                self.status_bar.showMessage(f"✅ {message}")
            else:
                self.status_bar.showMessage(f"⚠️ {message}，但将继续尝试应用账号")

            return True  # 无论关闭是否成功都继续
        else:
            # 用户选择No，取消操作
            self.status_bar.showMessage("用户取消操作")
            return False

    def _apply_account_config(self, account, storage_machine_ids, machine_id_file_value):
        """应用账号配置 - 集成新的模块化架构"""
        try:
            print("\n=== 🚀 开始应用账号配置 (新架构) ===")

            # 获取路径
            paths = CursorManager.get_cursor_paths()
            storage_file = paths["storage_json"]
            machine_id_file = paths["machine_id"]

            print(f"📁 配置文件路径: {storage_file}")
            print(f"📁 机器ID文件路径: {machine_id_file}")

            # 确保目录存在
            os.makedirs(os.path.dirname(storage_file), exist_ok=True)

            # 读取现有配置
            config = {}
            if os.path.exists(storage_file):
                print("📖 读取现有配置文件...")
                with open(storage_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                print(f"📊 现有配置键数量: {len(config)}")
            else:
                print("📄 配置文件不存在，将创建新的")

            # 🔧 显示账号专属机器ID
            print("🔑 账号专属机器ID配置:")
            for key, value in storage_machine_ids.items():
                print(f"   {key}: {value[:16]}...")
            print(f"   machineId文件值: {machine_id_file_value[:16]}...")

            # 更新认证配置 -
            new_config = {
                # 核心认证配置
                "workos.sessionToken": account.get("cookie_token", ""),
                "cursor.auth.token": account.get("cookie_token", ""),
                "cursor.auth.userId": account.get("user_id", ""),
                "cursor.auth.email": account.get("email", ""),
                "cursor.auth.lastLogin": datetime.now().isoformat(),
                "cursor.auth.subscriptionType": account.get("subscription_type", "仅auto"),
                # 🆕 账号专属机器ID配置 - 真正的一号一码
                "telemetry.devDeviceId": storage_machine_ids["telemetry.devDeviceId"],
                "telemetry.macMachineId": storage_machine_ids["telemetry.macMachineId"],
                "telemetry.machineId": storage_machine_ids["telemetry.machineId"],
                "telemetry.sqmId": storage_machine_ids["telemetry.sqmId"],
                # 账号切换和状态标记
                "cursor.lastAccountSwitch": datetime.now().isoformat(),
                "cursor.currentAccount": account.get("email", account.get("user_id", "")),
                "cursor.accountSwitcher.usedAccountSpecificMachineId": True,
                "cursor.appliedByFreeVersion": True,
                "cursor.appliedAt": datetime.now().isoformat(),
                # 清除可能的冲突配置
                "telemetry.currentSessionDate": None,
                "notifications.perSourceDoNotDisturbMode": None,
                "editorFontInfo": None,
                "extensionsAssistant/recommendations": None,
            }

            config.update(new_config)
            print(f"⚙️ 更新配置，新增 {len(new_config)} 个配置项")

            # 写入配置文件
            print(f"💾 写入配置到: {storage_file}")
            with open(storage_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("✅ storage.json 写入成功")

            # 验证关键配置
            print("🔍 验证写入的认证配置:")
            print(
                f"   workos.sessionToken: "
                f"{new_config['workos.sessionToken'][:50] if new_config['workos.sessionToken'] else 'N/A'}..."
            )
            print(f"   cursor.auth.userId: {new_config['cursor.auth.userId']}")
            print(f"   cursor.auth.email: {new_config['cursor.auth.email']}")
            print(f"   订阅类型: {new_config['cursor.auth.subscriptionType']}")
            print(f"   专属机器ID: {new_config['telemetry.machineId'][:16]}...")

            # 写入machineId文件
            print(f"💾 写入机器ID文件: {machine_id_file}")
            try:
                os.makedirs(os.path.dirname(machine_id_file), exist_ok=True)
                with open(machine_id_file, "w", encoding="utf-8") as f:
                    f.write(machine_id_file_value)
                print("✅ machineId 文件写入成功")
            except Exception as e:
                print(f"❌ 写入machineId文件失败: {e}")

            print("=== ✅ 账号配置应用完成 ===")

            # 🔧 重要：更新Cursor数据库认证信息 ()
            print("=== 🔧 开始更新Cursor认证数据库 ===")
            auth_success, auth_msg = self.cursor_manager.update_auth(
                email=account.get("email", ""),
                access_token=account.get("access_token") or account.get("cookie_token"),
                refresh_token=account.get("refresh_token", account.get("access_token") or account.get("cookie_token")),
                user_id=account.get("user_id", ""),
            )

            if not auth_success:
                print(f"❌ 认证数据库更新失败: {auth_msg}")
                return False

            # 🔧 应用补丁系统
            print("=== 🔧 开始应用补丁系统 ===")
            patch_success = self._apply_patches()

            if patch_success:
                print("✅ 补丁应用成功")
                print("🎉 账号应用完全成功！")
            else:
                print("⚠️ 补丁应用失败，但配置文件已写入")

            return True

        except Exception as e:
            print(f"❌ 应用账号配置失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _apply_patches(self):
        """应用补丁系统"""
        try:
            # 🔧 ：使用skip_permission_check=True
            patcher = self.cursor_manager.patcher
            success, message = patcher.apply_patch(skip_permission_check=True)

            print(f"🔧 补丁应用结果: {message}")
            return success

        except Exception as e:
            print(f"❌ 补丁应用出错: {e}")
            return False

    # ================= 临时占位方法 - 后续完善 =================

    def on_table_cell_clicked(self, row, column):
        """处理表格单元格点击事件 -"""
        if column == 2:  # 订阅类型栏 - 启动真实刷新功能
            self.refresh_subscription_info(row)
        elif column == 0:  # 选择框栏
            checkbox_widget = self.account_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())

    def refresh_subscription_info(self, row):
        """刷新指定行的订阅信息 - 真实实现"""
        # 检查是否已在刷新
        if row in self.refresh_threads and self.refresh_threads[row].isRunning():
            self.status_bar.showMessage("该账号正在刷新中，请稍候...")
            return

        # 检查行号有效性
        if row < 0 or row >= self.account_table.rowCount():
            self.status_bar.showMessage(f"无效的行号: {row}")
            return

        # 获取账号信息
        accounts = self.config.get_accounts()
        if row >= len(accounts):
            self.status_bar.showMessage("账号索引超出范围")
            return

        account = accounts[row]
        email = account.get("email", "")

        if not email:
            self.status_bar.showMessage("账号邮箱为空")
            return

        if not account.get("cookie_token"):
            self.status_bar.showMessage(f"账号 {email} 缺少认证Token")
            return

        # 🔧 启动单账号刷新线程
        print(f"🔄 开始刷新账号: {email}")
        self.status_bar.showMessage(f"正在刷新账号 {email} 的订阅状态...")

        # 创建并启动刷新线程
        refresh_thread = SingleRefreshThread(self.config, row, email, account)
        refresh_thread.refresh_finished.connect(self.handle_single_refresh_finished)
        refresh_thread.start()

        # 保存线程引用
        self.refresh_threads[row] = refresh_thread

        # 更新UI显示刷新状态
        subscription_item = self.account_table.item(row, 2)
        if subscription_item:
            subscription_item.setText("刷新中...")
            subscription_item.setForeground(QColor(255, 165, 0))  # 橙色显示刷新中

    def handle_single_refresh_finished(self, row, success, message, updated_account):
        """处理单个账号刷新完成 -"""
        print(f"🔍 刷新完成: row={row}, success={success}, message={message}")

        # 清理线程引用
        if row in self.refresh_threads:
            thread = self.refresh_threads[row]
            if thread.isRunning():
                thread.stop()
                thread.wait(1000)
            del self.refresh_threads[row]

        # 检查行号有效性
        if row < 0 or row >= self.account_table.rowCount():
            print(f"⚠️ 刷新完成时行号{row}超出有效范围")
            return

        # 获取表格中的订阅类型项
        subscription_item = self.account_table.item(row, 2)
        if not subscription_item:
            print(f"⚠️ 刷新完成时无法获取行{row}的订阅类型项")
            return

        if success and updated_account:
            # 🔧 更新配置文件中的账号数据
            accounts = self.config.get_accounts()
            if row < len(accounts):
                # 更新账号数据
                accounts[row]["subscription_type"] = updated_account["subscription_type"]
                accounts[row]["membershipType"] = updated_account.get("membershipType", "")
                accounts[row]["subscriptionData"] = updated_account.get("subscriptionData", {})
                accounts[row]["updated_at"] = datetime.now().isoformat()

                # 保存到配置文件
                self.config.config["accounts"] = accounts
                self.config._save_config(self.config.config)

                # 🎨 更新UI显示
                new_subscription_type = updated_account["subscription_type"]
                subscription_item.setText(new_subscription_type)

                # 设置颜色
                subscription_color = self.get_subscription_color(new_subscription_type)
                subscription_item.setForeground(subscription_color)

                # 🔧 重新创建操作按钮（如果是废卡，按钮应该变为删除）
                self._update_action_button_for_row(row, updated_account)

                self.status_bar.showMessage(f"✅ {message}")
                print(f"✅ 账号 {updated_account.get('email', '')} 订阅状态已更新: {new_subscription_type}")
            else:
                self.status_bar.showMessage("❌ 账号索引错误，更新失败")
        else:
            # 刷新失败，恢复原状态
            accounts = self.config.get_accounts()
            if row < len(accounts):
                original_subscription = accounts[row].get("subscription_type", "未知")
                subscription_item.setText(original_subscription)
                subscription_color = self.get_subscription_color(original_subscription)
                subscription_item.setForeground(subscription_color)

            self.status_bar.showMessage(f"❌ {message}")
            print(f"❌ 账号刷新失败: {message}")

    def _update_action_button_for_row(self, row, account):
        """更新指定行的操作按钮"""
        status = account.get("status", "待应用")
        subscription_type = account.get("subscription_type", "未知")

        # 🔧 动态按钮逻辑 -
        if subscription_type == "废卡":
            # 废卡显示删除按钮
            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #e04b59;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """
            )
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_single_account(r))
            self.account_table.setCellWidget(row, 5, delete_btn)
        elif status == "应用中":
            # 🔧 当前活跃账号显示"再应用"按钮
            reapply_btn = QPushButton("再应用")
            reapply_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #ff9800;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #e68900;
                }
            """
            )
            reapply_btn.clicked.connect(lambda checked, r=row: self.apply_account_async(r))
            self.account_table.setCellWidget(row, 5, reapply_btn)
        elif status == "已应用":
            # 🔧 之前应用过的账号显示"切换"按钮
            switch_btn = QPushButton("切换")
            switch_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """
            )
            switch_btn.clicked.connect(lambda checked, r=row: self.apply_account_async(r))
            self.account_table.setCellWidget(row, 5, switch_btn)
        else:
            # 待应用状态显示"应用账号"按钮
            apply_btn = QPushButton("应用账号")
            apply_btn.setStyleSheet(self.get_apply_button_style())
            apply_btn.clicked.connect(lambda checked, r=row: self.apply_account_async(r))
            self.account_table.setCellWidget(row, 5, apply_btn)

    def delete_single_account(self, row):
        """删除单个账号 -"""
        accounts = self.config.get_accounts()
        if row >= len(accounts):
            return

        account = accounts[row]
        email = account.get("email", "未知账号")

        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除账号 {email} 吗？\n\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 删除账号
            remaining_accounts = [acc for i, acc in enumerate(accounts) if i != row]

            # 保存更新后的账号列表
            self.config.config["accounts"] = remaining_accounts
            self.config._save_config(self.config.config)

            # 智能更新UI - 删除该行而不是重新加载
            self.account_table.removeRow(row)

            # 更新统计
            self.update_statistics(remaining_accounts)

            self.status_bar.showMessage(f"✅ 已删除账号: {email}")

    def select_all_pro(self, state):
        """选择所有Pro账号 - 适配JSON存储"""
        checked = state == Qt.CheckState.Checked.value
        accounts = self.config.get_accounts()

        for row in range(self.account_table.rowCount()):
            if row < len(accounts):
                account = accounts[row]
                if "pro" in account.get("subscription_type", "").lower():
                    checkbox_widget = self.account_table.cellWidget(row, 0)
                    if checkbox_widget:
                        checkbox = checkbox_widget.findChild(QCheckBox)
                        if checkbox:
                            checkbox.setChecked(checked)

    def copy_selected(self):
        """复制选中账号 - 适配JSON存储"""
        selected = self.get_selected_accounts()
        if not selected:
            self.status_bar.showMessage("❌ 请先选择账号")
            return

        copy_lines = []
        for account in selected:
            display_name = account.get("email") or account.get("user_id", "")[:25]
            copy_lines.append(f"# {display_name}")
            copy_lines.append(f"WorkosCursorSessionToken={account.get('cookie_token', '')}")
            copy_lines.append("")

        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(copy_lines))

        self.status_bar.showMessage(f"✅ 已复制 {len(selected)} 个账号")

    def delete_selected(self):
        """删除选中账号 - 智能批量删除，避免重新加载"""
        selected_rows_and_accounts = self.get_selected_rows_and_accounts()
        if not selected_rows_and_accounts:
            self.status_bar.showMessage("❌ 请先选择账号")
            return

        selected_accounts = [item["account"] for item in selected_rows_and_accounts]

        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {len(selected_accounts)} 个账号吗？\n\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 🔧 智能删除 - 从后往前删除行，避免索引错乱
            rows_to_delete = sorted([item["row"] for item in selected_rows_and_accounts], reverse=True)
            user_ids_to_delete = [acc.get("user_id") for acc in selected_accounts]

            # 停止这些账号的相关线程
            for row in rows_to_delete:
                if row in self.refresh_threads:
                    thread = self.refresh_threads[row]
                    if thread.isRunning():
                        thread.stop()
                        thread.wait(1000)
                    del self.refresh_threads[row]

            # 从配置中删除
            all_accounts = self.config.get_accounts()
            remaining_accounts = [acc for acc in all_accounts if acc.get("user_id") not in user_ids_to_delete]

            # 保存更新后的账号列表
            self.config.config["accounts"] = remaining_accounts
            self.config._save_config(self.config.config)

            # 🔧 智能UI更新：逐行删除而不是重新加载
            for row in rows_to_delete:
                self.account_table.removeRow(row)

            # 更新统计
            self.update_statistics(remaining_accounts)

            self.status_bar.showMessage(f"✅ 已删除 {len(selected_accounts)} 个账号")
            print(f"✅ 智能删除完成: {len(selected_accounts)} 个账号")

    def clear_applied(self):
        """清除已应用账号 - 智能批量清除，避免重新加载"""
        all_accounts = self.config.get_accounts()

        # 🔧 找到已应用账号的行号
        applied_rows_and_accounts = []
        for row in range(self.account_table.rowCount()):
            if row < len(all_accounts):
                account = all_accounts[row]
                if account.get("status") == "已应用":
                    applied_rows_and_accounts.append({"row": row, "account": account})

        if not applied_rows_and_accounts:
            self.status_bar.showMessage("❌ 没有已应用的账号")
            return

        # 确认清除
        reply = QMessageBox.question(
            self,
            "确认清除",
            f"确定要清除 {len(applied_rows_and_accounts)} 个已应用的账号吗？\n\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 🔧 智能清除 - 从后往前删除行
            rows_to_delete = sorted([item["row"] for item in applied_rows_and_accounts], reverse=True)
            user_ids_to_delete = [item["account"].get("user_id") for item in applied_rows_and_accounts]

            # 停止相关线程
            for row in rows_to_delete:
                if row in self.refresh_threads:
                    thread = self.refresh_threads[row]
                    if thread.isRunning():
                        thread.stop()
                        thread.wait(1000)
                    del self.refresh_threads[row]

            # 从配置中删除
            remaining_accounts = [acc for acc in all_accounts if acc.get("user_id") not in user_ids_to_delete]

            # 保存更新后的账号列表
            self.config.config["accounts"] = remaining_accounts
            self.config._save_config(self.config.config)

            # 🔧 智能UI更新：逐行删除而不是重新加载
            for row in rows_to_delete:
                self.account_table.removeRow(row)

            # 更新统计
            self.update_statistics(remaining_accounts)

            self.status_bar.showMessage(f"✅ 已清除 {len(applied_rows_and_accounts)} 个已应用账号")
            print(f"✅ 智能清除完成: {len(applied_rows_and_accounts)} 个账号")

    def get_selected_accounts(self):
        """获取选中的账号列表"""
        selected_accounts = []
        accounts = self.config.get_accounts()

        for row in range(self.account_table.rowCount()):
            if row < len(accounts):
                checkbox_widget = self.account_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        selected_accounts.append(accounts[row])

        return selected_accounts

    def get_selected_rows_and_accounts(self):
        """获取选中的行号和账号信息 - 用于智能批量操作"""
        selected_items = []
        accounts = self.config.get_accounts()

        for row in range(self.account_table.rowCount()):
            if row < len(accounts):
                checkbox_widget = self.account_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        selected_items.append({"row": row, "account": accounts[row]})

        return selected_items

    def auto_login_browser(self, row):
        """账号列表Dashboard登录 - 完全静默实现"""
        accounts = self.config.get_accounts()
        if row >= len(accounts):
            return

        account = accounts[row]
        display_name = account.get("email") or account.get("user_id", "")[:25]
        user_id = account.get("user_id")
        # 🔧 ：统一使用access_token字段
        access_token = account.get("access_token") or account.get("cookie_token")  # 兼容性

        if not user_id or not access_token:
            self.status_bar.showMessage(f"❌ 账号 {display_name} 信息不完整")
            return

        try:
            self.status_bar.showMessage(f"🌐 正在为 {display_name} 启动浏览器...")

            # 🔧 ：login_to_dashboard_with_account的实现
            browser_manager = BrowserManager(self.config, incognito_mode=True)
            page = browser_manager.get_new_page()
            if not page:
                self.status_bar.showMessage("❌ 启动浏览器失败")
                return

            # 🔧 设置认证Cookie
            success = browser_manager.set_auth_cookie(page, user_id, access_token)
            if not success:
                self.status_bar.showMessage("❌ 设置认证Cookie失败")
                return

            # 🔧 ：page.get(CURSOR_URLS['DASHBOARD'])
            from ..constants import CURSOR_URLS

            page.get(CURSOR_URLS.get("DASHBOARD", "https://cursor.com/dashboard"))

            # 🔧 ：browser = None（清理引用）
            browser_manager.browser = None

            self.status_bar.showMessage(f"✅ 浏览器已打开，账号 {display_name} 登录成功")

        except Exception as e:
            self.status_bar.showMessage(f"❌ 浏览器登录失败: {str(e)}")

    def login_to_dashboard(self):
        """浏览器登录到Dashboard - 完全静默实现"""
        try:
            # 🔧 1. 获取当前账号完整信息
            account_info = self.get_current_cursor_account_info()

            if not account_info:
                self.status_bar.showMessage("❌ 当前账号信息不完整")
                return

            email = account_info.get("email")
            user_id = account_info.get("user_id")
            access_token = account_info.get("token")

            if not access_token or not email or not user_id:
                self.status_bar.showMessage("❌ 账号信息不完整")
                return

            self.status_bar.showMessage(f"🌐 正在为账号 {email} 启动浏览器...")

            # 🔧 2. 静默执行，无弹窗
            browser_manager = BrowserManager(self.config, incognito_mode=True)
            success = browser_manager.open_dashboard(user_id, access_token)

            if success:
                # ✅ 成功 - 静默成功，只更新状态栏
                self.status_bar.showMessage(f"✅ 浏览器已打开，账号 {email} 登录成功")
            else:
                # ❌ 失败 - 静默失败，只更新状态栏
                self.status_bar.showMessage("❌ 启动浏览器失败")

        except Exception as e:
            # ❌ 异常 - 静默处理
            self.status_bar.showMessage(f"❌ 浏览器登录失败: {str(e)}")

    def add_current_account_to_list(self):
        """添加当前账号到账号管理列表"""
        try:
            # 🔧
            account_details = self.cursor_manager.get_cursor_account_details()

            if not account_details:
                QMessageBox.warning(self, "添加失败", "未检测到当前登录的Cursor账号")
                return

            access_token = account_details.get("token")
            user_id = account_details.get("user_id")
            email = account_details.get("email")

            if not access_token or not email or not user_id:
                QMessageBox.warning(self, "添加失败", "当前账号信息不完整，无法添加")
                return

            # 🔧 根据email检查
            existing_account = self.config.get_account(email)
            if existing_account:
                QMessageBox.information(self, "账号已存在", f"账号 {email} 已存在于账号列表中")
                return

            # 🔧 直接使用从数据库获取的access_token，不再从storage.json获取

            # 🔧 获取真实订阅类型（复用topbar的逻辑）
            subscription = "仅auto"  # 默认值

            # 尝试通过API获取真实订阅类型
            try:
                import requests

                session_token = f"{user_id}%3A%3A{access_token}"

                headers = {
                    "accept": "*/*",
                    "content-type": "application/json",
                    "origin": "https://cursor.com",
                    "referer": "https://cursor.com/dashboard",
                }

                cookies = {"WorkosCursorSessionToken": session_token, "NEXT_LOCALE": "zh"}

                response = requests.get(
                    "https://cursor.com/api/auth/stripe", headers=headers, cookies=cookies, timeout=10
                )

                if response.status_code == 200:
                    subscription_data = response.json()
                    membership_type = subscription_data.get("membershipType", "free")

                    # 转换为显示名称
                    if membership_type == "pro":
                        subscription = "pro专业版"
                    elif membership_type == "free":
                        trial_eligible = subscription_data.get("trialEligible", False)
                        if trial_eligible:
                            subscription = "pro试用版"
                        else:
                            subscription = "free免费版"
                    else:
                        subscription = membership_type

                    print(f"✅ 获取当前账号真实订阅: {subscription}")
                else:
                    print(f"⚠️ 订阅API调用失败({response.status_code})，使用默认值")
            except Exception as e:
                print(f"⚠️ 获取订阅信息异常: {e}，使用默认值")

            # 添加到配置文件
            account_data = {
                "email": email,
                "user_id": user_id,
                "access_token": access_token,  # 🔧 使用正确字段名
                "cookie_token": access_token,  # 兼容性字段
                "subscription_type": subscription,
                "note": "从当前登录账号添加",
                "status": "待应用",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            success = self.config.add_account(account_data)
            if success:
                self.load_accounts()  # 刷新账号列表
                self.status_bar.showMessage(f"✅ 成功添加账号: {email}")
                QMessageBox.information(
                    self,
                    "添加成功",
                    f"已成功添加当前账号到管理列表！\n\n邮箱: {email}\n用户ID: {user_id}\n订阅类型: {subscription}",
                )
            else:
                QMessageBox.critical(self, "添加失败", "添加账号到配置文件时出错")

        except Exception as e:
            QMessageBox.critical(self, "添加失败", f"添加当前账号时出错: {str(e)}")
            self.status_bar.showMessage("❌ 添加当前账号失败")

    def get_current_cursor_account_info(self):
        """获取当前Cursor账号信息 - 与topbar显示保持一致，优先state.vscdb"""
        # 🔧 修复数据源一致性：与topbar显示保持一致，优先使用state.vscdb
        state_info = self._get_account_from_state_db()
        if state_info:
            print(f"✅ 从state.vscdb获取到账号信息: {state_info.get('email', 'N/A')}")
            return state_info

        # 回退：从storage.json获取信息
        print("⚠️ state.vscdb无账号信息，尝试从storage.json获取...")
        storage_info = self._get_account_from_storage_json()
        if storage_info:
            print(f"✅ 从storage.json获取到账号信息: {storage_info.get('email', 'N/A')}")
            return storage_info

        return None

    def _get_account_from_storage_json(self):
        """从storage.json获取账号信息 - 直接复制cursor_account_tool的工作实现"""
        try:
            paths = CursorManager.get_cursor_paths()
            storage_file = paths["storage_json"]

            if not os.path.exists(storage_file):
                print(f"⚠️ storage.json不存在: {storage_file}")
                return None

            with open(storage_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 检查关键认证字段
            session_token = config.get("workos.sessionToken")
            auth_email = config.get("cursor.auth.email")
            auth_user_id = config.get("cursor.auth.userId")
            subscription_type = config.get("cursor.auth.subscriptionType", "pro")

            if not session_token or not auth_email or not auth_user_id:
                print("⚠️ storage.json中缺少关键认证信息")
                return None

            # 检查token是否有效
            try:
                from ..utils.jwt_utils import JWTUtils

                payload = JWTUtils.decode_jwt_payload(session_token)
                if payload:
                    exp_time = payload.get("exp", 0)
                    if exp_time:
                        import time

                        if exp_time <= time.time():
                            print("⚠️ storage.json中的token已过期")
                            return None
            except Exception as e:
                print(f"⚠️ 检查storage.json token时出错: {e}")

            print(f"✅ 从storage.json成功读取账号: {auth_email}")

            return {
                "email": auth_email,
                "user_id": auth_user_id,
                "token": session_token,
                "subscription": subscription_type,
                "usage_info": f"📁 来源: storage.json\n💳 {subscription_type}账号",
                "source": "storage.json",
            }

        except Exception as e:
            print(f"⚠️ 从storage.json读取账号信息失败: {e}")
            return None

    def _get_account_from_state_db(self):
        """从state.vscdb获取账号信息 - 原有逻辑"""
        try:
            import sqlite3

            # 构建数据库路径
            if sys.platform == "win32":
                db_path = os.path.join(os.getenv("APPDATA"), "Cursor", "User", "globalStorage", "state.vscdb")
            elif sys.platform == "darwin":
                db_path = os.path.abspath(
                    os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")
                )
            else:  # Linux
                db_path = os.path.expanduser("~/.config/Cursor/User/globalStorage/state.vscdb")

            if not os.path.exists(db_path):
                print(f"⚠️ Cursor数据库不存在: {db_path}")
                return None

            # 连接SQLite数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 🔧 修复：根据实际数据库字段查询
            cursor.execute(
                """
                SELECT key, value
                FROM ItemTable
                WHERE key IN (
                    'cursorAuth/accessToken',
                    'cursorAuth/refreshToken',
                    'cursorAuth/cachedEmail',
                    'cursorAuth/userId',
                    'cursorAuth/email'
                )
            """
            )
            results = cursor.fetchall()
            conn.close()

            if not results:
                print("⚠️ 未找到Cursor认证信息")
                return None

            auth_data = {}
            for key, value in results:
                if key == "cursorAuth/accessToken":
                    auth_data["token"] = value.strip('"') if value else None
                elif key == "cursorAuth/refreshToken":
                    auth_data["refresh_token"] = value.strip('"') if value else None
                elif key in ["cursorAuth/cachedEmail", "cursorAuth/email"]:
                    auth_data["email"] = value.strip('"') if value else None
                elif key == "cursorAuth/userId":
                    auth_data["user_id"] = value.strip('"') if value else None

            print(f"🔍 从数据库获取的认证数据: {list(auth_data.keys())}")
            if auth_data.get("email"):
                print(f"✅ 从数据库获取到邮箱: {auth_data['email']}")
            if auth_data.get("user_id"):
                print(f"✅ 从数据库获取到用户ID: {auth_data['user_id']}")

            if not auth_data.get("token") or not auth_data.get("email"):
                print("⚠️ 认证信息不完整")
                return None

            print(f"✅ 从state.vscdb获取到账号信息: {auth_data['email']}")

            # 🔧 从accessToken中提取user_id和真实邮箱（优先于数据库中的邮箱）
            if auth_data.get("token"):
                try:
                    from ..utils.jwt_utils import JWTUtils

                    payload = JWTUtils.decode_jwt_payload(auth_data["token"])
                    if payload:
                        sub = payload.get("sub", "")
                        if "|" in sub:
                            if not auth_data.get("user_id"):
                                auth_data["user_id"] = sub.split("|")[1]
                                print(f"✅ 从token中提取user_id: {auth_data['user_id']}")

                        # 🔧 优先使用JWT中的真实邮箱
                        token_email = self._extract_email_from_token(auth_data["token"])
                        if token_email and "@" in token_email and not token_email.endswith("@cursor.local"):
                            print(f"✅ 从token中提取真实邮箱: {token_email}")
                            print(f"   替换数据库邮箱: {auth_data.get('email', 'N/A')}")
                            auth_data["email"] = token_email
                except Exception:
                    pass

            return {
                "email": auth_data["email"],
                "user_id": auth_data.get("user_id", "unknown"),
                "access_token": auth_data["token"],  # 🔧 使用正确字段名
                "token": auth_data["token"],  # 兼容性
                "subscription": "pro",
                "usage_info": "📁 来源: state.vscdb\n💳 pro账号",
                "source": "state.vscdb",
            }

        except Exception as e:
            print(f"⚠️ 从state.vscdb获取账号信息失败: {e}")
            return None

    def _extract_email_from_token(self, token):
        """从JWT token中提取真实邮箱 - 直接复制cursor_account_tool的实现"""
        try:
            from ..utils.jwt_utils import JWTUtils

            payload = JWTUtils.decode_jwt_payload(token)
            if not payload:
                return None

            # 尝试多种可能的邮箱字段 - cursor_account_tool的完整逻辑
            email_fields = ["email", "user_email", "preferred_username", "name"]

            for field in email_fields:
                email = payload.get(field)
                if email and "@" in str(email):
                    print(f"✅ 从token {field}字段提取真实邮箱: {email}")
                    return email

            # 如果没有直接的邮箱字段，尝试从sub字段分析
            sub = payload.get("sub")
            if sub and "@" in str(sub):
                print(f"✅ 从sub字段提取邮箱: {sub}")
                return sub

            return None

        except Exception as e:
            print(f"⚠️ 从token提取邮箱失败: {e}")
            return None

    def update_statistics(self, accounts):
        """更新统计信息 - 支持完整状态统计"""
        applied = len([a for a in accounts if a.get("status") == "已应用"])
        pending = len([a for a in accounts if a.get("status") == "待应用"])
        applying = len([a for a in accounts if a.get("status") == "应用中"])

        if applying > 0:
            self.stats_label.setText(f"已应用: {applied} | 应用中: {applying} | 待应用: {pending}")
        else:
            self.stats_label.setText(f"已应用: {applied} | 待应用: {pending}")

    def check_cursor_installation_paths(self):
        """检查Cursor安装路径（严格模式）"""
        is_valid, cursor_path = CursorManager.validate_cursor_installation()

        if is_valid:
            self.status_bar.showMessage(f"✅ 检测到Cursor安装: {cursor_path}")
            print(f"✅ Cursor路径验证通过: {cursor_path}")
        else:
            self.status_bar.showMessage("❌ 未检测到Cursor安装 - 需要设置路径")
            print("❌ Cursor路径验证失败，需要用户设置")
            # 强制要求用户设置路径，否则退出程序
            self.force_cursor_path_setup()

    def force_cursor_path_setup(self):
        """强制用户设置Cursor路径（严格模式）"""

        from PyQt6.QtWidgets import QMessageBox

        # 强制要求用户设置路径
        reply = QMessageBox.critical(
            self,
            "Cursor路径必须设置",
            "⚠️ 未能检测到Cursor安装路径！\n\n"
            "本程序需要正确的Cursor安装路径才能正常工作。\n"
            "包括版本检测、补丁功能等都依赖于此。\n\n"
            "是否现在设置Cursor安装路径？\n\n"
            '点击"否"将退出程序。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 强制要求用户选择有效路径
            if not self.force_select_valid_cursor_path():
                # 用户最终放弃设置，退出程序
                self.exit_application("用户取消路径设置")
        else:
            # 用户选择不设置，直接退出程序
            self.exit_application("用户拒绝设置Cursor路径")

    def validate_and_save_cursor_path(self, path):
        """验证并保存用户选择的Cursor路径"""
        import platform

        system = platform.system().lower()

        if system == "windows":
            key_files = ["Cursor.exe", "resources/app/out/main.js"]
        elif system == "darwin":
            key_files = ["Contents/MacOS/Cursor", "Contents/Resources/app/out/main.js"]
        else:  # Linux
            key_files = ["cursor", "resources/app/out/main.js"]

        # 验证路径
        if CursorManager._validate_cursor_path(path, key_files):
            # 保存到配置
            self.config.set("cursor", "app_path", path)
            return True

        return False

    def force_select_valid_cursor_path(self):
        """强制选择有效的Cursor路径（循环直到成功或用户取消）"""
        import os

        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        while True:
            print("🔄 开始路径选择")

            # 打开文件夹选择对话框
            cursor_path = QFileDialog.getExistingDirectory(
                self, "选择Cursor安装目录", os.path.expanduser("~"), QFileDialog.Option.ShowDirsOnly
            )

            if not cursor_path:
                # 用户取消了选择，直接退出程序
                print("🚫 用户取消了路径选择，程序将退出")
                return False

            # 验证选择的路径
            if self.validate_and_save_cursor_path(cursor_path):
                # 路径有效，设置成功
                QMessageBox.information(
                    self,
                    "设置成功",
                    f"✅ 已成功设置Cursor安装路径：\n{cursor_path}\n\n" "程序将使用此路径进行版本检测和补丁功能。",
                )
                print(f"✅ Cursor路径设置成功: {cursor_path}")
                return True
            else:
                # 路径无效，询问是否重新选择
                reply = QMessageBox.warning(
                    self,
                    "路径无效",
                    "❌ 选择的路径不是有效的Cursor安装目录！\n\n"
                    "请确保目录中包含以下文件：\n"
                    "• Windows: Cursor.exe\n"
                    "• macOS: Contents/MacOS/Cursor\n"
                    "• Linux: cursor 可执行文件\n\n"
                    "支持的Linux安装方式:\n"
                    "- AppImage便携版\n"
                    "- 系统包管理器安装\n"
                    "- Snap/Flatpak包\n"
                    "- 源码编译安装\n\n"
                    "是否重新选择路径？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes,
                )

                if reply == QMessageBox.StandardButton.No:
                    print("🚫 用户放弃重新选择，程序将退出")
                    return False  # 用户放弃
                # 如果用户选择"是"，继续循环

    def exit_application(self, reason):
        """退出应用程序"""
        print(f"🚫 程序退出: {reason}")
        self.status_bar.showMessage(f"程序退出: {reason}")

        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self, "程序退出", f"程序即将退出。\n\n原因: {reason}\n\n" "请重新启动程序并正确设置Cursor路径。"
        )

        # 清理资源并退出
        self.close()
        import sys

        sys.exit(1)

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 设置菜单
        settings_menu = menubar.addMenu("设置")

        # Cursor路径设置
        cursor_path_action = settings_menu.addAction("设置Cursor路径")
        cursor_path_action.triggered.connect(self.manual_set_cursor_path)

        # 查看当前路径
        view_path_action = settings_menu.addAction("查看当前路径")
        view_path_action.triggered.connect(self.view_current_cursor_path)

    def manual_set_cursor_path(self):
        """手动设置Cursor路径（菜单调用 - 严格模式）"""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "重新设置Cursor路径",
            "是否要重新设置Cursor安装路径？\n\n当前设置将被覆盖。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.force_select_valid_cursor_path():
                # 路径设置成功，重新检查版本
                from src.utils.cursor_version import CursorVersionDetector

                paths = CursorVersionDetector.get_cursor_paths()
                if paths:
                    self.status_bar.showMessage("✅ Cursor路径已更新，版本检测功能已恢复")
                    print("✅ 手动路径设置成功，功能已恢复")

    def view_current_cursor_path(self):
        """查看当前Cursor路径设置"""
        from PyQt6.QtWidgets import QMessageBox

        current_path = self.config.get("cursor", "app_path")
        if current_path:
            QMessageBox.information(self, "当前Cursor路径", f"当前设置的Cursor安装路径：\n\n{current_path}")
        else:
            QMessageBox.information(
                self, "当前Cursor路径", "尚未设置Cursor安装路径。\n\n程序将尝试在默认位置查找Cursor。"
            )

    def update_usage_data(self):
        """更新数据用量显示 - ，使用异步线程"""
        print("🔍 [REFRESH-DEBUG] update_usage_data 方法被调用")
        print("=== 开始更新顶部账号信息 ===")

        if hasattr(self, "_is_updating") and self._is_updating:
            print("🔍 [REFRESH-DEBUG] 更新已在进行中，跳过本次请求")
            return

        # 取消之前的更新线程
        if (
            hasattr(self, "_current_update_thread")
            and self._current_update_thread
            and self._current_update_thread.isRunning()
        ):
            print("🔍 [REFRESH-DEBUG] 取消之前的更新线程")
            self._current_update_thread.cancel()
            self._current_update_thread.wait(1000)

        self._is_updating = True
        if hasattr(self, "refresh_account_button"):
            self.refresh_account_button.setEnabled(False)

        print("🔍 [REFRESH-DEBUG] 准备启动异步更新线程")

        # 更新UI显示
        if hasattr(self, "current_email_label"):
            self.current_email_label.setText("查询中...")
        if hasattr(self, "current_subscription_label"):
            self.current_subscription_label.setText("查询中...")

        self.status_bar.showMessage("🔄 正在刷新账号使用额度...")
        print("🔍 [REFRESH-DEBUG] 启动更新线程")

        # 启动使用额度更新线程
        try:
            self._current_update_thread = UsageUpdateThread()
            self._current_update_thread.update_finished.connect(self.handle_usage_update)
            self._current_update_thread.start()
            print("🔍 [REFRESH-DEBUG] 更新线程启动成功")
        except Exception as e:
            print(f"🚨 [REFRESH-DEBUG] 启动更新线程失败: {e}")
            self._is_updating = False
            if hasattr(self, "refresh_account_button"):
                self.refresh_account_button.setEnabled(True)

    def handle_usage_update(self, account_details):
        """处理账户信息更新结果 - 支持渐进式更新"""
        print("🔍 [REFRESH-DEBUG] handle_usage_update 被调用")
        print("=== 处理使用额度更新结果 ===")

        self._is_updating = False
        if hasattr(self, "refresh_account_button"):
            self.refresh_account_button.setEnabled(True)

        if not account_details:
            print("未获取到账号信息")
            # 更新顶部面板显示未登录状态
            self.current_email_label.setText("当前账号: 未登录或未检测到")
            self.current_subscription_label.setText("订阅类型: 无")
            # 设置未登录状态的颜色
            self.current_subscription_label.setStyleSheet("color: #888888;")
            self.current_usage_label.setText("使用额度: 无法获取")
            self.current_usage_label.setStyleSheet("color: #888888;")
            self.status_bar.showMessage("❌ 获取账号信息失败")
            return

        email = account_details.get("email", "未知")
        subscription = account_details.get("subscription", "未知")
        subscription_display = account_details.get("subscription_display", "未知")
        aggregated_usage_cost = account_details.get("aggregated_usage_cost", 0.0)
        monthly_invoice_cost = account_details.get("monthly_invoice_cost", 0.0)
        trial_days = account_details.get("trial_days", 0)
        source = account_details.get("source", "unknown")

        print(f"邮箱: {email}")
        print(f"订阅类型: {subscription}")
        print(f"订阅显示: {subscription_display}")
        print(f"数据来源: {source}")

        # 更新顶部面板信息
        display_email = email if len(email) <= 30 else f"{email[:30]}..."
        self.current_email_label.setText(f"当前账号: {display_email}")
        self.current_email_label.setToolTip(email)

        # 🎨 设置订阅类型颜色
        subscription_color = self.get_subscription_color(subscription_display)
        color_hex = f"#{subscription_color.red():02x}{subscription_color.green():02x}{subscription_color.blue():02x}"

        # 使用富文本，只有订阅类型值变色
        self.current_subscription_label.setText(
            f'订阅类型: <span style="color: {color_hex};">{subscription_display}</span>'
        )
        self.current_subscription_label.setStyleSheet("color: #cccccc;")  # 标签文字保持灰色

        # 显示订阅类型和使用费用
        if subscription == "pro":
            if isinstance(aggregated_usage_cost, (int, float)) and isinstance(monthly_invoice_cost, (int, float)):
                self.update_usage_cost_display(aggregated_usage_cost, monthly_invoice_cost)
            else:
                print("费用数据格式错误")
                self.current_usage_label.setText("使用额度: 费用查询失败")
                self.current_usage_label.setStyleSheet("color: #FF9800;")  # 橙色警告
        elif subscription == "free_trial" and trial_days > 0:
            trial_usage_cost = account_details.get("trial_usage_cost", 0.0)
            if trial_usage_cost > 0:
                display_text = f"{trial_usage_cost:.2f}$/{trial_days}天"
                print(f"试用版费用显示: {display_text}")
                self.current_usage_label.setText(f"试用额度: {display_text}")
                self.current_usage_label.setStyleSheet("color: #FF00FF;")  # 紫色试用
            else:
                display_text = f"{trial_days}天"
                print(f"试用版天数显示: {display_text}")
                self.current_usage_label.setText(f"试用额度: {display_text}")
                self.current_usage_label.setStyleSheet("color: #FF00FF;")  # 紫色试用
        else:
            self.current_usage_label.setText("使用额度: 查询完成")
            self.current_usage_label.setStyleSheet("color: #cccccc;")

        self.status_bar.showMessage(f"✅ 账号信息更新完成 (来源: {source})")
        print("=== 顶部账号信息更新完成 ===")

    def update_usage_cost_display(self, aggregated_usage_cost, monthly_invoice_cost):
        """更新使用费用显示，显示(A+B=C$)格式"""
        try:
            total_sum = aggregated_usage_cost + monthly_invoice_cost
            display_text = (
                f"({int(round(aggregated_usage_cost))}+{int(round(monthly_invoice_cost))}={int(round(total_sum))}$)"
            )

            # 根据总费用确定颜色 - 和原项目完全一样
            if total_sum < 50:
                color = "#00FF00"  # 绿色
                tooltip = "额度足够"
            elif total_sum < 71:
                color = "#FFFF00"  # 黄色
                tooltip = "使用透支额度"
            else:
                color = "#FF0000"  # 红色
                tooltip = "即将耗尽"

            print(f"费用显示: {display_text}, 颜色: {color}, 提示: {tooltip}")

            # 更新顶部面板的使用额度标签 - 清晰可见！
            self.current_usage_label.setText(f"使用额度: {display_text}")
            self.current_usage_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            self.current_usage_label.setToolTip(
                f"{tooltip} - a值(聚合费用): {aggregated_usage_cost:.2f}$, b值(月度账单): {monthly_invoice_cost:.2f}$"
            )

        except Exception as e:
            print(f"更新使用费用显示时出错: {e}")
            self.current_usage_label.setText("使用额度: 计算错误")
            self.current_usage_label.setStyleSheet("color: #FF0000;")
