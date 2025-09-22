# -*- coding: utf-8 -*-
"""
跨平台工具模块 - 处理不同操作系统的兼容性
"""

import sys


def get_platform_headers():
    """获取当前平台的请求头信息"""
    if sys.platform == "win32":
        return {
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"10.0.0"',
        }
    elif sys.platform == "darwin":
        return {
            "sec-ch-ua-platform": '"macOS"',
            "sec-ch-ua-platform-version": '"13.0.0"',
        }
    else:  # Linux
        return {
            "sec-ch-ua-platform": '"Linux"',
            "sec-ch-ua-platform-version": '""',
        }


def get_user_agent():
    """获取当前平台的User-Agent"""
    if sys.platform == "win32":
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
        )
    elif sys.platform == "darwin":
        return (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        )
    else:  # Linux
        return (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 " "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        )


def get_platform_name():
    """获取平台名称"""
    if sys.platform == "win32":
        return "Windows"
    elif sys.platform == "darwin":
        return "macOS"
    else:
        return "Linux"
