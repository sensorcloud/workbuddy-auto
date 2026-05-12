"""
日志配置模块
设置应用日志记录
"""
import logging
import sys

def setup_logging():
    """
    配置日志
    设置日志格式和级别
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
