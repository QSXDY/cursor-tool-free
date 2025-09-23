#!/bin/bash
# 版本发布脚本 - 自动化版本标记和发布

set -e

echo "🚀 Cursor Tool Free 版本发布工具"
echo "=================================="

# 检查是否有未提交的更改
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ 检测到未提交的更改，请先提交所有更改"
    git status --short
    exit 1
fi

# 获取当前版本
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "📋 当前版本: $CURRENT_TAG"

# 提示输入新版本
echo "📝 请输入新版本号 (格式: v1.0.0):"
read -r NEW_VERSION

# 验证版本格式
if [[ ! $NEW_VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ 版本格式错误，请使用 v1.0.0 格式"
    exit 1
fi

# 检查版本是否已存在
if git tag -l | grep -q "^$NEW_VERSION$"; then
    echo "❌ 版本 $NEW_VERSION 已存在"
    exit 1
fi

# 更新版本信息
echo "🔧 更新版本信息到代码中..."

# 更新main.py中的版本
sed -i.bak "s/setApplicationVersion(".*")/setApplicationVersion("${NEW_VERSION#v}")/" main.py

# 更新__init__.py中的版本  
sed -i.bak "s/__version__ = ".*"/__version__ = "${NEW_VERSION#v}"/" src/__init__.py

# 提交版本更新
git add main.py src/__init__.py
git commit -m "Bump version to $NEW_VERSION"

# 创建并推送标签
echo "🏷️ 创建版本标签: $NEW_VERSION"
git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION"

echo "📤 推送到远程仓库..."
git push origin main
git push origin "$NEW_VERSION"

echo "✅ 版本发布完成！"
echo "🔗 GitHub Actions将自动构建以下文件:"
echo "   • CursorToolFree-Windows.exe"  
echo "   • CursorToolFree-macOS-Universal.dmg"
echo "   • CursorToolFree-Linux"
echo ""
echo "🎉 请访问 GitHub Releases 页面查看构建进度"
echo "   https://github.com/QSXDY/cursor-tool-free/releases"
