"""
视频处理核心模块
处理视频文件信息获取、字幕提取、元数据分析等功能
"""

import os
import re
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
from datetime import timedelta

import ffmpeg
from ..utils.helpers import (
    is_video_file,
    format_duration,
    format_file_size,
    get_file_size,
    temp_file_context,
    retry_on_failure,
    check_ffmpeg_available
)

logger = logging.getLogger(__name__)


class VideoInfo:
    """视频信息类"""

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.duration = 0.0
        self.width = 0
        self.height = 0
        self.fps = 0.0
        self.bitrate = 0
        self.file_size = 0
        self.format_name = ""
        self.video_codec = ""
        self.audio_codec = ""
        self.subtitle_streams = []
        self.audio_streams = []
        self.video_streams = []
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'file_path': str(self.file_path),
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'bitrate': self.bitrate,
            'file_size': self.file_size,
            'format_name': self.format_name,
            'video_codec': self.video_codec,
            'audio_codec': self.audio_codec,
            'subtitle_streams': self.subtitle_streams,
            'audio_streams': self.audio_streams,
            'video_streams': self.video_streams,
            'metadata': self.metadata
        }


class SubtitleStream:
    """字幕流信息类"""

    def __init__(self, index: int, codec: str, language: str = None, title: str = None):
        self.index = index
        self.codec = codec
        self.language = language or 'unknown'
        self.title = title or f'Subtitle {index}'
        self.is_forced = False
        self.is_default = False

    def __str__(self):
        return f"Stream {self.index}: {self.title} ({self.language}, {self.codec})"


class VideoProcessor:
    """视频处理器"""

    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """检查FFmpeg是否可用"""
        if not check_ffmpeg_available():
            raise RuntimeError(
                "FFmpeg未找到或不可用。请确保FFmpeg已安装并添加到系统PATH中。\n"
                "下载地址: https://ffmpeg.org/download.html"
            )

    @retry_on_failure(max_retries=3, delay=1.0)
    def get_video_info(self, file_path: Union[str, Path]) -> VideoInfo:
        """获取视频文件信息"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {file_path}")

        if not is_video_file(file_path):
            raise ValueError(f"不是有效的视频文件: {file_path}")

        logger.info(f"正在分析视频文件: {file_path.name}")

        video_info = VideoInfo(file_path)
        video_info.file_size = get_file_size(file_path)

        try:
            # 使用ffprobe获取详细信息
            probe_data = self._probe_file(file_path)
            self._parse_probe_data(video_info, probe_data)

        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            # 尝试备用方法
            try:
                self._get_basic_info_fallback(video_info)
            except Exception as fallback_error:
                logger.error(f"备用方法也失败: {fallback_error}")
                raise RuntimeError(f"无法获取视频信息: {e}")

        logger.info(f"视频信息获取完成: {video_info.format_name}, "
                   f"{video_info.width}x{video_info.height}, "
                   f"{format_duration(video_info.duration)}")

        return video_info

    def _probe_file(self, file_path: Path) -> Dict[str, Any]:
        """使用ffprobe获取文件信息"""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            return json.loads(result.stdout)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffprobe执行失败: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("ffprobe执行超时")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"解析ffprobe输出失败: {e}")

    def _parse_probe_data(self, video_info: VideoInfo, probe_data: Dict[str, Any]):
        """解析ffprobe数据"""
        # 解析格式信息
        format_info = probe_data.get('format', {})
        video_info.duration = float(format_info.get('duration', 0))
        video_info.bitrate = int(format_info.get('bit_rate', 0))
        video_info.format_name = format_info.get('format_name', '')
        video_info.metadata = format_info.get('tags', {})

        # 解析流信息
        streams = probe_data.get('streams', [])

        for stream in streams:
            codec_type = stream.get('codec_type', '')
            codec_name = stream.get('codec_name', '')
            index = stream.get('index', 0)

            if codec_type == 'video':
                video_info.video_streams.append(stream)
                if not video_info.video_codec:  # 使用第一个视频流的信息
                    video_info.video_codec = codec_name
                    video_info.width = stream.get('width', 0)
                    video_info.height = stream.get('height', 0)

                    # 计算帧率
                    r_frame_rate = stream.get('r_frame_rate', '0/1')
                    if '/' in r_frame_rate:
                        num, den = map(int, r_frame_rate.split('/'))
                        video_info.fps = num / den if den != 0 else 0

            elif codec_type == 'audio':
                video_info.audio_streams.append(stream)
                if not video_info.audio_codec:
                    video_info.audio_codec = codec_name

            elif codec_type == 'subtitle':
                subtitle_stream = self._parse_subtitle_stream(stream)
                video_info.subtitle_streams.append(subtitle_stream)

    def _parse_subtitle_stream(self, stream: Dict[str, Any]) -> SubtitleStream:
        """解析字幕流信息"""
        index = stream.get('index', 0)
        codec = stream.get('codec_name', 'unknown')

        # 获取语言信息
        tags = stream.get('tags', {})
        language = tags.get('language', tags.get('lang', 'unknown'))
        title = tags.get('title', f'Subtitle {index}')

        subtitle_stream = SubtitleStream(index, codec, language, title)

        # 检查是否为强制字幕或默认字幕
        disposition = stream.get('disposition', {})
        subtitle_stream.is_forced = disposition.get('forced', 0) == 1
        subtitle_stream.is_default = disposition.get('default', 0) == 1

        return subtitle_stream

    def _get_basic_info_fallback(self, video_info: VideoInfo):
        """备用方法获取基本信息"""
        try:
            probe = ffmpeg.probe(str(video_info.file_path))

            format_info = probe.get('format', {})
            video_info.duration = float(format_info.get('duration', 0))
            video_info.format_name = format_info.get('format_name', '')

            # 查找视频流
            video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
            if video_streams:
                video_stream = video_streams[0]
                video_info.width = video_stream.get('width', 0)
                video_info.height = video_stream.get('height', 0)
                video_info.video_codec = video_stream.get('codec_name', '')

        except Exception as e:
            logger.warning(f"备用方法获取信息失败: {e}")

    def extract_subtitle(self, video_path: Union[str, Path],
                        subtitle_index: int = 0,
                        output_path: Optional[Union[str, Path]] = None,
                        output_format: str = 'srt') -> Optional[Path]:
        """提取指定的字幕轨道"""
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        # 获取视频信息以验证字幕轨道
        video_info = self.get_video_info(video_path)

        if not video_info.subtitle_streams:
            logger.warning(f"视频文件没有字幕轨道: {video_path.name}")
            return None

        # 验证字幕索引
        subtitle_streams = video_info.subtitle_streams
        target_stream = None

        for stream in subtitle_streams:
            if stream.index == subtitle_index:
                target_stream = stream
                break

        if not target_stream:
            available_indexes = [s.index for s in subtitle_streams]
            raise ValueError(
                f"字幕轨道索引 {subtitle_index} 不存在。"
                f"可用索引: {available_indexes}"
            )

        # 确定输出路径
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_{subtitle_index}.{output_format}"
        else:
            output_path = Path(output_path)

        logger.info(f"正在提取字幕: {target_stream}")

        try:
            self._extract_subtitle_with_ffmpeg(
                video_path,
                subtitle_index,
                output_path,
                output_format
            )

            if output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"字幕提取成功: {output_path}")
                return output_path
            else:
                logger.error("字幕提取失败：输出文件为空或不存在")
                return None

        except Exception as e:
            logger.error(f"字幕提取失败: {e}")
            if output_path.exists():
                output_path.unlink()  # 删除失败的文件
            return None

    def _extract_subtitle_with_ffmpeg(self, video_path: Path,
                                    subtitle_index: int,
                                    output_path: Path,
                                    output_format: str):
        """使用FFmpeg提取字幕"""
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-map', f'0:s:{subtitle_index}',
            '-c:s', self._get_subtitle_codec(output_format),
            '-y',  # 覆盖输出文件
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5分钟超时
            )

            logger.debug(f"FFmpeg输出: {result.stderr}")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg提取字幕失败: {error_msg}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("FFmpeg提取字幕超时")

    def _get_subtitle_codec(self, format_name: str) -> str:
        """根据格式获取字幕编码器"""
        codec_map = {
            'srt': 'srt',
            'vtt': 'webvtt',
            'ass': 'ass',
            'ssa': 'ssa',
            'sub': 'text'
        }
        return codec_map.get(format_name.lower(), 'srt')

    def extract_all_subtitles(self, video_path: Union[str, Path],
                            output_dir: Optional[Union[str, Path]] = None,
                            output_format: str = 'srt') -> Dict[int, Path]:
        """提取所有字幕轨道"""
        video_path = Path(video_path)

        if output_dir is None:
            output_dir = video_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        video_info = self.get_video_info(video_path)
        extracted_subtitles = {}

        if not video_info.subtitle_streams:
            logger.info(f"视频文件没有字幕轨道: {video_path.name}")
            return extracted_subtitles

        for subtitle_stream in video_info.subtitle_streams:
            try:
                output_filename = (
                    f"{video_path.stem}_sub_{subtitle_stream.index}"
                    f"_{subtitle_stream.language}.{output_format}"
                )
                output_path = output_dir / output_filename

                extracted_path = self.extract_subtitle(
                    video_path,
                    subtitle_stream.index,
                    output_path,
                    output_format
                )

                if extracted_path:
                    extracted_subtitles[subtitle_stream.index] = extracted_path

            except Exception as e:
                logger.error(f"提取字幕轨道 {subtitle_stream.index} 失败: {e}")
                continue

        logger.info(f"成功提取 {len(extracted_subtitles)} 个字幕轨道")
        return extracted_subtitles

    def has_subtitles(self, video_path: Union[str, Path]) -> bool:
        """检查视频是否包含字幕"""
        try:
            video_info = self.get_video_info(video_path)
            return len(video_info.subtitle_streams) > 0
        except Exception:
            return False

    def get_subtitle_languages(self, video_path: Union[str, Path]) -> List[str]:
        """获取视频中所有字幕的语言列表"""
        try:
            video_info = self.get_video_info(video_path)
            return [stream.language for stream in video_info.subtitle_streams]
        except Exception:
            return []

    def convert_video_format(self, input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           output_format: str = 'mp4',
                           quality: str = 'medium') -> bool:
        """转换视频格式"""
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        quality_settings = {
            'fast': ['-preset', 'fast', '-crf', '28'],
            'medium': ['-preset', 'medium', '-crf', '23'],
            'slow': ['-preset', 'slow', '-crf', '20'],
            'high': ['-preset', 'slow', '-crf', '18']
        }

        settings = quality_settings.get(quality, quality_settings['medium'])

        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            *settings,
            '-y',
            str(output_path)
        ]

        try:
            logger.info(f"开始转换视频格式: {input_path.name} -> {output_path.name}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"视频格式转换完成: {output_path}")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            logger.error(f"视频格式转换失败: {error_msg}")
            return False

    def extract_audio(self, video_path: Union[str, Path],
                     output_path: Optional[Union[str, Path]] = None,
                     audio_format: str = 'wav',
                     sample_rate: int = 16000) -> Optional[Path]:
        """从视频中提取音频"""
        video_path = Path(video_path)

        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}.{audio_format}"
        else:
            output_path = Path(output_path)

        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # 不处理视频
            '-acodec', 'pcm_s16le' if audio_format == 'wav' else 'mp3',
            '-ar', str(sample_rate),
            '-ac', '1',  # 单声道
            '-y',
            str(output_path)
        ]

        try:
            logger.info(f"正在提取音频: {video_path.name}")

            subprocess.run(
                cmd,
                capture_output=True,
                check=True
            )

            logger.info(f"音频提取完成: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"音频提取失败: {e}")
            return None

    def get_video_thumbnail(self, video_path: Union[str, Path],
                          output_path: Optional[Union[str, Path]] = None,
                          timestamp: float = 10.0) -> Optional[Path]:
        """生成视频缩略图"""
        video_path = Path(video_path)

        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_thumb.jpg"
        else:
            output_path = Path(output_path)

        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-ss', str(timestamp),
            '-vframes', '1',
            '-q:v', '2',  # 高质量
            '-y',
            str(output_path)
        ]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                check=True
            )

            return output_path

        except subprocess.CalledProcessError:
            return None
