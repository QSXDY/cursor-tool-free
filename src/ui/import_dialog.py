# -*- coding: utf-8 -*-
"""
导入对话框模块 - Cookie导入功能界面
"""


from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
)

from ..utils.cookie_import_manager import CookieImportManager
from ..utils.platform_utils import get_user_agent

# 🔧 单账号模式：直接API调用，确保"一号一码"安全性


class ImportDialog(QDialog):
    """Cookie导入对话框 - 用户友好的导入界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导入Cookie账号")
        self.resize(1000, 650)
        self.account_data = None
        self.cookie_manager = CookieImportManager()

        # 获取父窗口的主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
        else:
            from .theme_manager import ThemeManager

            self.theme_manager = ThemeManager()

        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        # 创建水平分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        # 左侧：输入区域
        left_widget = QGroupBox("输入Cookie信息")
        left_widget.setMinimumWidth(450)
        left_widget.setMaximumWidth(450)
        left_layout = QVBoxLayout(left_widget)

        # 提示信息
        tip_text = """
🔒 安全模式：仅支持单个账号导入

支持以下格式：

【完整格式】单个账号：
user_01K45K78WFM4HCZB...%3A%3AeyJhbGciOi...

【简化格式】单个账号（省略用户ID）：
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

🛡️ 安全机制：为确保"一号一码"安全性，
每次只能导入一个账号，避免机器ID冲突

⚠️ 提示：仅支持JWT token，无需其他信息
        """.strip()

        tip_label = QLabel(tip_text)
        tip_label.setWordWrap(True)
        tip_label.setProperty("class", "tip-info")
        left_layout.addWidget(tip_label)

        # Cookie输入框
        self.cookie_input = QPlainTextEdit()
        self.cookie_input.setPlaceholderText(
            "user_01XXXXX%3A%3AeyJhbGciOiJIUzI1NiXXXX...\n\n" "为确保一号一码绑定，每次只能导入一个Cookie。"
        )
        left_layout.addWidget(self.cookie_input)

        # 备注输入
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("备注信息 (可选)")
        left_layout.addWidget(self.note_input)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.parse_btn = QPushButton("解析Cookie")
        self.parse_btn.setProperty("class", "primary")
        self.parse_btn.clicked.connect(self.parse_cookie)

        button_layout.addWidget(self.parse_btn)
        button_layout.addStretch()
        left_layout.addLayout(button_layout)

        # 右侧：解析结果显示
        right_widget = QGroupBox("解析结果")
        right_layout = QVBoxLayout(right_widget)

        # 解析结果显示区域
        self.result_display = QPlainTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText(
            "⭐ 解析结果将在这里显示：\n\n" '请先在左侧输入Cookie信息并点击"解析Cookie"'
        )
        right_layout.addWidget(self.result_display)

        # 底部按钮栏
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.import_btn = QPushButton("导入账号")
        self.import_btn.setProperty("class", "primary")
        self.import_btn.clicked.connect(self.add_account)
        self.import_btn.setEnabled(False)

        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("class", "primary")
        cancel_btn.clicked.connect(self.reject)

        bottom_layout.addWidget(self.import_btn)
        bottom_layout.addWidget(cancel_btn)
        right_layout.addLayout(bottom_layout)

        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)  # 左侧固定宽度
        splitter.setStretchFactor(1, 1)  # 右侧自适应

        # 应用主题样式
        self.apply_theme_style()

    def apply_theme_style(self):
        """应用主题样式到对话框"""
        if hasattr(self, 'theme_manager'):
            qss = self.theme_manager.generate_qss()
            self.setStyleSheet(qss)

    def parse_cookie(self):
        """解析Cookie"""
        cookie_text = self.cookie_input.toPlainText().strip()
        if not cookie_text:
            self._show_error("请输入cookie信息")
            return

        self.parse_btn.setEnabled(False)
        self._show_progress("🔄 正在解析cookie信息...")

        # 使用QTimer延迟执行，避免界面卡顿
        QTimer.singleShot(100, lambda: self._do_parse(cookie_text))

    def _do_parse(self, cookie_text):
        """执行解析 - 正确两阶段流程"""
        try:
            # 🔧 阶段1：解析基本信息，跳过订阅检测 -
            self._show_progress("🔄 正在解析基本信息...")
            success, message, accounts_list = self.cookie_manager.parse_batch_cookie_info(
                cookie_text, skip_subscription=True
            )

            if not success or not accounts_list:
                self._show_error(f"❌ 基本信息解析失败\n\n{message}")
                return

            if len(accounts_list) != 1:
                self._show_error(
                    f"🔒 安全限制：一次只能导入一个账号\n\n"
                    f"检测到 {len(accounts_list)} 个账号\n\n"
                    f'🛡️ 原因：Cursor使用"一号一码"机制\n'
                    f"每个账号需要独立的机器ID，\n"
                    f"同时导入多个账号可能导致冲突\n\n"
                    f"💡 解决方案：请分别导入每个账号"
                )
                return

            # 🔧 阶段2：单账号API获取真实邮箱和订阅信息（简化批量逻辑）
            self._show_progress("🌐 正在通过API获取真实邮箱和订阅信息...")

            # 🔧 简化：单账号不需要批量处理器，直接调用API
            account_info = accounts_list[0]  # 只有一个账号

            # 🔧 直接调用API获取真实订阅信息（复制single_refresh_thread的逻辑）
            try:
                import requests

                access_token = account_info.get("access_token") or account_info.get("cookie_token")
                user_id = account_info.get("user_id", "")

                if access_token and user_id:
                    # 构建session token
                    session_token = f"{user_id}%3A%3A{access_token}"

                    headers = {
                        "accept": "*/*",
                        "accept-language": "zh-CN,zh;q=0.9",
                        "content-type": "application/json",
                        "origin": "https://cursor.com",
                        "referer": "https://cursor.com/dashboard",
                        "user-agent": get_user_agent(),
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
                            account_info["subscription_type"] = "pro专业版"
                        elif membership_type == "free":
                            trial_eligible = subscription_data.get("trialEligible", False)
                            if trial_eligible:
                                account_info["subscription_type"] = "pro试用版"
                            else:
                                account_info["subscription_type"] = "free免费版"
                        else:
                            account_info["subscription_type"] = membership_type

                        print(f"✅ 单账号API获取订阅成功: {account_info.get('subscription_type', '未知')}")
                    else:
                        print(f"⚠️ API调用失败({response.status_code})，使用默认值")
                        account_info["subscription_type"] = "未知"
                else:
                    print("⚠️ 缺少访问令牌或用户ID，无法获取订阅信息")
                    account_info["subscription_type"] = "未知"
            except Exception as e:
                print(f"⚠️ API调用异常: {e}")
                account_info["subscription_type"] = "未知"

            if account_info:

                # 添加备注信息
                if self.note_input.text().strip():
                    account_info["note"] = self.note_input.text().strip()

                self.account_data = account_info

                # 显示解析结果
                formatted_text = self.cookie_manager.format_account_info(account_info)

                self.result_display.setPlainText(formatted_text)
                self.result_display.setProperty("class", "result-success")
                self.import_btn.setEnabled(True)
                print(
                    f"✅ 单账号API解析成功，邮箱: {account_info.get('email')}, 订阅: {account_info.get('subscription_type')}"
                )
            else:
                self._show_error("❌ 获取账号信息失败")
                self.account_data = None

        except Exception as e:
            self._show_error(f"❌ 解析过程出错\n\n{str(e)}")
            self.account_data = None
        finally:
            self.parse_btn.setEnabled(True)

    def _show_progress(self, message):
        """显示进度信息"""
        self.result_display.setPlainText(message)
        self.result_display.setProperty("class", "result-progress")

    def _show_error(self, message):
        """显示错误信息"""
        self.result_display.setPlainText(message)
        self.result_display.setProperty("class", "result-error")
        self.import_btn.setEnabled(False)

    def add_account(self):
        """添加账号"""
        if not self.account_data:
            QMessageBox.warning(self, "错误", "没有可导入的账号数据")
            return

        self.accept()

    def get_account_data(self):
        """获取解析后的账号数据"""
        return self.account_data
