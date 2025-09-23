# -*- coding: utf-8 -*-
"""
JWT工具模块 - JWT处理功能
"""

import base64
import json


class JWTUtils:
    """JWT工具类"""

    @staticmethod
    def decode_jwt_payload(token):
        """解码JWT token的payload部分"""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            payload = parts[1]
            # 添加填充
            padding = len(payload) % 4
            if padding:
                payload += "=" * (4 - padding)

            # 解码
            decoded_bytes = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded_bytes.decode("utf-8"))

            return payload_data

        except Exception as e:
            print(f"⚠️ 解码JWT token失败: {e}")
            return None

    @staticmethod
    def extract_email_from_token(token):
        """从JWT token中提取邮箱地址"""
        try:
            payload = JWTUtils.decode_jwt_payload(token)
            if not payload:
                return None

            # 尝试多种可能的邮箱字段
            email_fields = ["email", "user_email", "preferred_username", "name"]

            for field in email_fields:
                email = payload.get(field)
                if email and "@" in str(email):
                    print(f"✅ 从token提取邮箱: {email}")
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

    @staticmethod
    def extract_user_id_from_token(token):
        """从JWT token中提取用户ID - 融入逆向代码的auth0格式支持"""
        try:
            if not token or not isinstance(token, str):
                return None

            payload = JWTUtils.decode_jwt_payload(token)
            if not payload:
                return None

            # 优先处理sub字段（基于逆向代码的验证逻辑）
            sub = payload.get('sub')
            if sub:
                sub_str = str(sub)
                # 处理auth0格式：auth0|user_xxx（逆向代码验证的格式）
                if 'auth0|user_' in sub_str:
                    return sub_str.replace('auth0|', '')
                # 处理其他|分隔格式
                elif '|' in sub_str:
                    parts = sub_str.split('|')
                    for part in parts:
                        if part.startswith('user_'):
                            return part
                    return parts[-1]  # 默认返回最后一部分
                # 直接返回sub值
                elif sub_str:
                    return sub_str

            # 尝试其他可能的用户ID字段
            user_id_fields = ["user_id", "userId", "uid", "id"]
            for field in user_id_fields:
                user_id = payload.get(field)
                if user_id:
                    return str(user_id)

            return None

        except Exception as e:
            print(f"⚠️ 从token提取用户ID失败: {e}")
            return None
