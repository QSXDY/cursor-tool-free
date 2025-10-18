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
# Windows/Linux
pyinstaller CursorToolFree.spec

# macOS（包含自动签名）
chmod +x build_macos.sh
./build_macos.sh
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
- **代码签名**: Ad-hoc自签名，首次打开需右键确认

### Linux
- **Cursor检测**: 系统安装、AppImage、Snap、Flatpak
- **浏览器支持**: Chrome、Chromium、Firefox、系统默认
- **安装方式**: 
  - **DEB包**（推荐Ubuntu/Debian用户）
  - **AppImage**（通用，支持所有发行版）
  - **源码安装**

## 🔧 系统要求

- Python 3.10.11+
- PyQt6
- 支持的操作系统: Windows, macOS, Linux

## 🍎 macOS特别说明

### 首次打开应用

由于应用使用ad-hoc签名（无Apple开发者证书），首次打开时需要：

**方法1（推荐）**：
1. 右键点击应用图标
2. 选择"打开"
3. 在弹出的对话框中点击"打开"按钮
4. 之后可以正常双击使用

**方法2**：
1. 尝试双击打开（会提示无法打开）
2. 打开"系统偏好设置" → "安全性与隐私"
3. 在"通用"选项卡中点击"仍要打开"

**方法3（命令行）**：
```bash
# 移除隔离属性
xattr -d com.apple.quarantine /Applications/CursorToolFree.app
```

### 开发者构建说明

在macOS上构建应用：

```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 2. 运行构建脚本（自动签名）
chmod +x build_macos.sh
./build_macos.sh

# 3. 构建产物
# - dist/CursorToolFree.app （应用包）
# - dist/CursorToolFree-macOS.dmg （DMG安装包，需要create-dmg）
# - dist/CursorToolFree-macOS.zip （ZIP压缩包）
```

**可选工具**：
```bash
# 安装create-dmg用于创建DMG安装包
brew install create-dmg
```

## 🐧 Ubuntu/Debian安装说明

### 使用DEB包安装（推荐）

从GitHub Releases下载 `CursorToolFree-Ubuntu.deb`，然后：

```bash
# 方法1：使用dpkg安装
sudo dpkg -i CursorToolFree-Ubuntu.deb

# 如果有依赖问题，自动安装依赖
sudo apt-get install -f

# 方法2：使用apt安装（自动处理依赖）
sudo apt install ./CursorToolFree-Ubuntu.deb
```

### 启动应用

```bash
# 命令行启动
cursortool-free

# 或从应用程序菜单启动
# 应用会出现在 "开发" 或 "工具" 分类中
```

### 卸载

```bash
sudo apt remove cursortool-free
# 或
sudo dpkg -r cursortool-free
```

### 系统要求

- Ubuntu 20.04+ / Debian 11+
- 自动安装依赖：libqt6core6, libqt6gui6, libqt6widgets6

### 使用AppImage（通用方法）

如果不想安装到系统，可以使用AppImage：

```bash
# 下载后添加执行权限
chmod +x CursorToolFree-Linux.AppImage

# 运行
./CursorToolFree-Linux.AppImage
```

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

## 🚀 自动化发布系统

### 📦 版本发布流程

我们使用**Git标签触发的自动化发布**系统：

#### 发布新版本：
```bash
# Windows用户
release.bat

# Linux/macOS用户  
chmod +x release.sh
./release.sh
```

#### 自动化构建：
当你推送版本标签（如`v1.0.1`）时，GitHub Actions会自动：

1. **🪟 Windows**: 构建 `CursorToolFree-Windows.exe`
2. **🍎 macOS**: 构建 `CursorToolFree-macOS.dmg`  
3. **🐧 Linux**: 构建 `CursorToolFree-Linux.AppImage`
4. **📋 创建GitHub Release**: 自动发布到Releases页面

#### 手动发布（高级）：
```bash
# 1. 提交所有更改
git add .
git commit -m "Prepare for v1.0.1"

# 2. 创建版本标签
git tag -a v1.0.1 -m "Release v1.0.1"

# 3. 推送标签（触发自动构建）
git push origin main
git push origin v1.0.1

# 4. GitHub Actions自动构建并发布
```

### 📁 发布产物

每次发布会自动生成：
- **Windows**: 单文件exe，包含所有依赖
- **macOS**: 标准dmg安装包，支持拖拽安装
- **Linux AppImage**: 便携应用，支持所有发行版
- **Linux DEB**: Ubuntu/Debian专用安装包

### 🔧 版本管理

- 版本号格式：`v主版本.次版本.修订版本` (如: v1.0.0)
- 自动更新代码中的版本信息
- 自动生成Release Notes
- 保留完整的版本历史
