# -*- coding: utf-8 -*-
"""
单账号刷新线程 - 订阅刷新功能
"""

import logging
import threading
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from .jwt_utils import JWTUtils
from .interruptible_api_call import InterruptibleApiCall

class SingleRefreshThread(QThread):
    """单个账号订阅刷新线程"""
    refresh_finished = pyqtSignal(int, bool, str, dict)  # row, success, message, updated_account
    
    def __init__(self, config, row, email, account):
        super().__init__()
        self.config = config
        self.row = row
        self.email = email
        self.account = account
        self.logger = logging.getLogger(__name__)
        self._stop_flag = False
        self._stop_event = threading.Event()
    
    def stop(self):
        """停止线程执行"""
        self._stop_flag = True
        self._stop_event.set()
        self.requestInterruption()
    
    def run(self):
        """执行单个账号订阅状态刷新"""
        try:
            if self._stop_flag or self.isInterruptionRequested():
                self.refresh_finished.emit(self.row, False, '刷新已取消', {})
                return
            
            # 🔧 ：使用access_token字段
            access_token = self.account.get('access_token')
            if not access_token:
                # 🔧 兼容性：尝试cookie_token字段
                access_token = self.account.get('cookie_token')
            
            if not access_token:
                self.refresh_finished.emit(self.row, False, f'账号 {self.email} 缺少访问令牌', {})
                return
            
            # 🔧 ：使用CursorApiClient + InterruptibleApiCall
            from ..config import Config
            config = Config.get_instance()
            
            # 🔧 创建简化的API客户端包装器
            class SimpleApiClient:
                def get_subscription_info(self, access_token, timeout=10):
                    return self._direct_api_call(access_token, timeout)
                
                def _direct_api_call(self, access_token, timeout):
                    """直接API调用 - """
                    user_id = self.account.get('user_id', '')
                    session_token = f'{user_id}%3A%3A{access_token.strip()}'
                    
                    headers = {
                        'accept': '*/*',
                        'accept-language': 'zh-CN,zh;q=0.9',
                        'content-type': 'application/json',
                        'origin': 'https://cursor.com',
                        'referer': 'https://cursor.com/cn/dashboard',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    cookies = {
                        'WorkosCursorSessionToken': session_token,
                        'NEXT_LOCALE': 'zh'
                    }
                    
                    response = requests.get(
                        'https://cursor.com/api/auth/stripe',
                        headers=headers,
                        cookies=cookies,
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    else:
                        return None
            
            # 绑定self到内部类
            api_client = SimpleApiClient()
            api_client.account = self.account
            
            interruptible_api = InterruptibleApiCall(api_client, self._stop_event)
            
            if self._stop_flag or self.isInterruptionRequested():
                self.refresh_finished.emit(self.row, False, '刷新已取消', {})
                return
            
            # 🔧 ：使用可中断API调用
            subscription_data = interruptible_api.get_subscription_info(access_token, timeout=10)
            
            if self._stop_flag or self.isInterruptionRequested():
                self.refresh_finished.emit(self.row, False, '刷新已取消', {})
                return
            
            if subscription_data and isinstance(subscription_data, dict):
                # 更新账号数据
                updated_account = self.account.copy()
                
                # 解析订阅类型
                membership_type = subscription_data.get('membershipType', 'free')
                display_name = self._get_membership_display_name(membership_type, subscription_data)
                
                updated_account['subscription_type'] = display_name
                updated_account['membershipType'] = membership_type
                updated_account['subscriptionData'] = subscription_data
                
                # 检查Token是否有效
                if membership_type == 'free' and not subscription_data.get('trialEligible', False):
                    updated_account['subscription_type'] = '废卡'
                
                self.refresh_finished.emit(self.row, True, f'账号 {self.email} 刷新成功: {display_name}', updated_account)
            else:
                self.refresh_finished.emit(self.row, False, f'账号 {self.email} API调用失败', {})
                
        except Exception as e:
            if not self._stop_flag and not self.isInterruptionRequested():
                self.logger.error(f'单个账号刷新线程出错: {str(e)}')
                self.refresh_finished.emit(self.row, False, f'刷新出错: {str(e)}', {})
    
    def _get_subscription_info(self, access_token):
        """获取订阅信息 - 真实API"""
        try:
            import requests
            
            # 🔧 从账号中提取user_id
            user_id = self.account.get('user_id', '')
            if not user_id:
                print(f"❌ 账号 {self.email} 缺少user_id")
                return None
            
            # 🔧 构建session_token - 
            session_token = f'{user_id}%3A%3A{access_token.strip()}'
            
            # 构建请求头 - 
            headers = {
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://cursor.com',
                'referer': 'https://cursor.com/cn/dashboard',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # 🔧 使用Cookie而不是Authorization header
            cookies = {
                'WorkosCursorSessionToken': session_token,
                'NEXT_LOCALE': 'zh'
            }
            
            # 🔧 调用正确的API端点 - 注释
            response = requests.get(
                'https://cursor.com/api/auth/stripe',
                headers=headers,
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 订阅信息获取成功: {self.email}")
                return data
            else:
                print(f"⚠️ 订阅API调用失败: {response.status_code}")
                if response.status_code == 401:
                    print("   可能是Token已过期或无效")
                elif response.status_code == 404:
                    print("   API端点可能已变更")
                return None
                
        except Exception as e:
            print(f"❌ 订阅API异常: {e}")
            return None
    
    def _get_membership_display_name(self, membership_type, subscription_data=None):
        """获取订阅类型显示名称 - 逻辑"""
        if membership_type == 'free':
            if subscription_data:
                trial_eligible = subscription_data.get('trialEligible', False)
                if trial_eligible:
                    return '仅auto'
                else:
                    return '废卡'
            else:
                return '废卡'
        elif membership_type == 'free_trial':
            return 'pro试用版'
        elif membership_type == 'pro':
            return 'pro专业版'
        elif membership_type == 'business':
            return '企业版'
        elif membership_type == 'team':
            return '团队版'
        elif membership_type == 'enterprise':
            return '企业版'
        else:
            return membership_type.capitalize() if membership_type else '未知'
