#!/bin/bash
# Ubuntu/Debian DEB包构建脚本

set -e

echo "🐧 开始构建Ubuntu/Debian DEB包..."

# 检查操作系统
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ 此脚本只能在Linux上运行"
    exit 1
fi

# 检查必需工具
if ! command -v dpkg-deb &> /dev/null; then
    echo "❌ 未找到dpkg-deb工具"
    echo "💡 请安装: sudo apt-get install dpkg-dev"
    exit 1
fi

# 获取版本号（从git标签或默认值）
VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || echo "1.0.6")
echo "📋 版本号: ${VERSION}"

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf build dist cursortool-free_*.deb

# 使用PyInstaller构建可执行文件
echo "📦 构建可执行文件..."
pyinstaller CursorToolFree.spec --clean --noconfirm

# 检查构建是否成功
if [ ! -f "dist/CursorToolFree" ]; then
    echo "❌ 构建失败：未找到可执行文件"
    exit 1
fi

echo "✅ 可执行文件构建完成"

# 创建DEB包目录结构
DEB_DIR="cursortool-free_${VERSION}_amd64"
echo "📁 创建DEB包目录结构: ${DEB_DIR}"

mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/opt/cursortool-free"
mkdir -p "${DEB_DIR}/usr/share/applications"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/512x512/apps"
mkdir -p "${DEB_DIR}/usr/bin"

# 复制可执行文件和资源
echo "📋 复制文件..."
cp dist/CursorToolFree "${DEB_DIR}/opt/cursortool-free/"
cp -r resources "${DEB_DIR}/opt/cursortool-free/"
cp icon.png "${DEB_DIR}/usr/share/icons/hicolor/512x512/apps/cursortool-free.png"

# 创建启动脚本
echo "📝 创建启动脚本..."
cat > "${DEB_DIR}/usr/bin/cursortool-free" << 'LAUNCHER_EOF'
#!/bin/bash
cd /opt/cursortool-free
exec ./CursorToolFree "$@"
LAUNCHER_EOF
chmod +x "${DEB_DIR}/usr/bin/cursortool-free"

# 创建.desktop文件
echo "🖥️ 创建desktop文件..."
cat > "${DEB_DIR}/usr/share/applications/cursortool-free.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Type=Application
Name=Cursor Tool Free
Comment=Cursor账号管理工具 - 免费精简版
Exec=/usr/bin/cursortool-free
Icon=cursortool-free
Categories=Development;Utility;
Terminal=false
StartupWMClass=CursorToolFree
Keywords=cursor;account;manager;开发;账号;管理;
GenericName=Cursor Account Manager
DESKTOP_EOF

# 创建control文件
echo "⚙️ 创建control文件..."
cat > "${DEB_DIR}/DEBIAN/control" << CONTROL_EOF
Package: cursortool-free
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Depends: libqt6core6, libqt6gui6, libqt6widgets6
Maintainer: Cursor Tool Free Team <support@example.com>
Description: Cursor账号管理工具 - 免费精简版
 专业的Cursor账号管理系统，提供现代化用户界面、
 本地化数据存储、浏览器Cookie导入支持等功能。
 .
 主要功能：
  - 账号管理：添加、删除、编辑Cursor账号信息
  - Cookie导入：从浏览器导入账号Cookie
  - 状态监控：实时显示账号状态和使用情况
  - 数据安全：本地存储，保护用户隐私
Homepage: https://github.com/QSXDY/cursor-tool-free
CONTROL_EOF

# 创建postinst脚本（安装后执行）
echo "📝 创建postinst脚本..."
cat > "${DEB_DIR}/DEBIAN/postinst" << 'POSTINST_EOF'
#!/bin/bash
set -e

# 更新桌面数据库
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q
fi

# 更新图标缓存
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

echo "✅ Cursor Tool Free安装完成！"
echo ""
echo "🚀 启动方法："
echo "   命令行: cursortool-free"
echo "   或从应用程序菜单启动"

exit 0
POSTINST_EOF
chmod +x "${DEB_DIR}/DEBIAN/postinst"

# 创建prerm脚本（卸载前执行）
echo "📝 创建prerm脚本..."
cat > "${DEB_DIR}/DEBIAN/prerm" << 'PRERM_EOF'
#!/bin/bash
set -e
exit 0
PRERM_EOF
chmod +x "${DEB_DIR}/DEBIAN/prerm"

# 构建DEB包
echo "🔨 构建DEB包..."
dpkg-deb --build "${DEB_DIR}"
mv "${DEB_DIR}.deb" "CursorToolFree-Ubuntu.deb"

# 显示包信息
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 DEB包构建成功！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 包信息："
dpkg-deb --info "CursorToolFree-Ubuntu.deb"
echo ""
echo "📁 文件大小："
ls -lh "CursorToolFree-Ubuntu.deb"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 安装方法："
echo "   sudo dpkg -i CursorToolFree-Ubuntu.deb"
echo "   sudo apt-get install -f  # 如果有依赖问题"
echo ""
echo "💡 测试方法："
echo "   cursortool-free"
echo ""
echo "💡 卸载方法："
echo "   sudo apt remove cursortool-free"
echo ""

# 清理临时文件
rm -rf "${DEB_DIR}"

echo "🎉 构建完成！"

