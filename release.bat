@echo off
REM Windows版本发布脚本
echo 🚀 Cursor Tool Free 版本发布工具 (Windows)
echo ==================================

REM 检查git状态
git status --porcelain > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Git仓库状态检查失败
    pause
    exit /b 1
)

REM 获取当前版本
for /f "tokens=*" %%i in ('git describe --tags --abbrev=0 2^>nul') do set CURRENT_TAG=%%i
if "%CURRENT_TAG%"=="" set CURRENT_TAG=v0.0.0
echo 📋 当前版本: %CURRENT_TAG%

REM 提示输入新版本
set /p NEW_VERSION="📝 请输入新版本号 (格式: v1.0.0): "

REM 简单验证格式
echo %NEW_VERSION% | findstr /r "^v[0-9]*\.[0-9]*\.[0-9]*$" > nul
if %ERRORLEVEL% neq 0 (
    echo ❌ 版本格式错误，请使用 v1.0.0 格式
    pause
    exit /b 1
)

echo 🔧 创建版本标签...
git tag -a "%NEW_VERSION%" -m "Release %NEW_VERSION%"

echo 📤 推送到远程仓库...
git push origin main
git push origin "%NEW_VERSION%"

echo ✅ 版本发布完成！
echo 🔗 GitHub Actions将自动构建跨平台可执行文件
echo 🎉 请访问 GitHub Releases 页面查看构建进度
echo    https://github.com/QSXDY/cursor-tool-free/releases

pause
