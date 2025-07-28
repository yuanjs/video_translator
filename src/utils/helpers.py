"""
辅助函数模块
提供通用的工具函数，支持文件处理、格式转换、验证等功能
"""

import os
import re
import hashlib
import mimetypes
import subprocess
import tempfile
import shutil
import time
import functools
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
import unicodedata
import json
import threading
import queue
import platform
import psutil
from urllib.parse import urlparse
import chardet


def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    try:
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_free': psutil.disk_usage('/').free if platform.system() != 'Windows' else psutil.disk_usage('C:').free
        }
    except Exception:
        return {'platform': platform.system(), 'python_version': platform.python_version()}


def is_video_file(file_path: Union[str, Path]) -> bool:
    """检查文件是否为视频文件"""
    video_extensions = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
        '.m4v', '.3gp', '.f4v', '.asf', '.rm', '.rmvb', '.vob',
        '.ogv', '.drc', '.gif', '.gifv', '.mng', '.avi', '.mov',
        '.qt', '.wmv', '.yuv', '.rm', '.rmvb', '.asf', '.amv',
        '.mp4', '.m4p', '.m4v', '.mpg', '.mp2', '.mpeg', '.mpe',
        '.mpv', '.mpg', '.mpeg', '.m2v', '.m4v', '.svi', '.3gp',
        '.3g2', '.mxf', '.roq', '.nsv'
    }

    file_path = Path(file_path)
    if not file_path.exists():
        return False

    # 检查扩展名
    if file_path.suffix.lower() not in video_extensions:
        return False

    # 检查MIME类型
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith('video/'):
        return True

    return file_path.suffix.lower() in video_extensions


def get_video_files_in_directory(directory: Union[str, Path], recursive: bool = False) -> List[Path]:
    """获取目录中的所有视频文件"""
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        return []

    video_files = []
    pattern = "**/*" if recursive else "*"

    for file_path in directory.glob(pattern):
        if file_path.is_file() and is_video_file(file_path):
            video_files.append(file_path)

    return sorted(video_files)


def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小（字节）"""
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """格式化时长显示"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}分{secs:.1f}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}小时{minutes}分{secs:.1f}秒"


def srt_time_to_seconds(time_str: str) -> float:
    """将SRT时间格式转换为秒数"""
    # 格式: 00:00:00,000
    try:
        time_parts = time_str.split(',')
        hms = time_parts[0].split(':')
        hours = int(hms[0])
        minutes = int(hms[1])
        seconds = int(hms[2])
        milliseconds = int(time_parts[1]) if len(time_parts) > 1 else 0

        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
        return total_seconds
    except (ValueError, IndexError):
        return 0.0


def seconds_to_srt_time(seconds: float) -> str:
    """将秒数转换为SRT时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def vtt_time_to_seconds(time_str: str) -> float:
    """将VTT时间格式转换为秒数"""
    # 格式: 00:00:00.000
    try:
        time_parts = time_str.split('.')
        hms = time_parts[0].split(':')

        if len(hms) == 2:  # MM:SS format
            minutes = int(hms[0])
            seconds = int(hms[1])
            hours = 0
        else:  # HH:MM:SS format
            hours = int(hms[0])
            minutes = int(hms[1])
            seconds = int(hms[2])

        milliseconds = int(time_parts[1]) if len(time_parts) > 1 else 0

        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
        return total_seconds
    except (ValueError, IndexError):
        return 0.0


def seconds_to_vtt_time(seconds: float) -> str:
    """将秒数转换为VTT时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def clean_text(text: str) -> str:
    """清理文本，移除特殊字符和格式"""
    if not text:
        return ""

    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除字幕格式标记
    text = re.sub(r'\{[^}]*\}', '', text)  # 移除 {formatting}
    text = re.sub(r'\\[NnRr]', ' ', text)  # 移除换行符

    # 标准化Unicode字符
    text = unicodedata.normalize('NFKC', text)

    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def split_text_by_length(text: str, max_length: int = 500, preserve_sentences: bool = True) -> List[str]:
    """按长度分割文本，尽量保持句子完整"""
    if len(text) <= max_length:
        return [text]

    chunks = []

    if preserve_sentences:
        # 按句号、问号、感叹号分割
        sentences = re.split(r'[.!?。！？]+', text)
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"

        if current_chunk:
            chunks.append(current_chunk.strip())
    else:
        # 简单按长度分割
        for i in range(0, len(text), max_length):
            chunks.append(text[i:i + max_length])

    return chunks


def detect_text_encoding(file_path: Union[str, Path]) -> str:
    """检测文本文件编码"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    except Exception:
        return 'utf-8'


def safe_filename(filename: str) -> str:
    """生成安全的文件名，移除不合法字符"""
    # 移除不合法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # 移除控制字符
    filename = ''.join(char for char in filename if ord(char) >= 32)

    # 限制长度
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext

    return filename.strip()


def generate_unique_filename(directory: Union[str, Path], filename: str) -> Path:
    """生成唯一的文件名（如果文件已存在则添加数字后缀）"""
    directory = Path(directory)
    file_path = directory / filename

    if not file_path.exists():
        return file_path

    name, ext = os.path.splitext(filename)
    counter = 1

    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = directory / new_filename
        if not new_path.exists():
            return new_path
        counter += 1


def create_backup_file(file_path: Union[str, Path]) -> Optional[Path]:
    """创建文件备份"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        backup_path = file_path.parent / backup_name

        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception:
        return None


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """计算文件哈希值"""
    hash_func = getattr(hashlib, algorithm.lower())()

    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception:
        return ""


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e

                    time.sleep(current_delay)
                    current_delay *= backoff

            return None
        return wrapper
    return decorator


def validate_url(url: str) -> bool:
    """验证URL格式"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """扁平化嵌套字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def batch_process(items: List[Any], batch_size: int = 10) -> List[List[Any]]:
    """将列表分批处理"""
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches


def progress_callback(current: int, total: int, callback: Optional[Callable] = None):
    """进度回调函数"""
    if callback:
        progress = (current / total) * 100 if total > 0 else 0
        callback(current, total, progress)


class ThreadSafeCounter:
    """线程安全的计数器"""

    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> int:
        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount: int = 1) -> int:
        with self._lock:
            self._value -= amount
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

    def reset(self):
        with self._lock:
            self._value = 0


class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, total: int):
        self.total = total
        self.current = 0
        self.start_time = time.time()
        self._lock = threading.Lock()

    def update(self, amount: int = 1):
        with self._lock:
            self.current += amount

    def get_progress(self) -> Dict[str, Any]:
        with self._lock:
            elapsed = time.time() - self.start_time
            progress = (self.current / self.total) * 100 if self.total > 0 else 0

            if self.current > 0 and elapsed > 0:
                rate = self.current / elapsed
                eta = (self.total - self.current) / rate if rate > 0 else 0
            else:
                rate = 0
                eta = 0

            return {
                'current': self.current,
                'total': self.total,
                'progress': progress,
                'elapsed': elapsed,
                'eta': eta,
                'rate': rate
            }

    def reset(self):
        with self._lock:
            self.current = 0
            self.start_time = time.time()


def check_ffmpeg_available() -> bool:
    """检查FFmpeg是否可用"""
    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True,
                      check=True,
                      timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def temp_file_context(suffix: str = '', prefix: str = 'temp_', directory: Optional[str] = None):
    """临时文件上下文管理器"""
    class TempFileContext:
        def __init__(self):
            self.temp_file = None

        def __enter__(self):
            fd, self.temp_file = tempfile.mkstemp(
                suffix=suffix,
                prefix=prefix,
                dir=directory
            )
            os.close(fd)  # 关闭文件描述符，但保留文件
            return Path(self.temp_file)

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.temp_file and os.path.exists(self.temp_file):
                try:
                    os.unlink(self.temp_file)
                except OSError:
                    pass

    return TempFileContext()


def sanitize_subtitle_text(text: str) -> str:
    """清理字幕文本"""
    if not text:
        return ""

    # 移除多余的空行
    text = re.sub(r'\n\s*\n', '\n', text)

    # 移除行首行尾空格
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)

    # 处理常见的字幕格式问题
    text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # 句子间添加空格
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # 移除标点前的空格

    return text


def validate_subtitle_timing(start_time: float, end_time: float, min_duration: float = 0.1) -> Tuple[float, float]:
    """验证和修正字幕时间"""
    # 确保开始时间不为负数
    start_time = max(0, start_time)

    # 确保结束时间大于开始时间
    if end_time <= start_time:
        end_time = start_time + min_duration

    # 确保最小持续时间
    if end_time - start_time < min_duration:
        end_time = start_time + min_duration

    return start_time, end_time


def estimate_translation_time(text_length: int, provider: str = 'openai') -> float:
    """估算翻译时间"""
    # 基于经验的时间估算（秒）
    base_times = {
        'openai': 0.1,      # 每字符0.1秒
        'anthropic': 0.12,  # 每字符0.12秒
        'google': 0.05,     # 每字符0.05秒
        'azure': 0.06       # 每字符0.06秒
    }

    base_time = base_times.get(provider, 0.1)
    estimated_time = text_length * base_time

    # 添加网络延迟和处理开销
    overhead = min(5.0, estimated_time * 0.2)

    return estimated_time + overhead
