#!/bin/bash
# macOS构建和签名脚本
# 适用于ad-hoc签名（无需Apple开发者账号）

set -e

echo "🍎 开始macOS应用构建和签名..."

# 检查操作系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此脚本只能在macOS上运行"
    exit 1
fi

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf build dist

# 使用PyInstaller构建.app
echo "📦 构建.app应用包..."
pyinstaller CursorToolFree.spec

# 检查构建是否成功
if [ ! -d "dist/CursorToolFree.app" ]; then
    echo "❌ 构建失败：未找到.app文件"
    exit 1
fi

echo "✅ 应用包构建完成"

# Ad-hoc签名（无需开发者证书）
echo "🔏 执行ad-hoc签名..."
codesign --force --deep --sign - "dist/CursorToolFree.app"

# 验证签名
echo "🔍 验证签名..."
codesign --verify --deep --strict --verbose=2 "dist/CursorToolFree.app"

if [ $? -eq 0 ]; then
    echo "✅ 签名验证通过"
else
    echo "⚠️  签名验证失败，但应用仍可使用"
fi

# 创建DMG（可选，更专业的分发方式）
echo "📀 创建DMG安装包..."

# 检查是否安装了create-dmg工具
if ! command -v create-dmg &> /dev/null; then
    echo "⚠️  未安装create-dmg工具，跳过DMG创建"
    echo "💡 提示：可以通过 'brew install create-dmg' 安装"
else
    # 使用create-dmg创建安装包
    rm -f "dist/CursorToolFree-macOS.dmg"
    create-dmg \
        --volname "Cursor Tool Free" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "CursorToolFree.app" 175 190 \
        --hide-extension "CursorToolFree.app" \
        --app-drop-link 425 185 \
        "dist/CursorToolFree-macOS.dmg" \
        "dist/CursorToolFree.app"
    
    if [ $? -eq 0 ]; then
        echo "✅ DMG创建成功: dist/CursorToolFree-macOS.dmg"
    fi
fi

# 如果没有create-dmg，创建简单的zip包
if [ ! -f "dist/CursorToolFree-macOS.dmg" ]; then
    echo "📦 创建ZIP压缩包..."
    cd dist
    zip -r "CursorToolFree-macOS.zip" "CursorToolFree.app"
    cd ..
    echo "✅ ZIP创建成功: dist/CursorToolFree-macOS.zip"
fi

# 显示文件信息
echo ""
echo "📊 构建结果："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "dist/CursorToolFree-macOS.dmg" ]; then
    ls -lh "dist/CursorToolFree-macOS.dmg"
fi
if [ -f "dist/CursorToolFree-macOS.zip" ]; then
    ls -lh "dist/CursorToolFree-macOS.zip"
fi
ls -lh "dist/CursorToolFree.app"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "🎉 构建完成！"
echo ""
echo "📝 用户使用说明："
echo "  1. 下载后双击打开.dmg（或解压.zip）"
echo "  2. 首次打开时，右键点击应用 → 选择'打开' → 点击'打开'按钮"
echo "  3. 之后可以正常双击使用"
echo ""
echo "💡 如果遇到'无法打开'的提示："
echo "   方法1（推荐）：右键 → 打开 → 确认"
echo "   方法2：系统偏好设置 → 安全性与隐私 → 点击'仍要打开'"
echo ""

