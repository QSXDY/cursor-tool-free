# Cursor Tool Free - 账号管理工具

## 📁 项目结构

```
cursor_tool_free/
├── main.py                      # 主程序入口  
├── requirements.txt             # Python依赖
├── requirements_browser.txt     # 浏览器依赖
├── README.md                   # 项目说明
└── src/                        # 核心源码
    ├── config.py               # 配置管理
    ├── constants.py            # 常量定义
    ├── ui/                     # 用户界面
    │   ├── main_window.py      # 主窗口
    │   ├── accounts_widget.py  # 账号管理
    │   └── import_dialog.py    # 导入对话框
    └── utils/                  # 工具模块
        ├── cursor_manager.py   # Cursor管理
        ├── token_manager.py    # 令牌管理
        ├── browser_manager.py  # 浏览器管理
        └── ... (其他工具)
```

## 🚀 快速开始

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装浏览器依赖（可选）
pip install -r requirements_browser.txt

# 运行程序
python main.py
```

## ✨ 功能特点

- 🔐 专业的Cursor账号管理系统
- 📱 PyQt6现代化用户界面
- 💾 本地化数据存储
- 🔄 异步操作和状态管理
- 🛡️ 账号安全与隐私保护
- 🌐 浏览器Cookie导入支持
- 📊 使用额度实时监控

## 📋 主要功能

- **账号管理**: 添加、删除、编辑Cursor账号信息
- **Cookie导入**: 从浏览器导入账号Cookie
- **状态监控**: 实时显示账号状态和使用情况
- **配置管理**: 灵活的应用配置和设置
- **数据安全**: 本地存储，保护用户隐私

## 🔧 系统要求

- Python 3.10.11
- PyQt6
- 支持的操作系统: Windows, macOS, Linux
