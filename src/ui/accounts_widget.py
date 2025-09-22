# -*- coding: utf-8 -*-
"""
账号管理界面模块 - 处理已保存账号的管理
"""
import base64
import concurrent.futures as concurrent
import datetime
import hashlib
import json
import logging
import secrets
import time
import re
import threading
import requests
from DrissionPage import ChromiumPage
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QDialog, QTextEdit, QLineEdit, QCheckBox, QApplication
from src.config import Config
from src.constants import CURSOR_URLS
# 🔧 修复导入错误 - 这些模块在我们的项目中不存在或有错误
# from src.utils.browser.browser_manager import BrowserManager  
from src.utils.version_manager import VersionManager
# from import_dialog import ImportDialog
# from utils.user_permission_client import UserPermissionClient, OperationCode, UserStatus
# from utils.cursor_process_manager import CursorProcessManager
# from src.utils.cursor_api_client import CursorApiClient
# 🔧 删除：未使用的批量处理导入 (单账号模式不需要)
# from utils.subscription_batch_processor import SubscriptionBatchProcessor

class InterruptibleApiCall:
    '''可中断的API调用包装器'''
    
    def __init__(self, api_client, stop_event):
        self.api_client = api_client
        self.stop_event = stop_event
        self.result = None
        self.exception = None

    
    def get_subscription_info(self, access_token, timeout = (10,)):
        '''可中断的订阅信息获取'''
        if self.stop_event.is_set():
            return None
        
        def api_call():
            pass
        # WARNING: Decompyle incomplete

        api_thread = threading.Thread(api_call, True, **('target', 'daemon'))
        api_thread.start()
        api_thread.join(timeout + 2, **('timeout',))
        if self.stop_event.is_set():
            return None
        if None.is_alive():
            return None
        if None.exception:
            raise self.exception
        return self.result



class SingleRefreshThread(QThread):
    '''单个账号订阅刷新线程'''
    refresh_finished = pyqtSignal(int, bool, str, dict)
    
    def __init__(self = None, config = None, row = None, email = None, account = None):
        super().__init__()
        self.config = config
        self.row = row
        self.email = email
        self.account = account
        self.logger = logging.getLogger(__name__)
        self._stop_flag = False
        self._stop_event = threading.Event()

    
    def stop(self):
        '''停止线程执行'''
        self._stop_flag = True
        self._stop_event.set()
        self.requestInterruption()

    
    def run(self):
        '''执行单个账号订阅状态刷新'''
        pass
    # WARNING: Decompyle incomplete

    __classcell__ = None


def generate_pkce_challenge():
    """
    生成 PKCE 的 code_verifier 和 code_challenge。
    1. 生成一个32字节的随机字符串作为 code_verifier。
    2. 对 code_verifier 进行 SHA-256 哈希。
    3. 对哈希结果进行 URL 安全的 Base64 编码，并去除末尾的 '=' 填充。
    """
    code_verifier = secrets.token_urlsafe(32)
    sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('utf-8')
    return (code_verifier, code_challenge)




class ApplyAccountThread(QThread):
    '''应用账号线程'''
    progress = pyqtSignal(str)
    result = pyqtSignal(bool, str)
    
    def __init__(self = None, cursor_manager = None, account = None):
        '''
        初始化应用账号线程
        
        Args:
            cursor_manager: Cursor管理器对象
            account: 账号信息
        '''
        super().__init__()
        self.cursor_manager = cursor_manager
        self.account = account
        self._should_stop = False

    
    def stop(self):
        '''停止线程执行'''
        self._should_stop = True

    
    def run(self):
        '''执行应用账号操作'''
        pass
    # WARNING: Decompyle incomplete

    __classcell__ = None


class AccountsWidget(QWidget):
    '''账号管理界面，处理已保存账号的管理'''
    status_message = pyqtSignal(str)
    
    def get_membership_display_name(membership_type, subscription_data, api_failed = (None, False)):
        '''
        统一的订阅类型显示名称映射
        
        Args:
            membership_type: 原始的membershipType值
            subscription_data: 订阅数据（用于获取trialEligible等信息）
            api_failed: API调用是否失败，失败时显示"获取失败"而不是"废卡"
            
        Returns:
            str: 用于显示的订阅类型名称
        '''
        if api_failed:
            return '获取失败'
        if None == 'free':
            if subscription_data:
                trial_eligible = subscription_data.get('trialEligible', False)
                if trial_eligible:
                    return '仅auto'
                return None
            return None
        if None == 'free_trial':
            return 'pro试用版'
        if None == 'pro':
            return 'pro专业版'
        if None == 'business':
            return '企业版'
        if None == 'team':
            return '团队版'
        if None == 'enterprise':
            return '企业版'
        if None:
            return membership_type.capitalize()

    get_membership_display_name = staticmethod(get_membership_display_name)
    
    def get_membership_color(display_name):
        '''
        获取订阅类型对应的颜色
        
        Args:
            display_name: 显示名称
            
        Returns:
            Qt.GlobalColor: 对应的颜色
        '''
        if display_name == '未知':
            return Qt.GlobalColor.gray
        if None == '仅auto':
            return Qt.GlobalColor.yellow
        if None == '废卡':
            return Qt.GlobalColor.red
        if None == '获取失败':
            return Qt.GlobalColor.darkRed
        if None == 'pro试用版':
            return Qt.GlobalColor.magenta
        if None in ('pro专业版', '企业版', '团队版'):
            return Qt.GlobalColor.green
        return None.GlobalColor.white

    get_membership_color = staticmethod(get_membership_color)
    
    def is_mmdd_format(remark):
        '''
        检查备注是否为MMdd格式（4位数字）
        
        Args:
            remark: 备注字符串
            
        Returns:
            bool: 是否为MMdd格式
        '''
        if not remark or isinstance(remark, str):
            return False
        remark = None.strip()
        if remark:
            pass
        return bool(re.match('^\\d{4}$', remark))

    is_mmdd_format = staticmethod(is_mmdd_format)
    
    def is_trial_format(remark):
        '''
        检查备注是否为试用期格式（MMdd或MMdd_xxx）
        
        Args:
            remark: 备注字符串
            
        Returns:
            bool: 是否为试用期格式
        '''

        if not remark:
            return False
        return bool(re.match(r'^\d{4}(_.*)?$', remark))