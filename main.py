#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cursor Tool Free - 免费精简版Cursor账号管理工具
专业的本地化账号管理解决方案
"""

import atexit
import os
import signal
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# PyQt6导入必须在路径设置后
from PyQt6.QtCore import QTimer  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

# 全局变量用于清理
main_window = None
app = None


def cleanup():
    """清理资源"""
    global main_window, app
    # main_window和app在main()函数中赋值
    if main_window is not None:
        print("🔧 清理线程资源...")
        try:
            # 清理刷新线程
            if hasattr(main_window, "refresh_threads"):
                for thread in main_window.refresh_threads.values():
                    if thread and thread.isRunning():
                        thread.stop()
                        thread.wait(1000)

            # 清理使用额度更新线程
            if hasattr(main_window, "_current_update_thread") and main_window._current_update_thread:
                if main_window._current_update_thread.isRunning():
                    main_window._current_update_thread.quit()
                    main_window._current_update_thread.wait(1000)

            print("✅ 资源清理完成")
        except Exception as e:
            print(f"⚠️ 清理资源时出错: {e}")


def signal_handler(sig, frame):
    """信号处理器 - 处理Ctrl+C"""
    print("\n🛑 接收到中断信号，正在安全退出...")
    cleanup()
    sys.exit(0)


def main():
    """主函数 - 程序入口"""
    global main_window, app

    try:
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        atexit.register(cleanup)

        # 导入模块化组件
        from src.config import Config
        from src.ui.main_window import CursorAccountManagerPro

        # 创建应用程序
        app = QApplication(sys.argv)

        # 设置应用程序属性
        app.setApplicationName("Cursor Tool Free")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Cursor Tool Free Team")

        # 启用Ctrl+C处理
        timer = QTimer()
        timer.start(500)
        timer.timeout.connect(lambda: None)

        # 初始化配置
        config = Config.get_instance()
        print(f"✅ 配置初始化完成: {config.config_dir}")

        # 创建主窗口
        main_window = CursorAccountManagerPro()
        main_window.show()

        print("🚀 Cursor Tool Free 启动成功")

        # 🔧 在启动时执行版本检测并缓存结果
        print("🔍 执行启动时版本检测...")
        from src.utils.version_manager import SmartAPIManager

        global_api_manager = SmartAPIManager()
        patch_rules = global_api_manager.get_patch_rules(timeout=10)

        # 🔧 将规则缓存到全局配置，供后续使用
        from src.config import Config

        config = Config.get_instance()
        if not hasattr(config, "_global_patch_rules"):
            config._global_patch_rules = patch_rules
            print(f"✅ 版本检测完成，缓存了 {len(patch_rules) if patch_rules else 0} 条规则")

        # 运行应用程序
        sys.exit(app.exec())

    except KeyboardInterrupt:
        print("\n🛑 启动时用户中断")
        cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback

        traceback.print_exc()
        cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
