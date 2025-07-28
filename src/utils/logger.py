"""
日志系统模块
提供统一的日志管理功能，支持文件输出、控制台输出、日志轮转等
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
import time
import functools
from datetime import datetime
import traceback
import colorama
from colorama import Fore, Back, Style

# 初始化colorama
colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }

    def format(self, record):
        # 为日志级别添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"

        # 为模块名添加颜色
        if hasattr(record, 'name'):
            record.name = f"{Fore.BLUE}{record.name}{Style.RESET_ALL}"

        return super().format(record)


class PerformanceLogger:
    """性能日志记录器"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def time_it(self, func_name: str = None):
        """装饰器：记录函数执行时间"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    duration = end_time - start_time

                    self.logger.info(f"⏱️ {name} 执行完成，耗时: {duration:.3f}s")
                    return result

                except Exception as e:
                    end_time = time.time()
                    duration = end_time - start_time

                    self.logger.error(f"❌ {name} 执行失败，耗时: {duration:.3f}s，错误: {str(e)}")
                    raise

            return wrapper
        return decorator

    def log_memory_usage(self, description: str = ""):
        """记录内存使用情况"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            self.logger.info(f"💾 内存使用 {description}: {memory_mb:.2f} MB")
        except ImportError:
            self.logger.debug("psutil未安装，无法获取内存使用信息")


class TranslationLogger:
    """翻译专用日志记录器"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.translation_stats = {
            'total_segments': 0,
            'translated_segments': 0,
            'failed_segments': 0,
            'total_chars': 0,
            'start_time': None,
            'errors': []
        }

    def start_translation(self, total_segments: int):
        """开始翻译任务"""
        self.translation_stats.update({
            'total_segments': total_segments,
            'translated_segments': 0,
            'failed_segments': 0,
            'total_chars': 0,
            'start_time': time.time(),
            'errors': []
        })

        self.logger.info(f"🚀 开始翻译任务，总计 {total_segments} 个片段")

    def log_segment_translated(self, segment_index: int, char_count: int, provider: str):
        """记录片段翻译完成"""
        self.translation_stats['translated_segments'] += 1
        self.translation_stats['total_chars'] += char_count

        progress = (self.translation_stats['translated_segments'] /
                   self.translation_stats['total_segments'] * 100)

        self.logger.info(
            f"✅ 片段 {segment_index + 1}/{self.translation_stats['total_segments']} "
            f"翻译完成 ({progress:.1f}%) - {provider} - {char_count} 字符"
        )

    def log_segment_failed(self, segment_index: int, error: str):
        """记录片段翻译失败"""
        self.translation_stats['failed_segments'] += 1
        self.translation_stats['errors'].append({
            'segment': segment_index,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })

        self.logger.error(f"❌ 片段 {segment_index + 1} 翻译失败: {error}")

    def finish_translation(self):
        """完成翻译任务"""
        if self.translation_stats['start_time']:
            duration = time.time() - self.translation_stats['start_time']

            success_rate = (self.translation_stats['translated_segments'] /
                          self.translation_stats['total_segments'] * 100)

            self.logger.info(
                f"🎉 翻译任务完成！\n"
                f"   总时间: {duration:.2f}s\n"
                f"   成功率: {success_rate:.1f}% "
                f"({self.translation_stats['translated_segments']}/{self.translation_stats['total_segments']})\n"
                f"   失败数: {self.translation_stats['failed_segments']}\n"
                f"   总字符数: {self.translation_stats['total_chars']}"
            )

            if self.translation_stats['errors']:
                self.logger.warning(f"⚠️ 有 {len(self.translation_stats['errors'])} 个错误需要注意")


class LoggerManager:
    """日志管理器"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.loggers: Dict[str, logging.Logger] = {}
        self.performance_loggers: Dict[str, PerformanceLogger] = {}
        self.translation_loggers: Dict[str, TranslationLogger] = {}

        # 默认配置
        self.default_config = {
            'level': 'INFO',
            'file': 'logs/app.log',
            'max_size': '10MB',
            'backup_count': 5,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'console_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'enable_console': True,
            'enable_file': True,
            'enable_colors': True
        }

        # 合并配置
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value

    def _parse_size(self, size_str: str) -> int:
        """解析文件大小字符串"""
        size_str = size_str.upper().strip()

        # 支持多种格式：10MB, 10M, 10KB, 10K, 10GB, 10G, 10B, 10
        multipliers = {
            'GB': 1024**3, 'G': 1024**3,
            'MB': 1024**2, 'M': 1024**2,
            'KB': 1024, 'K': 1024,
            'B': 1
        }

        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                number_part = size_str[:-len(suffix)].strip()
                try:
                    return int(number_part) * multiplier
                except ValueError:
                    return int(float(number_part)) * multiplier

        # 如果没有单位，默认为字节
        try:
            return int(size_str)
        except ValueError:
            return int(float(size_str))

    def get_logger(self, name: str) -> logging.Logger:
        """获取或创建日志记录器"""
        if name not in self.loggers:
            self._create_logger(name)
        return self.loggers[name]

    def _create_logger(self, name: str):
        """创建日志记录器"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.config['level'].upper()))

        # 避免重复添加处理器
        if logger.handlers:
            return

        # 文件处理器
        if self.config.get('enable_file', True):
            log_file = Path(self.config['file'])
            log_file.parent.mkdir(parents=True, exist_ok=True)

            max_bytes = self._parse_size(self.config['max_size'])
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=self.config['backup_count'],
                encoding='utf-8'
            )

            file_formatter = logging.Formatter(self.config['format'])
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # 控制台处理器
        if self.config.get('enable_console', True):
            console_handler = logging.StreamHandler(sys.stdout)

            if self.config.get('enable_colors', True):
                console_formatter = ColoredFormatter(self.config['console_format'])
            else:
                console_formatter = logging.Formatter(self.config['console_format'])

            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        self.loggers[name] = logger

    def get_performance_logger(self, name: str) -> PerformanceLogger:
        """获取性能日志记录器"""
        if name not in self.performance_loggers:
            logger = self.get_logger(f"{name}.performance")
            self.performance_loggers[name] = PerformanceLogger(logger)
        return self.performance_loggers[name]

    def get_translation_logger(self, name: str) -> TranslationLogger:
        """获取翻译日志记录器"""
        if name not in self.translation_loggers:
            logger = self.get_logger(f"{name}.translation")
            self.translation_loggers[name] = TranslationLogger(logger)
        return self.translation_loggers[name]

    def set_level(self, level: str):
        """设置所有日志记录器的级别"""
        log_level = getattr(logging, level.upper())
        for logger in self.loggers.values():
            logger.setLevel(log_level)

    def log_exception(self, logger_name: str, exception: Exception, context: str = ""):
        """记录异常信息"""
        logger = self.get_logger(logger_name)

        error_msg = f"异常发生 {context}: {str(exception)}"
        logger.error(error_msg)
        logger.debug(f"异常详情:\n{traceback.format_exc()}")

    def create_child_logger(self, parent_name: str, child_name: str) -> logging.Logger:
        """创建子日志记录器"""
        full_name = f"{parent_name}.{child_name}"
        return self.get_logger(full_name)


# 全局日志管理器实例
_logger_manager: Optional[LoggerManager] = None


def init_logger(config: Dict[str, Any] = None) -> LoggerManager:
    """初始化日志系统"""
    global _logger_manager
    _logger_manager = LoggerManager(config)
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    if _logger_manager is None:
        init_logger()
    return _logger_manager.get_logger(name)


def get_performance_logger(name: str) -> PerformanceLogger:
    """获取性能日志记录器"""
    if _logger_manager is None:
        init_logger()
    return _logger_manager.get_performance_logger(name)


def get_translation_logger(name: str) -> TranslationLogger:
    """获取翻译日志记录器"""
    if _logger_manager is None:
        init_logger()
    return _logger_manager.get_translation_logger(name)


def log_function_call(logger_name: str = None):
    """装饰器：记录函数调用"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = logger_name or func.__module__
            logger = get_logger(name)

            func_name = f"{func.__module__}.{func.__name__}"
            logger.debug(f"🔄 调用函数: {func_name}")

            try:
                result = func(*args, **kwargs)
                logger.debug(f"✅ 函数执行成功: {func_name}")
                return result
            except Exception as e:
                logger.error(f"❌ 函数执行失败: {func_name} - {str(e)}")
                raise

        return wrapper
    return decorator


def setup_logging_from_config(config_dict: Dict[str, Any]):
    """从配置字典设置日志系统"""
    logging_config = config_dict.get('logging', {})
    init_logger(logging_config)


# 便捷函数
def debug(message: str, logger_name: str = 'main'):
    """记录调试信息"""
    get_logger(logger_name).debug(message)


def info(message: str, logger_name: str = 'main'):
    """记录信息"""
    get_logger(logger_name).info(message)


def warning(message: str, logger_name: str = 'main'):
    """记录警告"""
    get_logger(logger_name).warning(message)


def error(message: str, logger_name: str = 'main'):
    """记录错误"""
    get_logger(logger_name).error(message)


def critical(message: str, logger_name: str = 'main'):
    """记录严重错误"""
    get_logger(logger_name).critical(message)
