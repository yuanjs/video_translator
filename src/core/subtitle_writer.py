"""
字幕写入模块
处理翻译后字幕的格式化和文件输出
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import timedelta
import logging
import html

from .subtitle_extractor import SubtitleFile, SubtitleSegment
from ..utils.helpers import (
    seconds_to_srt_time,
    seconds_to_vtt_time,
    safe_filename,
    generate_unique_filename,
    create_backup_file,
    sanitize_subtitle_text
)
from ..utils.config import get_config

logger = logging.getLogger(__name__)


class SubtitleFormatter:
    """字幕格式化器基类"""

    def __init__(self, output_format: str = 'bilingual'):
        self.output_format = output_format  # 'bilingual' 或 'monolingual'
        self.config = get_config()

    def format_text(self, segment: SubtitleSegment) -> str:
        """格式化字幕文本"""
        if self.output_format == 'bilingual':
            if segment.translated_text:
                return f"{segment.text}\n{segment.translated_text}"
            else:
                return segment.text
        else:  # monolingual
            return segment.translated_text or segment.text

    def validate_timing(self, segment: SubtitleSegment) -> Tuple[float, float]:
        """验证和修正时间"""
        start_time = max(0, segment.start_time)
        end_time = max(start_time + 0.1, segment.end_time)
        return start_time, end_time


class SRTFormatter(SubtitleFormatter):
    """SRT格式化器"""

    def format_subtitle_file(self, subtitle_file: SubtitleFile) -> str:
        """格式化整个字幕文件为SRT格式"""
        lines = []

        for segment in subtitle_file.segments:
            if not segment.text.strip():
                continue

            start_time, end_time = self.validate_timing(segment)

            # 片段索引
            lines.append(str(segment.index))

            # 时间轴
            start_time_str = seconds_to_srt_time(start_time)
            end_time_str = seconds_to_srt_time(end_time)
            lines.append(f"{start_time_str} --> {end_time_str}")

            # 文本内容
            text = self.format_text(segment)
            text = sanitize_subtitle_text(text)
            lines.append(text)

            # 空行分隔
            lines.append("")

        return "\n".join(lines)


class VTTFormatter(SubtitleFormatter):
    """VTT格式化器"""

    def format_subtitle_file(self, subtitle_file: SubtitleFile) -> str:
        """格式化整个字幕文件为VTT格式"""
        lines = ["WEBVTT", ""]

        # 添加元数据
        if subtitle_file.language and subtitle_file.language != 'unknown':
            lines.append(f"Language: {subtitle_file.language}")
            lines.append("")

        for segment in subtitle_file.segments:
            if not segment.text.strip():
                continue

            start_time, end_time = self.validate_timing(segment)

            # 时间轴
            start_time_str = seconds_to_vtt_time(start_time)
            end_time_str = seconds_to_vtt_time(end_time)
            lines.append(f"{start_time_str} --> {end_time_str}")

            # 文本内容
            text = self.format_text(segment)
            text = sanitize_subtitle_text(text)
            lines.append(text)

            # 空行分隔
            lines.append("")

        return "\n".join(lines)


class ASSFormatter(SubtitleFormatter):
    """ASS格式化器"""

    def __init__(self, output_format: str = 'bilingual'):
        super().__init__(output_format)
        self.style_config = self.config.get('subtitle.ass_style', {})

    def format_subtitle_file(self, subtitle_file: SubtitleFile) -> str:
        """格式化整个字幕文件为ASS格式"""
        lines = []

        # ASS文件头
        lines.extend(self._get_ass_header())

        # 样式定义
        lines.extend(self._get_ass_styles())

        # 事件部分
        lines.append("[Events]")
        lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")

        for segment in subtitle_file.segments:
            if not segment.text.strip():
                continue

            start_time, end_time = self.validate_timing(segment)

            # 转换时间格式
            start_time_str = self._seconds_to_ass_time(start_time)
            end_time_str = self._seconds_to_ass_time(end_time)

            # 文本内容
            text = self.format_text(segment)
            text = self._escape_ass_text(text)

            # 对话行
            dialogue_line = f"Dialogue: 0,{start_time_str},{end_time_str},Default,,0,0,0,,{text}"
            lines.append(dialogue_line)

        return "\n".join(lines)

    def _get_ass_header(self) -> List[str]:
        """获取ASS文件头"""
        return [
            "[Script Info]",
            "Title: Translated Subtitles",
            "ScriptType: v4.00+",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "YCbCr Matrix: TV.601",
            "",
            "[Aegisub Project]",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
        ]

    def _get_ass_styles(self) -> List[str]:
        """获取ASS样式定义"""
        # 默认样式
        default_style = (
            "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
            "0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1"
        )

        styles = [default_style]

        # 如果是双语字幕，添加额外样式
        if self.output_format == 'bilingual':
            original_style = (
                "Style: Original,Arial,18,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
                "0,0,0,0,100,100,0,0,1,2,0,8,10,10,10,1"
            )
            translated_style = (
                "Style: Translated,Arial,18,&H0000FFFF,&H000000FF,&H00000000,&H80000000,"
                "0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1"
            )
            styles.extend([original_style, translated_style])

        styles.append("")
        return styles

    def _seconds_to_ass_time(self, seconds: float) -> str:
        """将秒数转换为ASS时间格式 (H:MM:SS.CC)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds % 1) * 100)

        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

    def _escape_ass_text(self, text: str) -> str:
        """转义ASS文本中的特殊字符"""
        # 替换换行符
        text = text.replace('\n', '\\N')

        # 转义大括号
        text = text.replace('{', '\\{').replace('}', '\\}')

        return text


class SubtitleWriter:
    """字幕写入器"""

    def __init__(self):
        self.config = get_config()
        self.formatters = {
            'srt': SRTFormatter,
            'vtt': VTTFormatter,
            'ass': ASSFormatter
        }

    def write_subtitle_file(self,
                          subtitle_file: SubtitleFile,
                          output_path: Union[str, Path],
                          output_format: str = 'srt',
                          bilingual: bool = True,
                          encoding: str = 'utf-8',
                          create_backup: bool = True) -> Path:
        """写入字幕文件"""
        output_path = Path(output_path)

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 生成安全的文件名
        safe_name = safe_filename(output_path.name)
        output_path = output_path.parent / safe_name

        # 如果文件已存在且需要备份
        if output_path.exists() and create_backup:
            backup_path = create_backup_file(output_path)
            if backup_path:
                logger.info(f"已创建备份文件: {backup_path}")

        # 选择格式化器
        formatter_class = self.formatters.get(output_format.lower(), SRTFormatter)
        output_type = 'bilingual' if bilingual else 'monolingual'
        formatter = formatter_class(output_type)

        logger.info(f"正在写入字幕文件: {output_path} ({output_format.upper()}, {output_type})")

        try:
            # 格式化字幕内容
            content = formatter.format_subtitle_file(subtitle_file)

            # 写入文件
            with open(output_path, 'w', encoding=encoding, newline='\n') as f:
                f.write(content)

            logger.info(f"字幕文件写入完成: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"写入字幕文件失败: {e}")
            raise RuntimeError(f"写入字幕文件失败: {e}")

    def write_multiple_formats(self,
                             subtitle_file: SubtitleFile,
                             output_dir: Union[str, Path],
                             base_filename: str,
                             formats: List[str] = None,
                             bilingual: bool = True,
                             encoding: str = 'utf-8') -> Dict[str, Path]:
        """写入多种格式的字幕文件"""
        if formats is None:
            formats = ['srt', 'vtt']

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        written_files = {}
        base_name = Path(base_filename).stem

        for format_name in formats:
            try:
                output_filename = f"{base_name}.{format_name}"
                output_path = output_dir / output_filename

                written_path = self.write_subtitle_file(
                    subtitle_file,
                    output_path,
                    format_name,
                    bilingual,
                    encoding
                )

                written_files[format_name] = written_path

            except Exception as e:
                logger.error(f"写入 {format_name} 格式失败: {e}")
                continue

        return written_files

    def create_comparison_file(self,
                             original_subtitle: SubtitleFile,
                             translated_subtitle: SubtitleFile,
                             output_path: Union[str, Path],
                             format_type: str = 'srt') -> Path:
        """创建对比文件（原文与译文并排显示）"""
        output_path = Path(output_path)

        # 合并原文和译文
        comparison_segments = []

        for i, orig_segment in enumerate(original_subtitle.segments):
            trans_segment = None
            if i < len(translated_subtitle.segments):
                trans_segment = translated_subtitle.segments[i]

            # 创建对比片段
            comparison_text = orig_segment.text
            if trans_segment and trans_segment.translated_text:
                comparison_text += f"\n{trans_segment.translated_text}"
            elif trans_segment:
                comparison_text += f"\n{trans_segment.text}"

            comparison_segment = SubtitleSegment(
                orig_segment.index,
                orig_segment.start_time,
                orig_segment.end_time,
                comparison_text
            )
            comparison_segments.append(comparison_segment)

        # 创建对比字幕文件
        comparison_file = SubtitleFile()
        comparison_file.segments = comparison_segments
        comparison_file.format = format_type
        comparison_file.language = f"{original_subtitle.language}+{translated_subtitle.language}"

        return self.write_subtitle_file(
            comparison_file,
            output_path,
            format_type,
            bilingual=False  # 已经包含双语内容
        )

    def split_by_language(self,
                         bilingual_subtitle: SubtitleFile,
                         output_dir: Union[str, Path],
                         base_filename: str,
                         format_type: str = 'srt') -> Tuple[Path, Path]:
        """将双语字幕分离为两个单语文件"""
        output_dir = Path(output_dir)
        base_name = Path(base_filename).stem

        # 创建原文字幕文件
        original_file = SubtitleFile()
        original_file.format = format_type
        original_file.language = bilingual_subtitle.language

        # 创建译文字幕文件
        translated_file = SubtitleFile()
        translated_file.format = format_type
        translated_file.language = 'translated'

        for segment in bilingual_subtitle.segments:
            # 原文片段
            orig_segment = SubtitleSegment(
                segment.index,
                segment.start_time,
                segment.end_time,
                segment.text
            )
            original_file.add_segment(orig_segment)

            # 译文片段
            trans_segment = SubtitleSegment(
                segment.index,
                segment.start_time,
                segment.end_time,
                segment.translated_text or segment.text
            )
            translated_file.add_segment(trans_segment)

        # 写入文件
        original_path = output_dir / f"{base_name}_original.{format_type}"
        translated_path = output_dir / f"{base_name}_translated.{format_type}"

        original_written = self.write_subtitle_file(
            original_file, original_path, format_type, bilingual=False
        )
        translated_written = self.write_subtitle_file(
            translated_file, translated_path, format_type, bilingual=False
        )

        return original_written, translated_written

    def merge_subtitle_files(self,
                           subtitle_files: List[SubtitleFile],
                           output_path: Union[str, Path],
                           format_type: str = 'srt',
                           time_offset: float = 0.0) -> Path:
        """合并多个字幕文件"""
        merged_file = SubtitleFile()
        merged_file.format = format_type

        current_time_offset = 0.0
        segment_index = 1

        for subtitle_file in subtitle_files:
            max_end_time = 0.0

            for segment in subtitle_file.segments:
                # 调整时间偏移
                new_start = segment.start_time + current_time_offset
                new_end = segment.end_time + current_time_offset

                merged_segment = SubtitleSegment(
                    segment_index,
                    new_start,
                    new_end,
                    segment.text
                )

                if segment.translated_text:
                    merged_segment.translated_text = segment.translated_text

                merged_file.add_segment(merged_segment)
                segment_index += 1
                max_end_time = max(max_end_time, new_end)

            # 更新时间偏移
            current_time_offset = max_end_time + time_offset

        return self.write_subtitle_file(merged_file, output_path, format_type)

    def validate_subtitle_file(self, subtitle_file: SubtitleFile) -> List[str]:
        """验证字幕文件并返回警告信息"""
        warnings = []
        max_chars_per_line = self.config.get('subtitle.max_chars_per_line', 50)
        min_duration = self.config.get('subtitle.min_segment_duration', 1.0)
        max_duration = 8.0

        for i, segment in enumerate(subtitle_file.segments):
            # 检查时间
            if segment.start_time >= segment.end_time:
                warnings.append(f"片段 {i+1}: 开始时间大于等于结束时间")

            if segment.duration < min_duration:
                warnings.append(f"片段 {i+1}: 持续时间过短 ({segment.duration:.2f}s)")

            if segment.duration > max_duration:
                warnings.append(f"片段 {i+1}: 持续时间过长 ({segment.duration:.2f}s)")

            # 检查文本长度
            lines = segment.text.split('\n')
            for line_num, line in enumerate(lines):
                if len(line) > max_chars_per_line:
                    warnings.append(f"片段 {i+1} 第{line_num+1}行: 文本过长 ({len(line)} 字符)")

            # 检查重叠
            if i > 0:
                prev_segment = subtitle_file.segments[i-1]
                if segment.start_time < prev_segment.end_time:
                    warnings.append(f"片段 {i+1}: 与前一片段时间重叠")

        return warnings

    def get_output_filename(self,
                          original_filename: str,
                          target_language: str,
                          output_format: str,
                          bilingual: bool = True) -> str:
        """生成输出文件名"""
        template = self.config.get('output.filename_template', '{original_name}_{lang}_{format}')

        base_name = Path(original_filename).stem
        format_suffix = 'bilingual' if bilingual else 'mono'

        filename = template.format(
            original_name=base_name,
            lang=target_language.replace('-', '_'),
            format=format_suffix
        )

        return f"{filename}.{output_format}"
