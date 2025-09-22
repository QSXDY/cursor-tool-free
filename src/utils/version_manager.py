# -*- coding: utf-8 -*-
"""
版本管理模块 - 版本管理和API调用
"""

import json
import os
from datetime import datetime

from .cursor_version import CursorVersionDetector


class SmartAPIManager:
    """智能API管理器 - 实现版本探测和规则缓存"""

    def __init__(self, config=None):
        """初始化API管理器

        Args:
            config: 配置对象（用于JSON存储模式）或db_instance（用于SQLite模式）
        """
        self.config = config
        self.api_base_url = "https://cursor.aimoyu.top"
        self.fake_tool_version = 259  # 工具版本号

    def get_patch_rules(self, timeout=10):
        """获取补丁规则 - 直接使用内置降级规则，避免复杂的云端检测"""
        print("🔧 使用内置补丁规则...")

        # 🔧 简化：直接使用内置降级规则，不再执行云端版本探测
        cursor_version = CursorVersionDetector.get_cursor_version(formatted=True)
        print(f"📋 检测到Cursor软件版本: {cursor_version or '未知'}")
        print("✅ 使用内置降级规则 (跳过云端探测)")

        # 直接返回经过验证的内置规则
        fallback_rules = self._get_fallback_rules()
        print(f"📦 加载了 {len(fallback_rules)} 条内置补丁规则")

        return fallback_rules

    def _fetch_rules_from_api(self, version):
        """从API获取规则"""
        try:
            import requests

            api_url = f"{self.api_base_url}/scripts/replacements/{version}"
            params = {"tool_version": self.fake_tool_version}

            response = requests.get(api_url, params=params, timeout=5)

            if response.status_code == 200:
                rules_data = response.json()
                if rules_data.get("code") == 100:
                    # 工具版本过期
                    print(f"⚠️ 工具版本被拒绝，版本: {version}")
                    return None

                replacements = rules_data.get("replacements", [])
                if replacements and len(replacements) >= 2:
                    return replacements

            return None

        except Exception:
            # 静默处理异常
            return None

    def _get_cached_rules(self, version):
        """从JSON文件获取缓存规则 - 纯JSON存储"""
        try:
            cache_dir = os.path.join(self.config.config_dir, "api_cache")
            cache_file = os.path.join(cache_dir, f"{version}.json")

            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                return cache_data.get("rules", [])
            return None

        except Exception:
            return None

    def _cache_rules(self, version, rules):
        """缓存规则到JSON文件 - 纯JSON存储"""
        try:
            cache_dir = os.path.join(self.config.config_dir, "api_cache")
            os.makedirs(cache_dir, exist_ok=True)

            cache_file = os.path.join(cache_dir, f"{version}.json")
            cache_data = {
                "version": version,
                "rules": rules,
                "cached_at": datetime.now().isoformat(),
                "is_working": True,
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ 缓存规则失败: {e}")

    def _get_fallback_rules(self):
        """获取内置降级规则 - 经典规则"""
        return [
            {"name": "license_bypass_1", "old": "if(!this.isValidLicense)", "new": "if(false)"},
            {"name": "license_bypass_2", "old": "if (!this.isValidLicense)", "new": "if (false)"},
            {"name": "device_bind_bypass_1", "old": "if(deviceId !== storedDeviceId)", "new": "if(false)"},
            {"name": "device_bind_bypass_2", "old": "if (deviceId !== storedDeviceId)", "new": "if (false)"},
            {"name": "pro_check_bypass", "old": "this.isPro()", "new": "true"},
        ]


class VersionManager:
    """版本管理类"""

    API_BASE_URL = "https://cursor.aimoyu.top"
    _last_check_time = 0
    _min_check_interval = 3

    @staticmethod
    def get_api_base_url():
        """获取API基础URL"""
        return VersionManager.API_BASE_URL

    def __init__(self, config):
        """初始化版本管理器"""
        self.config = config
        self.api_base_url = VersionManager.get_api_base_url()
