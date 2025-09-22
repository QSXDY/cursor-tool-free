# -*- coding: utf-8 -*-
"""
Cursor补丁模块 - 系统补丁功能
支持main.js和workbench.js的智能补丁应用
"""

import os
import re
import shutil
from .cursor_version import CursorVersionDetector
from .version_manager import SmartAPIManager

class CursorPatcher:
    """Cursor补丁类 - 系统补丁功能"""
    
    def __init__(self, config=None):
        """初始化Cursor补丁器"""
        self.config = config
        self.cursor_paths = CursorVersionDetector.get_cursor_paths()
        
        if self.cursor_paths:
            self.main_path = self.cursor_paths['main_js']
            self.workbench_path = self.cursor_paths['workbench_js']
            self.pkg_path = self.cursor_paths['package_json']
        else:
            self.main_path = None
            self.workbench_path = None
            self.pkg_path = None
    
    def apply_patch(self, progress_callback=None, skip_permission_check=False):
        """应用Cursor补丁"""
        try:
            print("🔧 开始应用Cursor补丁...")
            
            if not self.cursor_paths:
                print("❌ 未找到Cursor安装路径")
                return (True, "未找到Cursor路径，跳过补丁（视为成功）")  # 宽容降级
            
            # 检查文件权限
            if not skip_permission_check:
                has_permission, error_msg = self.check_cursor_file_permission()
                if not has_permission:
                    return (False, f'权限检查失败: {error_msg}')
            
            success_count = 0
            
            # 修改main.js - 使用固定规则
            if progress_callback:
                progress_callback('正在修改main.js文件...')
            
            main_success = self.modify_main_js()
            if main_success:
                success_count += 1
                print("✅ main.js补丁应用成功")
            else:
                print("⚠️ main.js补丁应用失败")
            
            # 修改workbench.js - 使用智能API系统
            if progress_callback:
                progress_callback('正在修改workbench文件...')
            
            workbench_success = self.modify_workbench_js()
            if workbench_success:
                success_count += 1
                print("✅ workbench补丁应用成功")
            else:
                print("⚠️ workbench补丁应用失败")
            
            # 评估结果
            if success_count >= 1:
                if progress_callback:
                    progress_callback('补丁应用完成')
                return (True, 'Cursor补丁应用成功')
            else:
                return (True, '补丁应用失败，但继续执行')  # 宽容处理
                
        except Exception as e:
            error_msg = f'应用补丁时发生错误: {str(e)}'
            print(f"❌ {error_msg}")
            return (False, error_msg)
    
    def modify_main_js(self):
        """修改main.js文件"""
        if not self.main_path or not os.path.exists(self.main_path):
            print("❌ main.js文件不存在")
            return False
        
        try:
            # 备份原文件
            backup_path = self.main_path + ".backup"
            if not os.path.exists(backup_path):
                shutil.copy2(self.main_path, backup_path)
                print(f"📦 已备份main.js到: {backup_path}")
            
            # 读取文件
            with open(self.main_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 正则替换规则 - 机器ID绕过
            patterns = {
                r'async getMachineId\(\)\{return [^??]+\?\?([^}]+)\}': r'async getMachineId(){return \1}',
                r'async getMacMachineId\(\)\{return [^??]+\?\?([^}]+)\}': r'async getMacMachineId(){return \1}'
            }
            
            modified = False
            original_content = content
            
            for pattern, replacement in patterns.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True
                    print(f"✅ 应用main.js规则: {pattern[:30]}...")
            
            if content == original_content:
                print("⚠️ main.js没有找到需要修改的内容（可能已被修改）")
                return True  # 可能已经被修改过了
            
            if modified:
                with open(self.main_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ main.js文件修改完成")
                return True
            else:
                return True
                
        except Exception as e:
            print(f"❌ 修改main.js失败: {e}")
            return False
    
    def modify_workbench_js(self):
        """修改workbench.js文件 - 使用智能API系统"""
        if not self.workbench_path or not os.path.exists(self.workbench_path):
            print("⚠️ workbench文件不存在，跳过workbench修改")
            return True
        
        try:
            # 检查是否已被替换过
            if self._check_file_already_replaced(self.workbench_path):
                print("✅ workbench文件已经被替换过，跳过修改")
                return True
            
            # 🔧 使用启动时缓存的全局规则，避免重复版本探测
            if hasattr(self.config, '_global_patch_rules') and self.config._global_patch_rules:
                print("✅ 使用启动时缓存的补丁规则 (跳过版本探测)")
                rules = self.config._global_patch_rules
            else:
                print("⚠️ 未找到缓存规则，使用降级规则")
                # 使用内置降级规则，避免版本探测
                rules = [
                    {
                        'name': 'license_bypass_1',
                        'old': 'if(!this.isValidLicense)',
                        'new': 'if(false)'
                    },
                    {
                        'name': 'license_bypass_2', 
                        'old': '!this.isValidLicense',
                        'new': 'false'
                    }
                ]
            
            if not rules or len(rules) < 2:
                print("✅ 规则不足或获取失败，跳过workbench修改（视为成功）")
                return True
            
            # 备份并应用规则
            backup_path = self.workbench_path + ".backup"
            if not os.path.exists(backup_path):
                shutil.copy2(self.workbench_path, backup_path)
                print(f"📦 已备份workbench.js到: {backup_path}")
            
            # 读取文件并应用规则
            with open(self.workbench_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            changes_made = 0
            for rule in rules:
                name = rule['name']
                old = rule['old']
                new = rule['new']
                
                if old in content:
                    content = content.replace(old, new)
                    changes_made += 1
                    print(f"✅ 应用规则: {name}")
            
            if changes_made > 0:
                # 添加替换标记
                content = '/*replace*/\n' + content
                
                with open(self.workbench_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ workbench智能补丁完成: {changes_made} 个规则已应用")
                return True
            else:
                print("⚠️ workbench没有找到需要替换的内容")
                return True  # 宽容处理
                
        except Exception as e:
            print(f"❌ 智能修改workbench失败: {e}")
            return False
    
    def _check_file_already_replaced(self, file_path):
        """检查文件是否已经被替换过（通过检查/*replace*/标记）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.read(100)
                return first_line.startswith('/*replace*/')
        except Exception:
            return False
    
    def check_cursor_file_permission(self):
        """检查是否有Cursor文件的权限"""
        if not self.main_path or not os.path.exists(self.main_path):
            error_msg = '找不到Cursor主文件'
            print(f'❌ {error_msg}')
            return (False, error_msg)
        
        try:
            with open(self.main_path, 'r+') as f:
                pass
            print('✅ Cursor文件权限检查成功')
            return (True, '')
        except PermissionError:
            error_msg = '没有Cursor文件写入权限'
            print(f'❌ Cursor文件权限检查失败: {error_msg}')
            return (False, error_msg)
        except Exception as e:
            error_msg = f'检查Cursor文件权限时发生错误: {str(e)}'
            print(f'❌ {error_msg}')
            return (False, error_msg)
    
    def get_cursor_version(self, formatted=False):
        """获取当前Cursor版本号"""
        return CursorVersionDetector.get_cursor_version(formatted)
    
    def get_backup_path(self):
        """获取main.js备份文件路径"""
        return self.main_path + '.backup' if self.main_path else None
    
    def get_workbench_backup_path(self):
        """获取workbench备份文件路径"""
        return self.workbench_path + '.backup' if self.workbench_path else None

