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

### 👥 普通用户

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装浏览器依赖（可选，用于Cookie导入）
pip install -r requirements_browser.txt

# 运行程序
python main.py
```

### 👨‍💻 开发者（二次开发）

```bash
# 安装所有依赖（包括开发工具）
pip install -r requirements.txt
pip install -r requirements_browser.txt
pip install -r requirements-dev.txt

# 代码格式化（推荐在提交前运行）
black . --line-length 120
isort . --profile black

# 代码质量检查
flake8 . --max-line-length=120

# 运行测试
pytest

# 构建可执行文件
pyinstaller --onefile --windowed main.py
```

## ✨ 功能特点

- 🔐 专业的Cursor账号管理系统
- 📱 PyQt6现代化用户界面  
- 💾 本地化数据存储
- 🔄 异步操作和状态管理
- 🛡️ 账号安全与隐私保护
- 🌐 浏览器Cookie导入支持
- 📊 使用额度实时监控
- 🌍 **完整跨平台支持** (Windows/macOS/Linux)

## 📋 主要功能

- **账号管理**: 添加、删除、编辑Cursor账号信息
- **Cookie导入**: 从浏览器导入账号Cookie
- **状态监控**: 实时显示账号状态和使用情况
- **配置管理**: 灵活的应用配置和设置
- **数据安全**: 本地存储，保护用户隐私
- **跨平台兼容**: 智能检测各平台Cursor安装和浏览器

## 🌍 跨平台支持详情

### Windows
- **Cursor检测**: 自动检测标准安装位置
- **浏览器支持**: Chrome、Edge、Firefox
- **安装方式**: 标准installer、便携版

### macOS  
- **Cursor检测**: 标准安装、Homebrew、用户目录
- **浏览器支持**: Chrome、Safari、Edge、Firefox、Chromium
- **安装方式**: .app包、Homebrew Cask

### Linux
- **Cursor检测**: 系统安装、AppImage、Snap、Flatpak
- **浏览器支持**: Chrome、Chromium、Firefox、系统默认
- **安装方式**: APT/YUM/Pacman、Snap、Flatpak、AppImage

## 🔧 系统要求

- Python 3.10.11+
- PyQt6
- 支持的操作系统: Windows, macOS, Linux

## 👨‍💻 开发指南

### 📦 依赖管理策略

项目采用分层依赖管理：

- **requirements.txt** - 核心运行依赖（普通用户必需）
- **requirements_browser.txt** - 浏览器功能依赖（可选）
- **requirements-dev.txt** - 开发工具依赖（仅开发者需要）

### 🛠️ 开发工具链

本项目使用专业的代码质量工具：

```bash
# 代码格式化
black . --line-length 120        # 统一代码风格
isort . --profile black          # 整理导入语句

# 代码质量检查
flake8 . --max-line-length=120   # 静态代码分析
autoflake --remove-all-unused-imports --recursive .  # 清理未使用导入

# 测试运行
pytest                           # 单元测试
python main.py                   # 功能测试
```

### 🎯 贡献指南

1. **Fork 项目** 
2. **安装开发依赖**: `pip install -r requirements-dev.txt`
3. **代码修改后运行格式化**: `black . && isort .`
4. **质量检查**: `flake8 .`
5. **提交代码**
6. **创建 Pull Request**

我们维护**严格的代码质量标准**，所有PR都会通过自动化检查！
