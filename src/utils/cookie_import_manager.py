# -*- coding: utf-8 -*-
"""
Cookie导入管理模块 - Cookie解析功能
"""

import base64
import hashlib
import json
import logging
from datetime import datetime


class CookieParser:
    """Cookie解析器"""

    @staticmethod
    def parse_cursor_cookie(cookie_string):
        """解析Cursor Cookie"""
        cookie_string = cookie_string.strip()

        if cookie_string.startswith("WorkosCursorSessionToken="):
            cookie_string = cookie_string[len("WorkosCursorSessionToken=") :]

        if "%3A%3A" in cookie_string:
            parts = cookie_string.split("%3A%3A", 1)
            if len(parts) == 2:
                user_id = parts[0]
                jwt_token = parts[1]

                token_info = CookieParser.decode_jwt_payload(jwt_token)

                return {
                    "user_id": user_id,
                    "jwt_token": jwt_token,
                    "cookie_token": cookie_string,
                    "token_info": token_info,
                    "email": CookieParser.extract_email_from_sub(token_info.get("sub", "")),
                    "subscription_type": CookieParser.detect_subscription_type(token_info),
                    "expires_at": token_info.get("exp", 0),
                }

        return None

    @staticmethod
    def decode_jwt_payload(jwt_token):
        """解码JWT payload"""
        try:
            parts = jwt_token.split(".")
            if len(parts) >= 2:
                payload = parts[1]
                payload += "=" * (4 - len(payload) % 4)
                decoded_bytes = base64.urlsafe_b64decode(payload.encode())
                return json.loads(decoded_bytes.decode())
        except Exception:
            pass
        return {}

    @staticmethod
    def extract_email_from_sub(sub_string):
        """从JWT sub字段提取邮箱"""
        if "|" in sub_string:
            for part in sub_string.split("|"):
                if "@" in part and "." in part:
                    return part
        return None

    @staticmethod
    def detect_subscription_type(token_info):
        """检测订阅类型"""
        scope = token_info.get("scope", "").lower()

        if "offline_access" in scope and "pro" in scope:
            return "pro专业版"
        elif "trial" in scope:
            return "pro试用版"
        else:
            return "仅auto"


class CookieImportManager:
    """Cookie导入管理器 - 完整的功能实现"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_cookie_info(self, cookie_text, skip_subscription=False):
        """解析单个cookie信息 - 重定向到批量解析"""
        try:
            success, message, accounts_list = self.parse_batch_cookie_info(cookie_text, skip_subscription)

            if success and accounts_list and len(accounts_list) == 1:
                return (True, message, accounts_list[0])
            elif success and accounts_list and len(accounts_list) > 1:
                return (False, f"检测到 {len(accounts_list)} 个账号，请使用批量导入", None)
            else:
                return (False, message, None)

        except Exception as e:
            return (False, f"解析过程中出错: {str(e)}", None)

    def parse_batch_cookie_info(self, cookie_text, skip_subscription=True):
        """解析批量cookie信息"""
        try:
            accounts_list = []
            lines = cookie_text.strip().split("\n")

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                try:
                    # 🔧 解析每行 - 支持多种格式
                    if "%3A%3A" in line:
                        success, message, account_info = self._parse_complete_format(
                            line, skip_subscription=skip_subscription
                        )
                    elif line.startswith("ey"):
                        success, message, account_info = self._parse_jwt_only_format(
                            line, skip_subscription=skip_subscription
                        )
                    else:
                        print(f"⚠️ 跳过第{line_num}行: 格式不支持")
                        continue

                    if success and account_info:
                        accounts_list.append(account_info)
                        print(f"✅ 解析第{line_num}行: {account_info.get('user_id', 'unknown')}")
                    else:
                        print(f"❌ 第{line_num}行解析失败: {message}")

                except Exception as e:
                    print(f"❌ 第{line_num}行解析错误: {e}")
                    continue

            if accounts_list:
                return (True, f"成功解析 {len(accounts_list)} 个账号的基本信息", accounts_list)
            else:
                return (False, "没有成功解析到任何有效账号", [])

        except Exception as e:
            return (False, f"批量解析过程中出错: {str(e)}", [])

    def _parse_complete_format(self, cookie_text, skip_subscription=False):
        """解析完整格式的cookie：user_xxx%3A%3Aeyj..."""
        try:
            parts = cookie_text.split("%3A%3A", 1)
            if len(parts) != 2:
                return (False, "cookie格式不正确，无法分割用户ID和token", None)

            user_id = parts[0].strip()
            access_token = parts[1].strip()

            if not user_id or not access_token:
                return (False, "用户ID或token为空", None)

            if not user_id.startswith("user_"):
                return (False, f"用户ID格式不正确，应以'user_'开头，当前: {user_id[:20]}...", None)

            return self._build_account_info(user_id, access_token, skip_subscription=skip_subscription)

        except Exception as e:
            self.logger.error(f"解析完整格式cookie时出错: {str(e)}")
            return (False, f"解析完整格式cookie时出错: {str(e)}", None)

    def _parse_jwt_only_format(self, jwt_token, skip_subscription=False):
        """解析纯JWT token格式：eyj..."""
        try:
            if not jwt_token.startswith("ey"):
                return (False, "JWT token格式不正确，应以'ey'开头", None)

            jwt_parts = jwt_token.split(".")
            if len(jwt_parts) != 3:
                return (False, "JWT token结构不正确，应包含三个部分", None)

            # 从JWT中提取user_id
            user_id = None
            try:
                payload = jwt_token.split(".")[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += "=" * padding
                decoded_bytes = base64.urlsafe_b64decode(payload)
                payload_json = json.loads(decoded_bytes.decode("utf-8"))

                if "sub" in payload_json:
                    sub = payload_json["sub"]
                    if "|" in sub and "user_" in sub:
                        parts = sub.split("|")
                        for part in parts:
                            if part.startswith("user_"):
                                user_id = part
                                break
            except Exception as e:
                self.logger.warning(f"从JWT payload中提取用户ID失败: {str(e)}")

            # 如果无法提取user_id，生成默认ID
            if not user_id:
                token_hash = hashlib.md5(jwt_token.encode()).hexdigest()[:24]
                user_id = f"user_{token_hash.upper()}"
                self.logger.info(f"为纯JWT token生成默认用户ID: {user_id}")

            return self._build_account_info(user_id, jwt_token, is_jwt_only=True, skip_subscription=skip_subscription)

        except Exception as e:
            self.logger.error(f"解析纯JWT token时出错: {str(e)}")
            return (False, f"解析纯JWT token时出错: {str(e)}", None)

    def _build_account_info(self, user_id, access_token, is_jwt_only=False, skip_subscription=False):
        """构建账号信息"""
        try:
            # 解析JWT token获取详细信息
            token_info = self._parse_jwt_token(access_token)

            # 🔧 ：统一字段结构，主要使用access_token
            account_info = {
                "user_id": user_id,
                "access_token": access_token,  # 🔑 主字段，
                "cookie_token": access_token,  # 兼容字段
                "jwt_token": access_token,
                "membershipType": "仅auto",
                "subscription_type": "仅auto",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "note": "",
                "status": "待应用",
            }

            # 🔧 直接复制cursor_account_tool的真实实现：从JWT token解析邮箱
            if token_info:
                # 从JWT sub字段提取邮箱 - cursor_account_tool的完整逻辑
                sub = token_info.get("sub", "")
                if "@" in sub:
                    # 直接包含邮箱
                    account_info["email"] = sub
                    print(f"✅ 从sub字段提取真实邮箱: {sub}")
                elif "|" in sub:
                    # auth0|user_xxx格式
                    parts = sub.split("|")
                    if len(parts) > 1:
                        user_part = parts[1]
                        if user_part.startswith("user_"):
                            clean_user_id = user_part.replace("user_", "")
                            account_info["email"] = f"{clean_user_id}@cursor.local"
                            print(f"✅ 生成cursor.local邮箱: {account_info['email']}")
                        else:
                            account_info["email"] = user_id
                    else:
                        account_info["email"] = user_id
                else:
                    account_info["email"] = user_id
                    print(f"⚠️ JWT中无邮箱信息，使用user_id: {user_id}")

                # 从JWT token_info检测订阅类型 - cursor_account_tool的方法
                if not skip_subscription:
                    subscription_type = self._detect_subscription_type(token_info)
                    account_info["subscription_type"] = subscription_type
                    print(f"✅ 从JWT检测订阅类型: {subscription_type}")
                else:
                    account_info["subscription_type"] = "未知"
            else:
                account_info["email"] = user_id
                account_info["subscription_type"] = "未知"
                print("⚠️ JWT解析失败，使用默认值")

            # 检查token过期时间
            if token_info:
                exp_time = token_info.get("exp", 0)
                if exp_time:
                    account_info["token_expires"] = exp_time

            return (True, "解析成功", account_info)

        except Exception as e:
            self.logger.error(f"构建账号信息时出错: {str(e)}")
            return (False, f"构建账号信息时出错: {str(e)}", None)

    def _parse_jwt_token(self, token):
        """解析JWT token"""
        try:
            parts = token.split(".")
            if len(parts) >= 2:
                payload = parts[1]
                # 添加必要的padding
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += "=" * padding

                decoded_bytes = base64.urlsafe_b64decode(payload)
                payload_json = json.loads(decoded_bytes.decode("utf-8"))
                return payload_json
        except Exception as e:
            self.logger.warning(f"解析JWT token失败: {str(e)}")
        return {}

    def _extract_email_from_token(self, token):
        """从JWT token中提取真实邮箱 - 直接复制cursor_account_tool的工作实现"""
        try:
            payload = self._parse_jwt_token(token)
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

            # 从sub字段的分隔部分提取
            if sub and "|" in sub:
                for part in sub.split("|"):
                    if "@" in part and "." in part:
                        print(f"✅ 从sub分隔部分提取邮箱: {part}")
                        return part

            return None

        except Exception as e:
            print(f"⚠️ 从token提取邮箱失败: {e}")
            return None

    def _detect_subscription_type(self, token_info):
        """检测订阅类型 - 直接复制cursor_account_tool的工作实现"""
        scope = token_info.get("scope", "").lower()

        if "offline_access" in scope and "pro" in scope:
            return "pro专业版"
        elif "trial" in scope:
            return "pro试用版"
        else:
            return "仅auto"

    def format_account_info(self, account_info):
        """格式化账号信息用于显示格式"""
        try:
            lines = []
            lines.append("=" * 50)
            lines.append("📋 账号信息解析结果")
            lines.append("=" * 50)
            lines.append(f"👤 用户ID: {account_info.get('user_id', 'N/A')}")
            lines.append(f"📧 邮箱: {account_info.get('email', 'N/A')}")
            lines.append(f"💳 订阅类型: {account_info.get('subscription_type', 'N/A')}")
            lines.append(f"🔑 Token: {account_info.get('access_token', 'N/A')[:50]}...")
            lines.append(f"⏰ 创建时间: {account_info.get('created_at', 'N/A')}")
            lines.append(f"📝 备注: {account_info.get('note', '无')}")
            lines.append("=" * 50)

            return "\n".join(lines)

        except Exception as e:
            self.logger.error(f"格式化账号信息时出错: {str(e)}")
            return f"格式化失败: {str(e)}"
