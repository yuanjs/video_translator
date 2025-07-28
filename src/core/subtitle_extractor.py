"""
字幕提取模块
处理字幕文件的读取、解析、格式转换和处理
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import timedelta
import logging
import chardet
import pysrt
import webvtt

from ..utils.helpers import (
    srt_time_to_seconds,
    seconds_to_srt_time,
    vtt_time_to_seconds,
    seconds_to_vtt_time,
    clean_text,
    sanitize_subtitle_text,
    validate_subtitle_timing,
    detect_text_encoding
)

logger = logging.getLogger(__name__)


class SubtitleSegment:
    """字幕片段类"""

    def __init__(self, index: int, start_time: float, end_time: float, text: str):
        self.index = index
        self.start_time = max(0, start_time)  # 确保不为负数
        self.end_time = max(start_time + 0.1, end_time)  # 确保结束时间大于开始时间
        self.text = clean_text(text)
        self.original_text = text
        self.translated_text = ""
        self.confidence = 1.0
        self.speaker = None
        self.style = {}

    @property
    def duration(self) -> float:
        """获取片段持续时间"""
        return self.end_time - self.start_time

    def __str__(self):
        return f"[{self.start_time:.2f}-{self.end_time:.2f}] {self.text}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'index': self.index,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'text': self.text,
            'original_text': self.original_text,
            'translated_text': self.translated_text,
            'duration': self.duration,
            'confidence': self.confidence,
            'speaker': self.speaker,
            'style': self.style
        }


class SubtitleFile:
    """字幕文件类"""

    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        self.file_path = Path(file_path) if file_path else None
        self.segments: List[SubtitleSegment] = []
        self.format = 'srt'
        self.encoding = 'utf-8'
        self.language = 'unknown'
        self.metadata = {}

    def __len__(self):
        return len(self.segments)

    def __iter__(self):
        return iter(self.segments)

    def __getitem__(self, index):
        return self.segments[index]

    def add_segment(self, segment: SubtitleSegment):
        """添加字幕片段"""
        self.segments.append(segment)
        self._sort_segments()

    def _sort_segments(self):
        """按时间排序字幕片段"""
        self.segments.sort(key=lambda s: s.start_time)
        # 重新编号
        for i, segment in enumerate(self.segments):
            segment.index = i + 1

    def get_text_at_time(self, timestamp: float) -> List[str]:
        """获取指定时间点的字幕文本"""
        texts = []
        for segment in self.segments:
            if segment.start_time <= timestamp <= segment.end_time:
                texts.append(segment.text)
        return texts

    def get_total_duration(self) -> float:
        """获取字幕总时长"""
        if not self.segments:
            return 0.0
        return max(segment.end_time for segment in self.segments)

    def get_text_count(self) -> int:
        """获取字幕文本总字符数"""
        return sum(len(segment.text) for segment in self.segments)

    def merge_short_segments(self, min_duration: float = 1.0):
        """合并过短的字幕片段"""
        if not self.segments:
            return

        merged_segments = []
        current_segment = None

        for segment in self.segments:
            if current_segment is None:
                current_segment = segment
            elif (segment.duration < min_duration and
                  segment.start_time - current_segment.end_time < 0.5):
                # 合并到当前片段
                current_segment.end_time = segment.end_time
                current_segment.text += " " + segment.text
            else:
                merged_segments.append(current_segment)
                current_segment = segment

        if current_segment:
            merged_segments.append(current_segment)

        self.segments = merged_segments
        self._sort_segments()


class SubtitleExtractor:
    """字幕提取器"""

    def __init__(self):
        self.supported_formats = {
            '.srt': self._load_srt,
            '.vtt': self._load_vtt,
            '.ass': self._load_ass,
            '.ssa': self._load_ssa,
            '.sub': self._load_sub,
            '.txt': self._load_txt
        }

    def load_subtitle_file(self, file_path: Union[str, Path]) -> SubtitleFile:
        """加载字幕文件"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"字幕文件不存在: {file_path}")

        # 检测文件编码
        encoding = detect_text_encoding(file_path)

        # 根据扩展名选择加载方法
        extension = file_path.suffix.lower()
        if extension not in self.supported_formats:
            logger.warning(f"不支持的字幕格式: {extension}，尝试作为SRT处理")
            extension = '.srt'

        logger.info(f"正在加载字幕文件: {file_path.name} (编码: {encoding})")

        try:
            loader_func = self.supported_formats[extension]
            subtitle_file = loader_func(file_path, encoding)
            subtitle_file.file_path = file_path
            subtitle_file.encoding = encoding
            subtitle_file.format = extension[1:]  # 去掉点号

            logger.info(f"字幕加载完成: {len(subtitle_file.segments)} 个片段")
            return subtitle_file

        except Exception as e:
            logger.error(f"加载字幕文件失败: {e}")
            raise RuntimeError(f"加载字幕文件失败: {e}")

    def _load_srt(self, file_path: Path, encoding: str) -> SubtitleFile:
        """加载SRT格式字幕"""
        subtitle_file = SubtitleFile()

        try:
            # 使用pysrt库加载
            subs = pysrt.open(str(file_path), encoding=encoding)

            for sub in subs:
                start_time = self._pysrt_time_to_seconds(sub.start)
                end_time = self._pysrt_time_to_seconds(sub.end)
                text = sub.text.replace('\n', ' ')

                segment = SubtitleSegment(sub.index, start_time, end_time, text)
                subtitle_file.add_segment(segment)

        except Exception as e:
            # 备用解析方法
            logger.warning(f"pysrt解析失败，使用备用方法: {e}")
            subtitle_file = self._parse_srt_manually(file_path, encoding)

        return subtitle_file

    def _parse_srt_manually(self, file_path: Path, encoding: str) -> SubtitleFile:
        """手动解析SRT文件"""
        subtitle_file = SubtitleFile()

        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()

        # SRT格式正则表达式
        srt_pattern = re.compile(
            r'(\d+)\s*\n'
            r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n'
            r'((?:.*\n?)*?)\n\s*\n',
            re.MULTILINE | re.DOTALL
        )

        matches = srt_pattern.findall(content)

        for match in matches:
            index = int(match[0])
            start_time = srt_time_to_seconds(match[1])
            end_time = srt_time_to_seconds(match[2])
            text = match[3].strip().replace('\n', ' ')

            segment = SubtitleSegment(index, start_time, end_time, text)
            subtitle_file.add_segment(segment)

        return subtitle_file

    def _load_vtt(self, file_path: Path, encoding: str) -> SubtitleFile:
        """加载VTT格式字幕"""
        subtitle_file = SubtitleFile()

        try:
            # 使用webvtt库加载
            vtt = webvtt.read(str(file_path))

            for i, caption in enumerate(vtt, 1):
                start_time = self._vtt_time_to_seconds(caption.start)
                end_time = self._vtt_time_to_seconds(caption.end)
                text = caption.text.replace('\n', ' ')

                segment = SubtitleSegment(i, start_time, end_time, text)
                subtitle_file.add_segment(segment)

        except Exception as e:
            logger.warning(f"webvtt解析失败，使用备用方法: {e}")
            subtitle_file = self._parse_vtt_manually(file_path, encoding)

        return subtitle_file

    def _parse_vtt_manually(self, file_path: Path, encoding: str) -> SubtitleFile:
        """手动解析VTT文件"""
        subtitle_file = SubtitleFile()

        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            lines = f.readlines()

        i = 0
        index = 1

        while i < len(lines):
            line = lines[i].strip()

            # 跳过WEBVTT头和空行
            if line.startswith('WEBVTT') or not line:
                i += 1
                continue

            # 检查是否为时间行
            if '-->' in line:
                time_parts = line.split('-->')
                start_time = vtt_time_to_seconds(time_parts[0].strip())
                end_time = vtt_time_to_seconds(time_parts[1].strip())

                # 读取文本行
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1

                text = ' '.join(text_lines)
                if text:
                    segment = SubtitleSegment(index, start_time, end_time, text)
                    subtitle_file.add_segment(segment)
                    index += 1

            i += 1

        return subtitle_file

    def _load_ass(self, file_path: Path, encoding: str) -> SubtitleFile:
        """加载ASS/SSA格式字幕"""
        subtitle_file = SubtitleFile()

        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            lines = f.readlines()

        dialogue_format = None
        index = 1

        for line in lines:
            line = line.strip()

            # 解析格式定义
            if line.startswith('Format:'):
                dialogue_format = [field.strip() for field in line[7:].split(',')]
                continue

            # 解析对话行
            if line.startswith('Dialogue:') and dialogue_format:
                values = line[9:].split(',', len(dialogue_format) - 1)

                if len(values) >= len(dialogue_format):
                    dialogue_dict = dict(zip(dialogue_format, values))

                    start_time = self._ass_time_to_seconds(dialogue_dict.get('Start', '0:00:00.00'))
                    end_time = self._ass_time_to_seconds(dialogue_dict.get('End', '0:00:01.00'))
                    text = dialogue_dict.get('Text', '')

                    # 清理ASS格式标记
                    text = re.sub(r'\{[^}]*\}', '', text)  # 移除格式标记
                    text = text.replace('\\N', ' ')  # 替换换行

                    if text.strip():
                        segment = SubtitleSegment(index, start_time, end_time, text)
                        subtitle_file.add_segment(segment)
                        index += 1

        return subtitle_file

    def _load_ssa(self, file_path: Path, encoding: str) -> SubtitleFile:
        """加载SSA格式字幕（与ASS相同）"""
        return self._load_ass(file_path, encoding)

    def _load_sub(self, file_path: Path, encoding: str) -> SubtitleFile:
        """加载SUB格式字幕"""
        # SUB格式通常与IDX文件配对，这里简化处理
        subtitle_file = SubtitleFile()

        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            lines = f.readlines()

        index = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 简单的时间戳匹配
            match = re.match(r'(\d+:\d+:\d+\.\d+)\s+(\d+:\d+:\d+\.\d+)\s+(.*)', line)
            if match:
                start_time = vtt_time_to_seconds(match.group(1))
                end_time = vtt_time_to_seconds(match.group(2))
                text = match.group(3)

                segment = SubtitleSegment(index, start_time, end_time, text)
                subtitle_file.add_segment(segment)
                index += 1

        return subtitle_file

    def _load_txt(self, file_path: Path, encoding: str) -> SubtitleFile:
        """加载TXT格式文本（需要推测时间）"""
        subtitle_file = SubtitleFile()

        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        # 假设每行文本持续3秒，间隔0.5秒
        duration_per_line = 3.0
        gap_between_lines = 0.5

        current_time = 0.0

        for i, line in enumerate(lines, 1):
            start_time = current_time
            end_time = start_time + duration_per_line

            segment = SubtitleSegment(i, start_time, end_time, line)
            subtitle_file.add_segment(segment)

            current_time = end_time + gap_between_lines

        return subtitle_file

    def _pysrt_time_to_seconds(self, pysrt_time) -> float:
        """将pysrt时间对象转换为秒数"""
        return (pysrt_time.hours * 3600 +
                pysrt_time.minutes * 60 +
                pysrt_time.seconds +
                pysrt_time.milliseconds / 1000.0)

    def _vtt_time_to_seconds(self, time_str: str) -> float:
        """VTT时间格式转换"""
        return vtt_time_to_seconds(time_str)

    def _ass_time_to_seconds(self, time_str: str) -> float:
        """ASS时间格式转换 (H:MM:SS.CC)"""
        try:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            sec_parts = parts[2].split('.')
            seconds = int(sec_parts[0])
            centiseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0

            return hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
        except (ValueError, IndexError):
            return 0.0

    def create_from_text_list(self, text_list: List[str],
                            duration_per_segment: float = 3.0,
                            gap_between_segments: float = 0.5) -> SubtitleFile:
        """从文本列表创建字幕"""
        subtitle_file = SubtitleFile()
        current_time = 0.0

        for i, text in enumerate(text_list, 1):
            if not text.strip():
                continue

            start_time = current_time
            end_time = start_time + duration_per_segment

            segment = SubtitleSegment(i, start_time, end_time, text.strip())
            subtitle_file.add_segment(segment)

            current_time = end_time + gap_between_segments

        return subtitle_file

    def split_long_segments(self, subtitle_file: SubtitleFile,
                          max_chars: int = 100,
                          max_duration: float = 6.0) -> SubtitleFile:
        """分割过长的字幕片段"""
        new_segments = []

        for segment in subtitle_file.segments:
            if len(segment.text) <= max_chars and segment.duration <= max_duration:
                new_segments.append(segment)
                continue

            # 需要分割
            words = segment.text.split()
            current_text = ""
            segment_start = segment.start_time
            duration_per_char = segment.duration / len(segment.text)

            for word in words:
                test_text = f"{current_text} {word}".strip()

                if len(test_text) > max_chars and current_text:
                    # 创建新片段
                    segment_duration = len(current_text) * duration_per_char
                    segment_end = segment_start + segment_duration

                    new_segment = SubtitleSegment(
                        len(new_segments) + 1,
                        segment_start,
                        segment_end,
                        current_text
                    )
                    new_segments.append(new_segment)

                    # 准备下一个片段
                    current_text = word
                    segment_start = segment_end
                else:
                    current_text = test_text

            # 添加最后一个片段
            if current_text:
                segment_end = segment.end_time
                new_segment = SubtitleSegment(
                    len(new_segments) + 1,
                    segment_start,
                    segment_end,
                    current_text
                )
                new_segments.append(new_segment)

        # 创建新的字幕文件
        new_subtitle_file = SubtitleFile()
        new_subtitle_file.segments = new_segments
        new_subtitle_file.format = subtitle_file.format
        new_subtitle_file.encoding = subtitle_file.encoding
        new_subtitle_file.language = subtitle_file.language
        new_subtitle_file._sort_segments()

        return new_subtitle_file

    def filter_by_time(self, subtitle_file: SubtitleFile,
                      start_time: float = 0.0,
                      end_time: Optional[float] = None) -> SubtitleFile:
        """按时间范围过滤字幕"""
        filtered_segments = []

        for segment in subtitle_file.segments:
            # 检查片段是否在时间范围内
            if segment.end_time < start_time:
                continue

            if end_time is not None and segment.start_time > end_time:
                break

            # 调整时间范围
            new_start = max(segment.start_time, start_time)
            new_end = segment.end_time
            if end_time is not None:
                new_end = min(segment.end_time, end_time)

            if new_start < new_end:
                new_segment = SubtitleSegment(
                    len(filtered_segments) + 1,
                    new_start - start_time,  # 相对时间
                    new_end - start_time,
                    segment.text
                )
                filtered_segments.append(new_segment)

        # 创建新的字幕文件
        filtered_subtitle_file = SubtitleFile()
        filtered_subtitle_file.segments = filtered_segments
        filtered_subtitle_file.format = subtitle_file.format
        filtered_subtitle_file.encoding = subtitle_file.encoding
        filtered_subtitle_file.language = subtitle_file.language

        return filtered_subtitle_file

    def detect_language(self, subtitle_file: SubtitleFile) -> str:
        """检测字幕语言"""
        try:
            from langdetect import detect

            # 获取前几个片段的文本用于检测
            sample_text = " ".join([
                segment.text for segment in subtitle_file.segments[:10]
                if segment.text.strip()
            ])

            if sample_text:
                detected_lang = detect(sample_text)
                logger.info(f"检测到字幕语言: {detected_lang}")
                return detected_lang

        except ImportError:
            logger.warning("langdetect库未安装，无法检测语言")
        except Exception as e:
            logger.warning(f"语言检测失败: {e}")

        return 'unknown'

    def get_subtitle_statistics(self, subtitle_file: SubtitleFile) -> Dict[str, Any]:
        """获取字幕统计信息"""
        if not subtitle_file.segments:
            return {}

        durations = [seg.duration for seg in subtitle_file.segments]
        text_lengths = [len(seg.text) for seg in subtitle_file.segments]

        return {
            'total_segments': len(subtitle_file.segments),
            'total_duration': subtitle_file.get_total_duration(),
            'total_characters': sum(text_lengths),
            'avg_segment_duration': sum(durations) / len(durations),
            'avg_text_length': sum(text_lengths) / len(text_lengths),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'format': subtitle_file.format,
            'encoding': subtitle_file.encoding,
            'language': subtitle_file.language
        }
