# -*- coding: utf-8 -*-
"""
Cursor管理模块 - 核心管理功能
"""

import os
import json
import shutil
import hashlib
import uuid
from datetime import datetime

class CursorManager:
    """Cursor管理类 - 核心管理功能实现"""
    
    def __init__(self, config):
        """初始化Cursor管理器"""
        self.config = config
        self.account_machine_id_dir = os.path.join(config.config_dir, 'account_machine_ids')
        self._patcher = None
    
    def get_cursor_account_details(self):
        """获取当前Cursor账号详情
        
        获取Cursor账号的详细信息
        实际调用数据库查询获取当前登录的账号信息
        
        Returns:
            Dict: 包含email, user_id, token等字段的账号详情，失败时返回None
        """
        import os
        import sys
        import sqlite3
        import json
        
        try:
            # 🔧 使用和main_window.py中_get_account_from_state_db相同的逻辑
            if sys.platform == 'win32':
                db_path = os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'state.vscdb')
            elif sys.platform == 'darwin':
                db_path = os.path.abspath(os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage/state.vscdb'))
            else:  # Linux
                db_path = os.path.expanduser('~/.config/Cursor/User/globalStorage/state.vscdb')
            
            if not os.path.exists(db_path):
                print(f"⚠️ Cursor数据库不存在: {db_path}")
                return None
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT key, value 
                FROM ItemTable 
                WHERE key IN (
                    'cursorAuth/accessToken',
                    'cursorAuth/refreshToken',
                    'cursorAuth/cachedEmail',
                    'cursorAuth/userId',
                    'cursorAuth/email'
                )
            ''')
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                print("⚠️ 未找到Cursor认证信息")
                return None
            
            auth_data = {}
            for key, value in results:
                if key == 'cursorAuth/accessToken':
                    auth_data['token'] = value.strip('"') if value else None
                elif key == 'cursorAuth/refreshToken':
                    auth_data['refresh_token'] = value.strip('"') if value else None
                elif key == 'cursorAuth/cachedEmail':
                    # 🔧 优先使用cachedEmail，与topbar保持一致
                    auth_data['email'] = value.strip('"') if value else None
                elif key == 'cursorAuth/email':
                    # 🔧 只有当cachedEmail不存在时才使用email
                    if 'email' not in auth_data:
                        auth_data['email'] = value.strip('"') if value else None
                elif key == 'cursorAuth/userId':
                    auth_data['user_id'] = value.strip('"') if value else None
            
            # 🔧 从JWT token中提取user_id和真实邮箱
            if auth_data.get('token'):
                try:
                    from .jwt_utils import JWTUtils
                    payload = JWTUtils.decode_jwt_payload(auth_data['token'])
                    if payload:
                        sub = payload.get('sub', '')
                        if '|' in sub:
                            if not auth_data.get('user_id'):
                                auth_data['user_id'] = sub.split('|')[1]
                        
                        # 优先使用JWT中的真实邮箱
                        email_fields = ['email', 'user_email', 'preferred_username', 'name']
                        for field in email_fields:
                            email = payload.get(field)
                            if email and '@' in str(email) and not str(email).endswith('@cursor.local'):
                                auth_data['email'] = email
                                break
                except Exception as e:
                    print(f"⚠️ JWT解析失败: {e}")
            
            if not auth_data.get('token') or not auth_data.get('email'):
                print("⚠️ 认证信息不完整")
                return None
            
            return auth_data
            
        except Exception as e:
            print(f"❌ 获取Cursor账号详情失败: {e}")
            return None
    
    def update_auth(self, email, access_token, refresh_token, user_id):
        """更新认证信息到Cursor数据库
        
        Args:
            email: 邮箱
            access_token: 访问令牌
            refresh_token: 刷新令牌
            user_id: 用户ID
            
        Returns:
            tuple: (是否成功, 消息)
        """
        try:
            import sqlite3
            import sys
            
            # 获取数据库路径
            if sys.platform == 'win32':
                db_path = os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'state.vscdb')
            elif sys.platform == 'darwin':
                db_path = os.path.abspath(os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage/state.vscdb'))
            else:  # Linux
                db_path = os.path.expanduser('~/.config/Cursor/User/globalStorage/state.vscdb')
            
            if not os.path.exists(db_path):
                return (False, f"Cursor数据库不存在: {db_path}")
            
            print(f"🔧 更新Cursor认证数据库: {db_path}")
            
            # 连接数据库并更新认证信息
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 🔧 关键步骤1：删除可能阻止认证的缓存键 ( line 348-350)
            delete_keys = [
                'telemetry.currentSessionDate',
                'workbench.auxiliarybar.pinnedPanels', 
                'notifications.perSourceDoNotDisturbMode',
                'vscode.typescript-language-features',
                'editorFontInfo',
                'workbench.auxiliarybar.placeholderPanels',
                'workbench.panel.placeholderPanels',
                'editorOverrideService.cache',
                'extensionsAssistant/recommendations',
                'cursorai/serverConfig',
                '__$__targetStorageMarker'
            ]
            
            print(f"🔧 清除 {len(delete_keys)} 个缓存键...")
            for key in delete_keys:
                cursor.execute('DELETE FROM ItemTable WHERE key = ?', (key,))
                print(f"   🗑️ 删除缓存: {key}")
            
            # 🔧 关键步骤2：更新认证字段 ()
            auth_updates = [
                ('cursorAuth/cachedSignUpType', 'Auth_0'),  # 🔑 关键字段
                ('cursorAuth/cachedEmail', email),
                ('cursorAuth/accessToken', access_token),
                ('cursorAuth/refreshToken', refresh_token),
                ('cursorAuth/userId', user_id),
                ('cursorAuth/email', email),
                ('cursorAuth/isAuthenticated', 'true'),
                ('cursorAuth/isLoggedIn', 'true'),
                ('cursorAuth/isAuthorized', 'true'),
            ]
            
            for key, value in auth_updates:
                # 🔧 INSERT OR REPLACE逻辑
                cursor.execute('SELECT COUNT(*) FROM ItemTable WHERE key = ?', (key,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute('INSERT INTO ItemTable (key, value) VALUES (?, ?)', (key, value))
                else:
                    cursor.execute('UPDATE ItemTable SET value = ? WHERE key = ?', (value, key))
                print(f"   ✅ 更新 {key}")
            
            conn.commit()
            conn.close()
            
            print("✅ Cursor认证信息更新成功")
            return (True, "认证信息更新成功")
            
        except Exception as e:
            print(f"❌ 更新认证信息失败: {e}")
            return (False, f"更新认证信息失败: {str(e)}")
    
    def apply_machine_id_patch(self, skip_permission_check=False):
        """应用机器ID补丁"""
        try:
            # 使用现有的补丁器
            success, message = self.patcher.apply_patch(skip_permission_check=skip_permission_check)
            return (success, message)
        except Exception as e:
            return (False, f"补丁应用失败: {str(e)}")
    
    @property
    def patcher(self):
        """延迟初始化的补丁器属性"""
        if self._patcher is None:
            from .patch_cursor_get_machine_id import CursorPatcher
            self._patcher = CursorPatcher(self.config)
        return self._patcher
    
    def reset_machine_ids(self, progress_callback=None, account_email=None):
        """重置Cursor机器ID - """
        try:
            print('开始重置Cursor机器ID...')
            if progress_callback:
                progress_callback('开始重置Cursor机器ID...')
            
            success, message, new_ids = self.reset_and_backup_machine_ids(account_email)
            
            if success:
                print('重置成功，开始应用机器ID补丁...')
                if progress_callback:
                    progress_callback('重置成功，开始应用机器ID补丁...')
                
                patch_success, patch_message = self.patcher.apply_patch(progress_callback)
                if patch_success:
                    message += f'；{patch_message}'
                    print(f'补丁应用成功: {patch_message}')
                    if progress_callback:
                        progress_callback(f'补丁应用成功: {patch_message}')
                else:
                    print(f'补丁应用失败: {patch_message}')
                    if progress_callback:
                        progress_callback(f'补丁应用失败: {patch_message}')
            
            return (success, message, new_ids)
            
        except Exception as e:
            error_msg = f'重置过程出错: {str(e)}'
            print(error_msg)
            if progress_callback:
                progress_callback(error_msg)
            return (False, error_msg, None)
    
    def reset_and_backup_machine_ids(self, account_email=None):
        """统一的重置机器ID方法，包含备份功能"""
        try:
            print('开始统一重置和备份机器ID...')
            success = True
            messages = []
            new_ids = {}
            
            # 重置storage.json
            storage_success, storage_msg, storage_ids = self._reset_storage_json(account_email)
            if storage_success:
                messages.append('storage.json重置成功')
                new_ids.update(storage_ids)
            else:
                success = False
                messages.append(f'storage.json重置失败: {storage_msg}')
            
            # 重置machineId文件
            machine_id_success, machine_id_msg, machine_id_value = self._reset_machine_id_file(account_email)
            if machine_id_success:
                messages.append('machineId文件重置成功')
                new_ids['machineId_file'] = machine_id_value
            else:
                success = False
                messages.append(f'machineId文件重置失败: {machine_id_msg}')
            
            # 保存账号专属配置
            if account_email and success and storage_success and machine_id_success:
                save_success = self._save_account_machine_ids(account_email, storage_ids, machine_id_value)
                if save_success:
                    print(f'已保存账号 {account_email} 的机器码配置')
                else:
                    print(f'保存账号 {account_email} 的机器码配置失败')
            
            result_message = '; '.join(messages)
            if success:
                print(f'机器ID重置和备份成功: {result_message}')
                return (True, '机器ID重置和备份成功', new_ids)
            else:
                print(f'机器ID重置和备份部分失败: {result_message}')
                return (False, f'机器ID重置和备份部分失败: {result_message}', new_ids)
                
        except Exception as e:
            error_msg = f'统一重置过程出错: {str(e)}'
            print(error_msg)
            return (False, error_msg, None)
    
    def _reset_storage_json(self, account_email=None):
        """重置和备份storage.json文件"""
        storage_path = self.config.get('cursor', 'storage_path')
        
        try:
            if not os.path.exists(storage_path):
                error_msg = f'配置文件不存在: {storage_path}'
                print(error_msg)
                return (False, error_msg, None)
            
            if not os.access(storage_path, os.R_OK | os.W_OK):
                error_msg = '无法读写配置文件，请检查文件权限！'
                print(error_msg)
                return (False, error_msg, None)
            
            print('读取当前storage.json配置...')
            with open(storage_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 备份
            backup_path = f'{storage_path}.old'
            print(f'备份storage.json到: {backup_path}')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            # 生成新的机器标识
            print('生成新的机器标识...')
            new_ids = self._generate_new_ids(account_email)
            config.update(new_ids)
            
            # 保存新配置
            print('保存新配置...')
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            print('storage.json机器标识重置成功！')
            return (True, 'storage.json机器标识重置成功', new_ids)
            
        except Exception as e:
            error_msg = f'storage.json重置过程出错: {str(e)}'
            print(error_msg)
            return (False, error_msg, None)
    
    def _reset_machine_id_file(self, account_email=None):
        """重置和备份machineId文件"""
        machine_id_path = self.config.get('cursor', 'machine_id_path')
        
        try:
            file_exists = os.path.exists(machine_id_path)
            if file_exists:
                print(f'machineId文件存在: {machine_id_path}')
                # 备份
                backup_path = f'{machine_id_path}.old'
                print(f'备份machineId到: {backup_path}')
                shutil.copy2(machine_id_path, backup_path)
            else:
                print('machineId文件不存在，将创建新文件')
                os.makedirs(os.path.dirname(machine_id_path), exist_ok=True)
            
            # 生成新的机器ID
            new_machine_id = self._get_account_machine_id_file_value(account_email)
            print(f'使用machineId: {new_machine_id}')
            
            with open(machine_id_path, 'w', encoding='utf-8') as f:
                f.write(new_machine_id)
            
            print('machineId文件重置成功！')
            return (True, 'machineId文件重置成功', new_machine_id)
            
        except Exception as e:
            error_msg = f'machineId文件重置过程出错: {str(e)}'
            print(error_msg)
            return (False, error_msg, None)
    
    def _get_account_machine_id_path(self, account_email):
        """获取账号专属机器码配置文件路径"""
        if not account_email:
            return None
        
        os.makedirs(self.account_machine_id_dir, exist_ok=True)
        safe_email = account_email.replace('@', '_')
        config_filename = f'{safe_email}.json'
        return os.path.join(self.account_machine_id_dir, config_filename)
    
    def _load_account_machine_ids(self, account_email):
        """加载账号专属机器码配置"""
        config_path = self._get_account_machine_id_path(account_email)
        if not config_path or not os.path.exists(config_path):
            print(f'账号 {account_email} 的机器码配置不存在')
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f'已加载账号 {account_email} 的机器码配置')
            return config
        except Exception as e:
            print(f'加载账号机器码配置失败: {str(e)}')
            return None
    
    def _save_account_machine_ids(self, account_email, storage_machine_ids, machine_id_file_value):
        """保存账号专属机器码配置"""
        config_path = self._get_account_machine_id_path(account_email)
        if not config_path:
            return False
        
        try:
            config_data = {
                'account_email': account_email,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'storage_machine_ids': storage_machine_ids,
                'machine_id_file': machine_id_file_value
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            print(f'已保存账号 {account_email} 的机器码配置')
            return True
            
        except Exception as e:
            print(f'保存账号机器码配置失败: {str(e)}')
            return False
    
    def _generate_new_ids(self, account_email=None):
        """生成新的机器ID - 真随机实现"""
        if account_email:
            existing_config = self._load_account_machine_ids(account_email)
            if existing_config and existing_config.get('storage_machine_ids'):
                print(f'使用账号 {account_email} 的已有机器码配置')
                return existing_config['storage_machine_ids']
        
        print(f"为账号 {account_email or '通用'} 生成新的机器码")
        

        dev_device_id = str(uuid.uuid4())
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()
        mac_machine_id = hashlib.sha256(os.urandom(64)).hexdigest()
        sqm_id = '{' + str(uuid.uuid4()).upper() + '}'
        
        new_ids = {
            'telemetry.devDeviceId': dev_device_id,
            'telemetry.macMachineId': mac_machine_id,
            'telemetry.machineId': machine_id,
            'telemetry.sqmId': sqm_id
        }
        
        return new_ids
    
    def _get_account_machine_id_file_value(self, account_email):
        """获取账号专属的machineId文件值"""
        if not account_email:
            return str(uuid.uuid4())
        
        existing_config = self._load_account_machine_ids(account_email)
        if existing_config and existing_config.get('machine_id_file'):
            print(f'使用账号 {account_email} 的已有machineId文件值')
            return existing_config['machine_id_file']
        else:
            new_machine_id_file = str(uuid.uuid4())
            print(f'为账号 {account_email} 生成新的machineId文件值')
            return new_machine_id_file
    
    def generate_account_machine_ids(self, account_email, force_new=False):
        """为指定账号生成或获取机器码配置"""
        if not account_email:
            storage_ids = self._generate_new_ids()
            machine_id_file = str(uuid.uuid4())
            return (storage_ids, machine_id_file)
        
        if not force_new:
            existing_config = self._load_account_machine_ids(account_email)
            if existing_config and existing_config.get('storage_machine_ids') and existing_config.get('machine_id_file'):
                print(f'使用账号 {account_email} 的已有机器码配置')
                return (existing_config['storage_machine_ids'], existing_config['machine_id_file'])
        
        print(f'为账号 {account_email} 生成新的机器码配置')
        storage_ids = self._generate_new_ids()
        machine_id_file = str(uuid.uuid4())
        
        # 保存配置
        self._save_account_machine_ids(account_email, storage_ids, machine_id_file)
        
        return (storage_ids, machine_id_file)
    
    @staticmethod
    def get_cursor_paths():
        """获取Cursor路径 - """
        import platform
        system = platform.system().lower()
        
        if system == 'windows':
            return {
                'global_storage': os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage'),
                'storage_json': os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'storage.json'),
                'machine_id': os.path.join(os.getenv('APPDATA'), 'Cursor', 'machineid')
            }
        elif system == 'darwin':
            return {
                'global_storage': os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage'),
                'storage_json': os.path.expanduser('~/Library/Application Support/Cursor/User/globalStorage/storage.json'),
                'machine_id': os.path.expanduser('~/Library/Application Support/Cursor/machineid')
            }
        else:  # Linux
            return {
                'global_storage': os.path.expanduser('~/.config/Cursor/User/globalStorage'),
                'storage_json': os.path.expanduser('~/.config/Cursor/User/globalStorage/storage.json'),
                'machine_id': os.path.expanduser('~/.config/Cursor/machineid')
            }
    
    @staticmethod
    def validate_cursor_installation():
        """验证Cursor安装是否有效"""
        from ..config import Config
        config = Config.get_instance()
        import platform
        system = platform.system().lower()
        
        # 1. 首先检查默认安装路径
        if system == 'windows':
            possible_paths = [
                os.path.join(os.getenv('LOCALAPPDATA', ''), 'Programs', 'Cursor'),
                os.path.join(os.getenv('PROGRAMFILES', ''), 'Cursor'),
                os.path.join(os.getenv('PROGRAMFILES(X86)', ''), 'Cursor')
            ]
            key_files = ['Cursor.exe', 'resources/app/out/main.js']
        elif system == 'darwin':
            possible_paths = ['/Applications/Cursor.app']
            key_files = ['Contents/MacOS/Cursor', 'Contents/Resources/app/out/main.js']
        else:  # Linux
            possible_paths = [
                '/usr/local/bin/cursor',
                '/usr/bin/cursor',
                os.path.expanduser('~/.local/share/cursor')
            ]
            key_files = ['cursor', 'resources/app/out/main.js']
        
        for path in possible_paths:
            if CursorManager._validate_cursor_path(path, key_files):
                # 保存检测到的默认路径到配置中
                config.set('cursor', 'app_path', path)
                return True, path
        
        # 2. 默认路径都找不到，检查用户之前设置的自定义路径
        custom_path = config.get('cursor', 'app_path')
        if custom_path and custom_path not in possible_paths:
            if CursorManager._validate_cursor_path(custom_path, key_files):
                return True, custom_path
        
        # 3. 都找不到，返回失败 - 让UI层处理用户路径选择
        return False, None
    
    @staticmethod
    def _validate_cursor_path(path, key_files):
        """验证指定路径是否为有效的Cursor安装"""
        if not os.path.exists(path):
            return False
        
        # 检查核心必需文件
        for file_path in key_files:
            if not os.path.exists(os.path.join(path, file_path)):
                return False
        
        return True
    
    @staticmethod
    def backup_cursor_config():
        """备份配置"""
        paths = CursorManager.get_cursor_paths()
        if os.path.exists(paths['global_storage']):
            backup_dir = f"cursor_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copytree(paths['global_storage'], backup_dir)
                return backup_dir
            except:
                pass
        return None

