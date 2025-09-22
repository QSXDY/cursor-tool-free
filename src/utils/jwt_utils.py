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
            parts = token.split('.')
            if len(parts) != 3:
                return None
                
            payload = parts[1]
            # 添加填充
            padding = len(payload) % 4
            if padding:
                payload += '=' * (4 - padding)
            
            # 解码
            decoded_bytes = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded_bytes.decode('utf-8'))
            
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
            email_fields = ['email', 'user_email', 'preferred_username', 'name']
            
            for field in email_fields:
                email = payload.get(field)
                if email and '@' in str(email):
                    print(f"✅ 从token提取邮箱: {email}")
                    return email
            
            # 如果没有直接的邮箱字段，尝试从sub字段分析
            sub = payload.get('sub')
            if sub and '@' in str(sub):
                print(f"✅ 从sub字段提取邮箱: {sub}")
                return sub
                
            return None
            
        except Exception as e:
            print(f"⚠️ 从token提取邮箱失败: {e}")
            return None
    
    @staticmethod
    def extract_user_id_from_token(token):
        """从JWT token中提取用户ID"""
        try:
            payload = JWTUtils.decode_jwt_payload(token)
            if not payload:
                return None
            
            # 尝试多种可能的用户ID字段
            user_id_fields = ['sub', 'user_id', 'userId', 'uid']
            
            for field in user_id_fields:
                user_id = payload.get(field)
                if user_id:
                    # 如果sub字段包含|分隔符，取最后一部分
                    if '|' in str(user_id):
                        parts = str(user_id).split('|')
                        for part in parts:
                            if part.startswith('user_'):
                                return part
                        return parts[-1]  # 默认返回最后一部分
                    return str(user_id)
            
            return None
            
        except Exception as e:
            print(f"⚠️ 从token提取用户ID失败: {e}")
            return None
