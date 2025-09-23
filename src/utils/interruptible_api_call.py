# -*- coding: utf-8 -*-
"""
可中断的API调用包装器 - 补全残缺实现
"""

import logging
import threading


class InterruptibleApiCall:
    """可中断的API调用包装器 - 补全"""

    def __init__(self, api_client, stop_event):
        self.api_client = api_client
        self.stop_event = stop_event
        self.result = None
        self.exception = None
        self.logger = logging.getLogger(__name__)

    def get_subscription_info(self, access_token, timeout=10):
        """可中断的订阅信息获取"""
        if self.stop_event.is_set():
            return None

        def api_call():
            """API调用线程函数"""
            try:
                # 🔧 使用传入的api_client进行调用
                self.result = self.api_client.get_subscription_info(access_token, timeout=timeout)
            except Exception as e:
                self.exception = e

        # 🔧 ：使用线程执行API调用
        api_thread = threading.Thread(target=api_call, daemon=True)
        api_thread.start()
        api_thread.join(timeout=timeout + 2)  # 额外2秒容错

        # 检查中断状态
        if self.stop_event.is_set():
            return None

        # 检查线程是否还在运行（超时）
        if api_thread.is_alive():
            self.logger.warning("API调用超时")
            return None

        # 检查是否有异常
        if self.exception:
            raise self.exception

        return self.result
