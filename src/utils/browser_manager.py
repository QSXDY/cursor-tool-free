# -*- coding: utf-8 -*-
"""
浏览器管理器 - 无痕浏览器自动化实现
支持Chrome/Edge的无痕模式，自动Cookie设置和Dashboard登录
当DrissionPage不可用时，降级使用系统默认浏览器
"""

import logging
import os
import subprocess
import sys
import webbrowser

# 检查是否有DrissionPage
try:
    from DrissionPage import ChromiumOptions, ChromiumPage

    DRISSIONPAGE_AVAILABLE = True
except ImportError:
    DRISSIONPAGE_AVAILABLE = False


class BrowserManager:
    """浏览器管理器 - 完全无痕浏览器自动化"""

    def __init__(self, config=None, incognito_mode=True):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.browser = None
        self.incognito_mode = incognito_mode

        if not DRISSIONPAGE_AVAILABLE:
            self.logger.warning("DrissionPage未安装，将降级使用系统默认浏览器打开")

    def get_new_page(self, use_stealth: bool = True):
        """
        获取一个无痕浏览器页面

        Args:
            use_stealth: 是否使用stealth模式

        Returns:
            ChromiumPage: 浏览器页面对象，如果失败则返回None
        """
        if not DRISSIONPAGE_AVAILABLE:
            return None

        try:
            if not self.browser:
                self.logger.info("🔧 正在启动无痕浏览器...")

                # 🔧 创建无痕浏览器配置 -
                co = ChromiumOptions()

                # 🔧 平台特定配置
                if sys.platform == "win32":
                    self._configure_windows_browser(co)
                elif sys.platform == "darwin":
                    self._configure_macos_browser(co)
                else:  # Linux
                    self._configure_linux_browser(co)

                co.auto_port()

                # 🔧 设置浏览器路径
                browser_path = self._find_browser_path()
                if browser_path:
                    co.set_browser_path(browser_path)
                    self.logger.info(f"使用浏览器: {browser_path}")

                # 🔧 启动浏览器
                self.browser = ChromiumPage(co)
                self.logger.info("🚀 无痕浏览器启动成功")

            # 🔧 获取标签页 -
            return self.browser.get_tab(1)

        except Exception as e:
            self.logger.error(f"❌ 启动浏览器失败: {e}")
            # 在 Linux 下如果 DrissionPage 启动失败，清理可能的僵尸进程
            if sys.platform == "linux":
                try:
                    import subprocess

                    # 清理可能的 Chrome 僵尸进程
                    subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
                    subprocess.run(["pkill", "-f", "chromium"], capture_output=True)
                except Exception:
                    pass
            return None

    def _configure_windows_browser(self, co):
        """Windows 浏览器配置 - 保持原有稳定逻辑"""
        # 无痕模式设置
        if self.incognito_mode:
            browser_path = self._find_browser_path()
            if browser_path and "msedge.exe" in browser_path.lower():
                co.set_argument("--inprivate")
                self.logger.info("✅ 使用Edge无痕模式 (--inprivate)")
            else:
                co.set_argument("--incognito")
                self.logger.info("✅ 使用Chrome无痕模式 (--incognito)")

        # 基础设置
        co.set_argument("--exclude-switches=enable-automation")
        co.set_argument("--no-first-run")
        co.set_argument("--no-default-browser-check")
        co.set_argument("--disable-background-networking")
        co.set_argument("--disable-component-update")
        co.set_argument("--disable-default-apps")
        co.set_argument("--disable-component-extensions-with-background-pages")

        # 窗口设置
        co.set_argument("--start-maximized")
        co.headless(False)

    def _configure_macos_browser(self, co):
        """macOS 浏览器配置 - 保持原有稳定逻辑"""
        # 无痕模式设置
        if self.incognito_mode:
            co.set_argument("--incognito")
            self.logger.info("✅ 使用Chrome无痕模式 (--incognito)")

        # 基础设置
        co.set_argument("--exclude-switches=enable-automation")
        co.set_argument("--no-first-run")
        co.set_argument("--no-default-browser-check")
        co.set_argument("--disable-background-networking")
        co.set_argument("--disable-component-update")
        co.set_argument("--disable-default-apps")
        co.set_argument("--disable-component-extensions-with-background-pages")

        # 窗口设置
        co.set_argument("--start-maximized")
        co.headless(False)

    def _configure_linux_browser(self, co):
        """Linux 浏览器配置 - 基础配置"""
        # 无痕模式设置
        if self.incognito_mode:
            co.set_argument("--incognito")
            self.logger.info("✅ 使用Chrome无痕模式 (--incognito)")

        # 基础设置
        co.set_argument("--exclude-switches=enable-automation")
        co.set_argument("--no-first-run")
        co.set_argument("--no-default-browser-check")
        co.set_argument("--disable-background-networking")
        co.set_argument("--disable-component-update")
        co.set_argument("--disable-default-apps")
        co.set_argument("--disable-component-extensions-with-background-pages")

        # Linux 必需参数 - 新版兼容方式
        co.set_argument("--disable-dev-shm-usage")  # 防止内存问题
        co.set_argument("--disable-gpu")  # 避免GPU相关问题
        co.set_argument("--remote-debugging-port=0")  # 自动分配调试端口

        # 窗口设置
        co.set_argument("--start-maximized")
        co.headless(False)

    def _find_browser_path(self):
        """查找可用的浏览器路径 - 完整跨平台版本"""

        if sys.platform == "win32":
            # Windows平台 - Chrome优先，然后Edge
            browser_paths = [
                # Chrome路径
                os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                # Edge路径
                os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe"),
                # Firefox路径
                os.path.expandvars(r"%PROGRAMFILES%\Mozilla Firefox\firefox.exe"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%\Mozilla Firefox\firefox.exe"),
            ]

        elif sys.platform == "darwin":
            # macOS平台 - Chrome优先，然后Safari/Edge/Firefox
            browser_paths = [
                # Chrome
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                # Safari（系统自带）
                "/Applications/Safari.app/Contents/MacOS/Safari",
                # Edge
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                # Firefox
                "/Applications/Firefox.app/Contents/MacOS/firefox",
                # Chromium
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                # 用户安装位置
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            ]

        else:
            # Linux平台 - Chrome/Chromium优先，然后Firefox
            browser_paths = [
                # Chrome
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/google-chrome-beta",
                "/usr/bin/google-chrome-unstable",
                # Chromium
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                # Snap包
                "/snap/bin/chromium",
                "/snap/bin/firefox",
                "/snap/bin/code",  # VS Code内置浏览器
                # Flatpak
                "/var/lib/flatpak/exports/bin/org.chromium.Chromium",
                "/var/lib/flatpak/exports/bin/org.mozilla.firefox",
                # Firefox
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr",
                # 用户本地安装
                os.path.expanduser("~/.local/bin/chrome"),
                os.path.expanduser("~/.local/bin/chromium"),
                os.path.expanduser("~/.local/bin/firefox"),
            ]

        # 查找第一个存在的浏览器
        for path in browser_paths:
            if os.path.exists(path):
                self.logger.info(f"🔍 找到浏览器: {path}")
                return path

        # 都找不到，返回None让DrissionPage使用系统默认
        self.logger.warning("⚠️ 未找到指定浏览器，将使用系统默认浏览器")
        return None

    def set_auth_cookie(self, page, user_id: str, access_token: str):
        """
        设置认证Cookie

        Args:
            page: 浏览器页面对象
            user_id: 用户ID
            access_token: 访问令牌

        Returns:
            bool: 是否设置成功
        """
        if not page:
            return False

        try:
            # 🔧 构建Cookie值 - 格式
            cookie_value = f"{user_id}%3A%3A{access_token}"

            # 🔧 ：先访问首页建立域名上下文
            page.get("https://cursor.com")

            # 🔧 ：设置认证Cookie
            cookie_dict = {"WorkosCursorSessionToken": cookie_value, "NEXT_LOCALE": "zh"}

            print(f"🍪 设置Cookie: WorkosCursorSessionToken={cookie_value[:50]}...")

            # 🔧 使用验证有效的Cookie设置方法
            page.set.cookies(cookie_dict)  # 方法1：直接传递字典，已验证有效

            print("✅ 认证Cookie设置完成")

            return True

        except Exception as e:
            self.logger.error(f"❌ 设置Cookie失败: {e}")
            return False

    def open_dashboard(self, user_id: str, access_token: str):
        """
        打开Dashboard并自动登录
        完全静默，无弹窗，一步到位

        Args:
            user_id: 用户ID
            access_token: 访问令牌

        Returns:
            bool: 是否成功
        """
        try:
            # 🔧 1. 获取无痕浏览器页面
            page = self.get_new_page()
            if not page:
                # DrissionPage 不可用，使用系统默认浏览器降级
                dashboard_url = "https://cursor.com/dashboard"
                self.logger.info("🔄 DrissionPage 不可用，使用系统默认浏览器打开 Dashboard")
                return self.open_url_with_system_browser(dashboard_url)

            # 🔧 2. 设置认证Cookie - 流程
            success = self.set_auth_cookie(page, user_id, access_token)
            if not success:
                return False

            # 🔧 3. 设置完Cookie后访问Dashboard -
            dashboard_url = "https://cursor.com/dashboard"
            print(f"🌐 访问Dashboard: {dashboard_url}")
            page.get(dashboard_url)

            # 🔧 等待页面加载并验证登录状态
            import time

            time.sleep(3)  # 等待3秒确保页面正确加载

            current_url = page.url
            title = page.title
            print(f"📍 最终URL: {current_url}")
            print(f"📄 页面标题: {title}")

            if "authenticator" in current_url:
                print("⚠️ 重定向到登录页，但浏览器已打开供手动登录")
            else:
                print("✅ 成功停留在Dashboard页面，登录成功")

            # 🔧 4. ：browser = None（清理引用）
            self.browser = None

            self.logger.info("🎉 Dashboard已打开，账号应已自动登录")
            return True

        except Exception as e:
            self.logger.error(f"❌ 打开Dashboard失败: {e}")
            return False

    def open_url_with_system_browser(self, url: str):
        """
        使用系统默认浏览器打开URL（降级方案）

        Args:
            url: 要打开的URL

        Returns:
            bool: 是否成功打开
        """
        try:
            if sys.platform == "linux":
                # Linux: 优先使用 xdg-open（更可靠）
                try:
                    subprocess.run(["xdg-open", url], check=True, capture_output=True)
                    self.logger.info(f"✅ 使用 xdg-open 打开: {url}")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # xdg-open 失败，降级到 webbrowser
                    pass

            # 跨平台降级：使用 Python 的 webbrowser 模块
            webbrowser.open(url)
            self.logger.info(f"✅ 使用系统默认浏览器打开: {url}")
            return True

        except Exception as e:
            self.logger.error(f"❌ 打开浏览器失败: {e}")
            return False

    def close(self):
        """安全地关闭浏览器 -"""
        if self.browser:
            try:
                self.logger.info("🔒 正在关闭无痕浏览器...")
                self.browser.quit()
                self.browser = None
                self.logger.info("✅ 浏览器已安全关闭")
            except Exception as e:
                self.logger.error(f"关闭浏览器时出错: {e}")
                # 🔧 强制关闭
                try:
                    self.browser.quit(force=True)
                    self.browser = None
                    self.logger.info("✅ 浏览器已强制关闭")
                except Exception:
                    pass
