# -*- coding: utf-8 -*-
"""
使用额度更新线程 - 异步更新机制
"""

import os

from PyQt6.QtCore import QThread, pyqtSignal

from .platform_utils import get_platform_headers, get_user_agent


class UsageUpdateThread(QThread):
    """账户使用额度更新线程"""

    update_finished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._is_cancelled = False

    def cancel(self):
        """取消线程执行"""
        self._is_cancelled = True

    def run(self):
        """执行线程任务 - 严格API调用，避免浏览器触发"""
        print("🔍 [THREAD-DEBUG] UsageUpdateThread.run 开始执行")

        if self._is_cancelled:
            print("🔍 [THREAD-DEBUG] 线程已取消，退出")
            return

        try:
            print("🔍 [THREAD-DEBUG] 开始获取账户数据（纯API调用）")
            account_details = self._fetch_all_data_concurrent()

            if self._is_cancelled:
                print("🔍 [THREAD-DEBUG] 线程在数据获取后被取消")
                return

            if account_details:
                print("🔍 [THREAD-DEBUG] 成功获取账户数据，发送完成信号")
                account_details["stage"] = "complete"
                self.update_finished.emit(account_details)
            else:
                print("🔍 [THREAD-DEBUG] 未获取到账户数据，发送None")
                self.update_finished.emit({})  # 发送空字典而不是None

        except Exception as e:
            print(f"🚨 [THREAD-DEBUG] 获取账户信息时出错: {str(e)}")
            print(f"🔍 [THREAD-DEBUG] 异常详情: {type(e).__name__}")
            self.update_finished.emit({})  # 发送空字典

    def _fetch_all_data_concurrent(self):
        """并发获取所有账户数据 - 精简版实现"""
        print("开始获取账号数据...")

        if self._is_cancelled:
            return None

        try:
            # 第一阶段：获取基本账号信息（从state.vscdb获取真实token）
            print("第一阶段：获取基本账号信息")
            basic_info = self._get_complete_account_info(include_costs=False)

            if not basic_info:
                print("未获取到基本账户信息")
                return None

            print(f"获取到的基本信息: email={basic_info.get('email')}, subscription={basic_info.get('subscription')}")

            account_details = {
                "email": basic_info["email"],
                "user_id": basic_info["user_id"],
                "token": basic_info["access_token"],
                "subscription": basic_info["subscription"],
                "subscription_display": basic_info["subscription_display"],
                "trial_days": basic_info.get("trial_days", 0),
                "aggregated_usage_cost": 0.0,
                "monthly_invoice_cost": 0.0,
                "source": "state.vscdb",  # 标记数据来源
            }

            print(f"第一阶段完成：基本信息 - {account_details['email']} ({account_details['subscription_display']})")

            # 第二阶段：获取费用信息 - 真实API调用！
            if basic_info["subscription"] in ["pro", "free_trial"]:
                if self._is_cancelled:
                    return account_details

                print(f'第二阶段：开始获取{basic_info["subscription"]}用户费用信息')

                # 调用真实API获取费用数据 - 完整实现
                if basic_info["subscription"] == "pro":
                    # 🔧 基于真实浏览器Cookie的session_token格式
                    # 真实格式：user_01K3BM7NV0CKM2EFHWFB3P3VYP%3A%3AeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
                    # 这是 user_id%3A%3A[完整JWT_token] 的格式
                    # state.vscdb中存储的access_token本身就是完整的JWT token
                    session_token = f"{basic_info['user_id']}%3A%3A{basic_info['access_token']}"
                    print("🔍 [Session Token] 格式: user_id%3A%3A[JWT_token]")

                    # 获取聚合使用费用 (a值)
                    aggregated_cost = self._get_aggregated_usage_cost(session_token)
                    account_details["aggregated_usage_cost"] = aggregated_cost

                    # 获取月度账单费用 (b值)
                    monthly_cost = self._get_monthly_invoice_cost(session_token)
                    account_details["monthly_invoice_cost"] = monthly_cost

                    print(f"Pro专业版费用获取完成: a={aggregated_cost}$, b={monthly_cost}$")

                elif basic_info["subscription"] == "free_trial":
                    # 🔧 试用版也使用相同的session_token格式
                    session_token = f"{basic_info['user_id']}%3A%3A{basic_info['access_token']}"
                    trial_cost = self._get_trial_usage_cost(session_token)
                    account_details["trial_usage_cost"] = trial_cost
                    print(f"Pro试用版费用获取完成: {trial_cost}$")
            else:
                print("非Pro/试用版账号，跳过费用查询")

            return account_details

        except Exception as e:
            print(f"获取账户数据时出错: {str(e)}")
            return None

    def _get_complete_account_info(self, include_costs=False):
        """获取完整的账号信息"""
        try:
            import sqlite3
            import sys

            # 构建数据库路径 - 和原项目完全一样
            if sys.platform == "win32":
                db_path = os.path.join(os.getenv("APPDATA"), "Cursor", "User", "globalStorage", "state.vscdb")
            elif sys.platform == "darwin":
                db_path = os.path.abspath(
                    os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")
                )
            else:
                db_path = os.path.expanduser("~/.config/Cursor/User/globalStorage/state.vscdb")

            if not os.path.exists(db_path):
                print(f"⚠️ Cursor数据库不存在: {db_path}")
                return None

            # 连接SQLite数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 获取认证信息 - 和原项目完全一样的字段
            cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("cursorAuth/cachedEmail",))
            email_result = cursor.fetchone()
            email = email_result[0] if email_result else None

            cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("cursorAuth/accessToken",))
            token_result = cursor.fetchone()
            access_token = token_result[0] if token_result else None

            cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("cursorAuth/userId",))
            user_id_result = cursor.fetchone()
            user_id = user_id_result[0] if user_id_result else None

            cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("cursorAuth/cachedSignUpType",))
            status_result = cursor.fetchone()
            status = status_result[0] if status_result else None

            conn.close()

            # 检查是否登录
            is_logged_in = status == "Auth_0" and email and access_token

            if not is_logged_in:
                print("⚠️ 用户未登录或认证信息不完整")
                return None

            # 简单的订阅类型检测
            subscription_type = "pro"  # 默认为pro
            subscription_display = "pro专业版"

            print(f"✅ 获取到账号信息: {email}")

            return {
                "email": email,
                "user_id": user_id,
                "access_token": access_token,
                "subscription": subscription_type,
                "subscription_display": subscription_display,
                "trial_days": 0,
            }

        except Exception as e:
            print(f"❌ 获取完整账号信息失败: {e}")
            return None

    def _get_aggregated_usage_cost(self, session_token):
        """获取聚合使用费用"""
        try:
            pass

            import requests

            # 🔧 基于真实浏览器请求的完整Headers
            headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-type": "application/json",
                "origin": "https://cursor.com",
                "referer": "https://cursor.com/cn/dashboard?tab=billing",
                "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
                "sec-ch-ua-arch": '"x86"',
                "sec-ch-ua-bitness": '"64"',
                "sec-ch-ua-mobile": "?0",
                **get_platform_headers(),
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": get_user_agent(),
                "priority": "u=1, i",
            }

            # 🔧 基于真实浏览器的Cookie格式
            cookies = {
                "WorkosCursorSessionToken": session_token,
                "generaltranslation.locale-routing-enabled": "true",
                "NEXT_LOCALE": "cn",
                "GCLB": '"d676ed5633f606e7"',
            }

            # 🔧 基于真实浏览器请求的POST请求体
            import time

            # A值按套餐周期计算（从订阅开通日期开始的周期）
            # 真实逻辑：需要获取用户的Pro订阅开通日期，然后计算当前套餐周期
            # 例如：开通日期8月27日 → 当前周期8月27日-9月27日
            # 目前使用简化逻辑：过去30天（实际应该调用API获取订阅信息）

            end_time_ms = int(time.time() * 1000)  # 当前时间戳（毫秒）

            # TODO: 实现真实的套餐周期计算逻辑
            # 1. 从API或数据库获取用户的Pro订阅开通日期
            # 2. 计算当前套餐周期的开始日期
            # 3. 使用套餐周期作为时间范围
            # 当前使用30天作为近似值
            start_time_ms = end_time_ms - (30 * 24 * 60 * 60 * 1000)  # 30天前（近似套餐周期）

            request_body = {"teamId": -1, "startDate": start_time_ms, "endDate": end_time_ms}  # -1表示个人账户

            print("🔍 [A值时间范围] 注意：当前使用30天近似计算")
            print("🔍 [A值时间范围] 真实逻辑应该按套餐周期计算（开通日期+N个月）")

            print("🔍 [A值API] 使用POST方法调用聚合使用费用API")
            print("🔍 [A值API] 请求参数: teamId=-1, 时间范围: 近似30天（应为套餐周期）")
            response = requests.post(
                "https://cursor.com/api/dashboard/get-aggregated-usage-events",
                headers=headers,
                cookies=cookies,
                json=request_body,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()

                # 🔧 基于真实响应结构解析数据
                total_cost_cents = data.get("totalCostCents", 0)
                cost_dollars = total_cost_cents / 100.0

                # 输出详细信息
                aggregations = data.get("aggregations", [])
                if aggregations:
                    for agg in aggregations:
                        model = agg.get("modelIntent", "Unknown")
                        input_tokens = agg.get("inputTokens", "0")
                        output_tokens = agg.get("outputTokens", "0")
                        cache_read = agg.get("cacheReadTokens", "0")
                        cache_write = agg.get("cacheWriteTokens", "0")
                        print(
                            f"🔍 [模型使用] {model}: 输入{input_tokens}, 输出{output_tokens}, "
                            f"缓存读取{cache_read}, 缓存写入{cache_write}"
                        )

                print(f"✅ 聚合使用费用(A值): {total_cost_cents} cents = {cost_dollars:.2f}$")
                return cost_dollars
            else:
                print(f"⚠️ 聚合费用API调用失败: {response.status_code}")
                return 0.0

        except Exception as e:
            print(f"❌ 聚合费用API异常: {e}")
            return 0.0

    def _get_monthly_invoice_cost(self, session_token):
        """获取月度账单费用"""
        try:
            import datetime

            import requests

            # 🔧 基于真实浏览器请求的完整Headers
            headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-type": "application/json",
                "origin": "https://cursor.com",
                "referer": "https://cursor.com/cn/dashboard?tab=billing",
                "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
                "sec-ch-ua-arch": '"x86"',
                "sec-ch-ua-bitness": '"64"',
                "sec-ch-ua-mobile": "?0",
                **get_platform_headers(),
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": get_user_agent(),
                "priority": "u=1, i",
            }

            # 🔧 基于真实浏览器的Cookie格式
            cookies = {
                "WorkosCursorSessionToken": session_token,
                "generaltranslation.locale-routing-enabled": "true",
                "NEXT_LOCALE": "cn",
                "GCLB": '"0dbb925141538464"',
            }

            # 🔧 基于真实浏览器请求的POST请求体
            # B值按自然月计算，月份从1开始计数（1=January, 9=September）

            # 获取当前时间 - 优先使用北京时间（东八区）
            try:
                import pytz

                beijing_tz = pytz.timezone("Asia/Shanghai")
                current_time = datetime.datetime.now(beijing_tz)
                print(f"🔍 [时间] 使用北京时间: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            except ImportError:
                # 备用方案：使用系统本地时间
                current_time = datetime.datetime.now()
                print(f"🔍 [时间] 使用系统时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (pytz不可用)")

            # 🔧 修正：B值查询上个月的账单，不是当前月
            # 基于真实浏览器抓包：9月22日查询的是8月账单
            if current_time.month == 1:
                # 如果当前是1月，查询上年12月
                target_month = 12
                target_year = current_time.year - 1
            else:
                # 否则查询当前年的上个月
                target_month = current_time.month - 1
                target_year = current_time.year

            request_body = {
                "month": target_month,  # 月份从1开始计数（1=January, 9=September）
                "year": target_year,
                "includeUsageEvents": False,  # 只需要账单项目，不需要详细使用事件
            }

            print("🔍 [B值API] 使用POST方法调用月度账单API")
            print(f"🔍 [B值API] 请求参数: 月份={target_month}, 年份={target_year} ({target_month}月)")
            print("🔍 [B值API] 查询上个月账单")

            # 🔧 重要发现：这是POST请求，不是GET！
            response = requests.post(
                "https://cursor.com/api/dashboard/get-monthly-invoice",
                headers=headers,
                cookies=cookies,
                json=request_body,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()

                # 🔧 基于真实响应结构解析B值

                # 🔧 基于真实响应结构解析B值
                items = data.get("items", [])
                if not items:
                    print("🔍 [B值API] items字段为空")
                    print(f"🔍 [B值API-DEBUG] items内容: {items}")
                    return 0.0

                # B值计算：累加所有正数cents（费用），忽略负数cents（已支付）
                total_unpaid_cents = 0
                paid_cents = 0

                for item in items:
                    cents = item.get("cents", 0)
                    description = item.get("description", "")

                    if cents > 0:
                        # 正数是未支付的费用
                        total_unpaid_cents += cents
                        print(f"🔍 [费用项目] +{cents / 100:.2f}$: {description[:60]}...")
                    elif cents < 0:
                        # 负数是已支付的费用
                        paid_cents += abs(cents)
                        print(f"🔍 [已支付] -{abs(cents) / 100:.2f}$: {description[:60]}...")

                # 转换为美元
                b_value_dollars = total_unpaid_cents / 100.0
                paid_dollars = paid_cents / 100.0

                # 输出详细信息
                has_unpaid_invoice = data.get("hasUnpaidMidMonthInvoice", False)
                hard_limit = data.get("lastHardLimitCents", 0) / 100.0

                print(f"✅ 月度账单(B值): {total_unpaid_cents} cents = {b_value_dollars:.2f}$")
                print(f"🔍 [账单状态] 未付费用: ${b_value_dollars:.2f}, 已支付: ${paid_dollars:.2f}")
                print(f"🔍 [账单状态] 有未付中期账单: {has_unpaid_invoice}, 硬性限制: ${hard_limit:.2f}")

                return b_value_dollars
            else:
                if response.status_code == 500:
                    print("🚨 月度账单API服务器错误(500) - 这是Cursor服务器问题，不是代码问题")
                    print("💡 建议：稍后重试或联系Cursor支持")
                else:
                    print(f"⚠️ 月度账单API调用失败: {response.status_code}")
                return 0.0

        except Exception as e:
            print(f"❌ 月度账单API异常: {e}")
            return 0.0

    def _retry_monthly_invoice_with_events(self, session_token, month, year):
        """重试B值API - 使用includeUsageEvents=true"""
        try:
            import requests

            headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-type": "application/json",
                "origin": "https://cursor.com",
                "referer": "https://cursor.com/cn/dashboard?tab=billing",
                "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
                "sec-ch-ua-mobile": "?0",
                **get_platform_headers(),
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": get_user_agent(),
                "priority": "u=1, i",
            }

            cookies = {
                "WorkosCursorSessionToken": session_token,
                "generaltranslation.locale-routing-enabled": "true",
                "NEXT_LOCALE": "cn",
                "GCLB": '"0dbb925141538464"',
            }

            # 🔧 重试：使用includeUsageEvents=true
            request_body = {"month": month, "year": year, "includeUsageEvents": True}  # 包含使用事件

            print(f"🔍 [B值重试] includeUsageEvents=true, 月份={month}, 年份={year}")

            response = requests.post(
                "https://cursor.com/api/dashboard/get-monthly-invoice",
                headers=headers,
                cookies=cookies,
                json=request_body,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                print(f"🔍 [B值重试-DEBUG] 重试响应: {data}")

                # 解析重试响应
                items = data.get("items", [])
                if items:
                    total_unpaid_cents = 0
                    for item in items:
                        cents = item.get("cents", 0)
                        if cents > 0:
                            total_unpaid_cents += cents
                            description = item.get("description", "")[:50]
                            print(f"🔍 [B值重试] 找到费用项目: +${cents / 100:.2f} - {description}")

                    if total_unpaid_cents > 0:
                        b_value = total_unpaid_cents / 100.0
                        print(f"✅ [B值重试] 成功获取B值: ${b_value:.2f}")
                        return b_value

                print("🔍 [B值重试] 重试后仍无账单项目")
                return 0.0
            else:
                print(f"❌ [B值重试] API调用失败: {response.status_code}")
                return 0.0

        except Exception as e:
            print(f"❌ [B值重试] 异常: {e}")
            return 0.0

    def _get_trial_usage_cost(self, session_token):
        """获取试用版费用API"""
        try:
            # 试用版也使用聚合费用API，但处理方式不同
            return self._get_aggregated_usage_cost(session_token)
        except Exception as e:
            print(f"❌ 试用版费用API异常: {e}")
            return 0.0
