# -*- coding: utf-8 -*-
"""
配置管理模块 - 应用程序配置管理
"""

import json
import logging
import os
import sys


class Config:
    """配置管理类 - 统一管理应用程序配置"""

    _instance = None

    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance

    def __init__(self):
        """初始化配置管理器"""
        if Config._instance is not None:
            # 如果已有实例，复用配置
            self.config = Config._instance.config
            self.config_dir = Config._instance.config_dir
            self.config_file = Config._instance.config_file
            self.default_config = Config._instance.default_config
            return

        # 初始化新实例
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, "settings.json")
        os.makedirs(self.config_dir, exist_ok=True)

        # 默认配置设置
        self.default_config = {
            "app": {
                "auto_login": False,
                "language": "zh_CN",
                "theme": "light",
                "check_update": True,
                "update_interval": 7200,
                "version_code": 259,
                "version_name": "v2.5.9",
                "last_check_update_time": 0,
                "invitation_code": "",
                "ignored_versions": [],
            },
            "mail_settings": {
                "use_default": True,
                "register_email": "",
                "use_random_email": False,
                "email": "",
                "password": "",
                "imap_server": "imap.2925.com",
                "imap_port": 993,
            },
            "cursor": {
                "app_path": self._get_default_cursor_path(),
                "data_dir": self._get_default_cursor_data_dir(),
                "storage_path": self._get_default_storage_path(),
                "machine_id_path": self._get_default_machine_id_path(),
                "win_path": self._get_default_cursor_path() if sys.platform == "win32" else "",
                "browser_executable_path": "",
            },
            "browser": {
                "windows_priority": "edge",
                "macos_default": "chrome",
                "linux_default": "chrome",
                "incognito_mode": True,
                "disable_extensions": True,
            },
            "device": {
                "device_id": f"device_id_{os.urandom(8).hex()}",
            },
            "user": {
                "is_logged_in": False,
                "customer_id": "",
                "account": "",
                "token": "",
                "service_type": "",
                "service_expires_at": "",
                "bind_card_quota": 0,
                "invitation_code": "",
                "vip": 0,
                "last_login_time": "",
                "token_expires_at": "",
            },
            "accounts": [],
        }

        # 加载配置
        self.config = self._load_config()
        Config._instance = self

    def _get_config_dir(self):
        """获取配置目录"""
        if sys.platform == "win32":
            config_dir = os.path.join(os.getenv("APPDATA"), "CursorToolFree")
        elif sys.platform == "darwin":
            config_dir = os.path.expanduser("~/Library/Application Support/CursorToolFree")
        else:
            config_dir = os.path.expanduser("~/.config/CursorToolFree")
        return config_dir

    def _get_default_cursor_path(self):
        """获取Cursor应用程序默认路径"""
        if sys.platform == "win32":
            return os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "Cursor")
        elif sys.platform == "darwin":
            return "/Applications/Cursor.app"
        else:
            # Linux: 优先检测系统安装位置
            system_paths = [
                "/usr/bin/cursor",  # apt/deb 包安装
                "/usr/local/bin/cursor",  # 手动安装到系统
                "/snap/bin/cursor",  # snap 包
                "/var/lib/flatpak/exports/bin/cursor",  # flatpak 系统安装
                os.path.expanduser("~/.local/bin/cursor"),  # 用户本地安装
                os.path.expanduser("~/.local/share/cursor"),  # AppImage 解压
            ]

            for path in system_paths:
                if os.path.exists(path):
                    return path

            # 如果都没找到，返回最常见的系统路径
            return "/usr/bin/cursor"

    def _get_default_cursor_data_dir(self):
        """获取Cursor数据目录默认路径"""
        if sys.platform == "win32":
            return os.path.join(os.getenv("APPDATA"), "Cursor")
        elif sys.platform == "darwin":
            return os.path.expanduser("~/Library/Application Support/Cursor")
        else:
            return os.path.expanduser("~/.config/Cursor")

    def _get_default_storage_path(self):
        """获取Cursor存储文件默认路径"""
        if sys.platform == "win32":
            return os.path.join(os.getenv("APPDATA"), "Cursor", "User", "globalStorage", "storage.json")
        elif sys.platform == "darwin":
            return os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/storage.json")
        else:
            return os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")

    def _get_default_machine_id_path(self):
        """获取Cursor机器ID文件默认路径"""
        if sys.platform == "win32":
            return os.path.join(os.getenv("APPDATA"), "Cursor", "machineId")
        elif sys.platform == "darwin":
            return os.path.expanduser("~/Library/Application Support/Cursor/machineId")
        else:
            return os.path.expanduser("~/.config/Cursor/machineId")

    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # 合并默认配置
                merged_config = self.default_config.copy()
                for section, values in config.items():
                    if section in merged_config:
                        if isinstance(merged_config[section], dict) and isinstance(values, dict):
                            merged_config[section].update(values)
                        else:
                            merged_config[section] = values
                    else:
                        merged_config[section] = values

                return merged_config
            else:
                # 首次运行，保存默认配置
                self._save_config(self.default_config)
                return self.default_config

        except Exception as e:
            logging.error(f"加载配置文件时出错: {str(e)}")
            return self.default_config

    def _save_config(self, config):
        """保存配置到文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"保存配置文件时出错: {str(e)}")
            return False

    def get(self, section, key=None):
        """获取配置项"""
        try:
            if key is None:
                return self.config.get(section, {})
            else:
                return self.config.get(section, {}).get(key)
        except Exception as e:
            logging.error(f"获取配置项时出错: {str(e)}")
            return None

    def set(self, section, key, value):
        """设置配置项"""
        try:
            if section not in self.config:
                self.config[section] = {}

            if isinstance(key, str):
                # 单个键值对
                self.config[section][key] = value
            elif isinstance(key, list):
                # 列表数据
                self.config[section] = key
            else:
                # 直接设置整个section
                self.config[section] = key

            self._save_config(self.config)
            return True
        except Exception as e:
            logging.error(f"设置配置项时出错: {str(e)}")
            return False

    def get_version_info(self):
        """获取当前版本信息"""
        app_config = self.get("app")
        version_code = app_config.get("version_code", 259)
        version_name = app_config.get("version_name", "v2.5.9")
        return {"version_code": version_code, "version_name": version_name}

    def get_accounts(self):
        """获取所有保存的账号"""
        return self.config.get("accounts", [])

    def get_account(self, email):
        """根据邮箱获取单个账号"""
        accounts = self.get_accounts()
        for account in accounts:
            if account.get("email") == email:
                return account
        return None

    def add_account(self, account_data):
        """添加账号"""
        try:
            accounts = self.get_accounts()
            email = account_data.get("email")

            # 检查是否已存在，存在则更新
            for i, account in enumerate(accounts):
                if account.get("email") == email:
                    accounts[i] = account_data
                    self.config["accounts"] = accounts
                    return self._save_config(self.config)

            # 不存在则添加
            accounts.insert(0, account_data)
            self.config["accounts"] = accounts
            return self._save_config(self.config)

        except Exception as e:
            logging.error(f"添加账号时出错: {str(e)}")
            return False
