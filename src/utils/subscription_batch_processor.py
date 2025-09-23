# -*- coding: utf-8 -*-
"""
订阅批处理器 - 统一订阅获取逻辑
统一处理导入解析和一键刷新的订阅获取逻辑
"""

import concurrent.futures
import datetime
import logging
import re
import time
from typing import Callable, Dict, List, Optional, Tuple

from .platform_utils import get_user_agent


class SubscriptionBatchProcessor:
    """统一的订阅批处理器，用于解析导入和一键刷新 -"""

    def __init__(self, config, cookie_manager=None):
        """
        初始化订阅批处理器

        Args:
            config: 配置管理器
            cookie_manager: Cookie导入管理器（可选）
        """
        self.config = config
        self.cookie_manager = cookie_manager
        self.logger = logging.getLogger(__name__)

    def process_accounts_batch(
        self, accounts_list: List[Dict], preserve_remarks: bool = False, progress_callback: Optional[Callable] = None
    ) -> Tuple[bool, str, List[Dict]]:
        """
        批量处理账号订阅信息 -

        Args:
            accounts_list: 账号列表
            preserve_remarks: 是否保留原有备注（True=一键刷新模式，False=解析导入模式）
            progress_callback: 进度回调函数 callback(current, total, message)

        Returns:
            Tuple[bool, str, List[Dict]]: (成功, 消息, 处理后的账号列表)
        """
        try:
            total_accounts = len(accounts_list)
            if total_accounts == 0:
                return (True, "没有账号需要处理", [])

            self.logger.info(f"开始批量处理 {total_accounts} 个账号的订阅状态...")
            if progress_callback:
                progress_callback(0, total_accounts, "开始处理账号...")

            # 🔧 并发获取订阅状态
            processed_accounts = self._fetch_subscriptions_concurrently(
                accounts_list, preserve_remarks, progress_callback
            )

            if progress_callback:
                progress_callback(total_accounts, total_accounts, "处理完成！")

            success_count = len(processed_accounts)
            message = f"成功处理 {success_count} 个账号的订阅状态"
            return (True, message, processed_accounts)

        except Exception as e:
            error_msg = f"批量处理订阅状态时出错: {str(e)}"
            self.logger.error(error_msg)
            return (False, error_msg, [])

    def _fetch_subscriptions_concurrently(
        self, accounts_list: List[Dict], preserve_remarks: bool = False, progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """并发获取订阅状态 -"""
        total_accounts = len(accounts_list)

        def fetch_single_subscription(account_info):
            """获取单个账号的订阅状态"""
            email = account_info.get("email", "未知")
            self.logger.debug(f"正在获取账号 {email} 的订阅状态...")

            account_copy = account_info.copy()
            access_token = account_copy.get("cookie_token")  # 🔧 适配我们的字段名
            if not access_token:
                self.logger.warning(f"账号 {email} 缺少访问令牌")
                return account_copy

            try:
                # 🔧 调用订阅API - 实现
                subscription_data = self._get_subscription_info_api(access_token, account_copy.get("user_id", ""))

                if subscription_data and isinstance(subscription_data, dict):
                    self._process_subscription_update(account_copy, subscription_data, preserve_remarks)

                return account_copy

            except Exception as e:
                self.logger.error(f"获取账号 {account_info.get('email', '未知')} 订阅状态失败: {str(e)}")
                return account_info.copy()

        # 🔧 并发处理 -
        max_workers = min(5, total_accounts)
        self.logger.info(f"开始并发获取订阅状态：总账号数={total_accounts}，并发数={max_workers}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {}
            for i, account in enumerate(accounts_list):
                future = executor.submit(fetch_single_subscription, account)
                future_to_index[future] = i

            completed_accounts = [None] * total_accounts
            completed_count = 0

            for future in concurrent.futures.as_completed(future_to_index.keys()):
                try:
                    account_result = future.result()
                    index = future_to_index[future]
                    completed_accounts[index] = account_result
                    completed_count += 1

                    if progress_callback:
                        progress_callback(
                            completed_count, total_accounts, f"已处理 {completed_count}/{total_accounts} 个账号"
                        )

                except Exception as e:
                    self.logger.error(f"处理订阅状态结果时出错: {str(e)}")
                    index = future_to_index[future]
                    completed_accounts[index] = accounts_list[index]
                    completed_count += 1

        final_accounts = [acc for acc in completed_accounts if acc is not None]
        return final_accounts

    def _get_subscription_info_api(self, access_token: str, user_id: str):
        """调用订阅API获取信息 -"""
        try:
            import requests

            # 构建session token - 格式
            session_token = f"{user_id}%3A%3A{access_token.strip()}"

            # 构建请求头 -
            headers = {
                "accept": "*/*",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-type": "application/json",
                "origin": "https://cursor.com",
                "referer": "https://cursor.com/cn/dashboard",
                "user-agent": get_user_agent(),
            }

            # 使用Cookie -
            cookies = {"WorkosCursorSessionToken": session_token, "NEXT_LOCALE": "zh"}

            # 调用订阅API -
            response = requests.get("https://cursor.com/api/auth/stripe", headers=headers, cookies=cookies, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"🔍 API响应调试: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                if isinstance(data, dict) and "customer" in data:
                    print(f"🔍 Customer字段: {data['customer']}")
                return data
            else:
                print(f"⚠️ 订阅API调用失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 订阅API异常: {e}")
            return None

    def _process_subscription_update(self, account: Dict, subscription_data: Dict, preserve_remarks: bool = False):
        """
        处理订阅信息更新 -

        Args:
            account: 账号信息
            subscription_data: 订阅数据
            preserve_remarks: 是否保留原有备注
        """
        try:
            # 🔧 提取真实邮箱 - 从API响应中获取
            if "customer" in subscription_data and "email" in subscription_data["customer"]:
                account["email"] = subscription_data["customer"]["email"]
                print(f"✅ 从API获取真实邮箱: {account['email']}")

            # 🔧 处理订阅类型 - 逻辑
            membership_type = subscription_data.get("membershipType", "未知")
            individual_membership_type = subscription_data.get("individualMembershipType", membership_type)
            final_membership_type = individual_membership_type if individual_membership_type else membership_type

            if not isinstance(final_membership_type, str) or not final_membership_type.strip():
                final_membership_type = "未知"
            else:
                final_membership_type = final_membership_type.strip()

            # 🔧 设置订阅信息
            account["membershipType"] = final_membership_type
            account["subscriptionData"] = subscription_data
            account["subscriptionUpdatedAt"] = int(time.time())

            # 🔧 转换为显示名称
            display_name = self._get_membership_display_name(final_membership_type, subscription_data)
            account["subscription_type"] = display_name

            # 🔧 处理试用期备注
            if final_membership_type == "free_trial":
                trial_days = subscription_data.get("daysRemainingOnTrial", 0)
                if trial_days and trial_days > 0:
                    self._handle_trial_remark(account, trial_days, preserve_remarks)

        except Exception as e:
            self.logger.error(f"处理订阅更新时出错: {str(e)}")

    def _get_membership_display_name(self, membership_type: str, subscription_data: Dict = None):
        """获取订阅类型显示名称 - 逻辑"""
        if membership_type == "free":
            if subscription_data:
                trial_eligible = subscription_data.get("trialEligible", False)
                if trial_eligible:
                    return "仅auto"
                else:
                    return "废卡"
            else:
                return "废卡"
        elif membership_type == "free_trial":
            return "pro试用版"
        elif membership_type == "pro":
            return "pro专业版"
        elif membership_type == "business":
            return "企业版"
        elif membership_type == "team":
            return "团队版"
        elif membership_type == "enterprise":
            return "企业版"
        else:
            return membership_type.capitalize() if membership_type else "未知"

    def _handle_trial_remark(self, account: Dict, trial_days: int, preserve_remarks: bool = False):
        """处理试用账号的备注 -"""
        try:
            if preserve_remarks:
                original_remark = account.get("remark", "")
                new_remark = self._calculate_trial_expiry_remark_preserve(original_remark, trial_days)
            else:
                new_remark = self._calculate_trial_expiry_remark_simple(trial_days)

            if new_remark:
                account["remark"] = new_remark
                email = account.get("email", "未知")
                self.logger.info(f"为试用账号 {email} 设置备注: {new_remark}")

        except Exception as e:
            self.logger.error(f"处理试用备注时出错: {str(e)}")

    def _calculate_trial_expiry_remark_simple(self, days_remaining: int) -> str:
        """计算试用到期备注（简化版本）- 用于解析导入模式"""
        if days_remaining <= 0:
            return ""
        try:
            current_date = datetime.date.today()
            expiry_date = current_date + datetime.timedelta(days=int(days_remaining))
            expiry_mmdd = expiry_date.strftime("%m%d")
            return expiry_mmdd
        except Exception:
            return ""

    def _calculate_trial_expiry_remark_preserve(self, original_remark: str, days_remaining: int) -> str:
        """计算试用到期备注（保留原备注逻辑）- 用于一键刷新模式"""
        try:
            if days_remaining <= 0:
                return original_remark

            current_date = datetime.date.today()
            expiry_date = current_date + datetime.timedelta(days=int(days_remaining))
            expiry_mmdd = expiry_date.strftime("%m%d")

            original_remark = original_remark.strip() if original_remark else ""

            if original_remark and not self._is_trial_format(original_remark):
                return original_remark

            if original_remark and self._is_trial_format(original_remark):
                if "_" in original_remark:
                    parts = original_remark.split("_", 1)
                    return f"{expiry_mmdd}_{parts[1]}"
                else:
                    return expiry_mmdd
            else:
                return expiry_mmdd

        except Exception:
            return original_remark

    def _is_trial_format(self, remark: str) -> bool:
        """检查备注是否为试用期格式（MMdd或MMdd_xxx）"""
        if not remark or not isinstance(remark, str):
            return False

        remark = remark.strip()
        return bool(remark and (re.match(r"^\d{4}_", remark) or re.match(r"^\d{4}$", remark)))
