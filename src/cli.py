#!/usr/bin/env python3
"""
视频翻译器命令行界面
Video Translator Command Line Interface
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import List, Optional
import logging

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from tqdm import tqdm
from src.core.video_processor import VideoProcessor
from src.core.subtitle_extractor import SubtitleExtractor
from src.core.translator import TranslationManager, TranslationProvider
from src.core.subtitle_writer import SubtitleWriter
from src.utils.config import get_config, setup_logging
from src.utils.logger import init_logger, get_logger
from src.utils.helpers import (
    is_video_file,
    get_video_files_in_directory,
    format_duration,
    format_file_size,
    check_ffmpeg_available
)

logger = get_logger(__name__)


class CLIProgressCallback:
    """命令行进度回调"""

    def __init__(self, total_segments: int, description: str = "翻译进度"):
        self.pbar = tqdm(
            total=total_segments,
            desc=description,
            unit="段",
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )

    def update(self, current: int, total: int, progress: float):
        """更新进度"""
        self.pbar.n = current
        self.pbar.refresh()

    def close(self):
        """关闭进度条"""
        self.pbar.close()


class VideoTranslatorCLI:
    """视频翻译器命令行接口"""

    def __init__(self):
        self.config = get_config()
        self.video_processor = VideoProcessor()
        self.subtitle_extractor = SubtitleExtractor()
        self.translation_manager = TranslationManager()
        self.subtitle_writer = SubtitleWriter()

    def create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            description="视频翻译器 - 提取和翻译视频字幕",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  # 查看视频中的字幕轨道
  python cli.py --list-subtitles video.mp4

  # 翻译指定的字幕轨道
  python cli.py -i video.mp4 --subtitle-index 0 -o output.srt -l zh-CN

  # 翻译所有字幕轨道
  python cli.py -i video.mp4 --extract-all-subtitles --output-dir ./output -l zh-CN

  # 批量翻译目录下所有视频
  python cli.py --input-dir /path/to/videos --output-dir /path/to/output -l zh-CN

  # 指定翻译提供商和模型
  python cli.py -i video.mp4 --provider openai --model gpt-4 -l zh-CN

  # 生成多种格式字幕
  python cli.py -i video.mp4 --formats srt,vtt,ass -l zh-CN
            """
        )

        # 输入选项
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument(
            "-i", "--input",
            help="输入视频文件路径"
        )
        input_group.add_argument(
            "--input-dir",
            help="输入视频文件目录（递归搜索）"
        )
        input_group.add_argument(
            "--input-files",
            nargs="+",
            help="多个输入视频文件路径"
        )

        # 输出选项
        parser.add_argument(
            "-o", "--output",
            help="输出字幕文件路径（单文件输入时使用）"
        )
        parser.add_argument(
            "--output-dir",
            help="输出目录（批量处理时使用，默认为输入文件所在目录）"
        )

        # 翻译选项
        parser.add_argument(
            "-l", "--language",
            default="zh-CN",
            help="目标语言代码（默认: zh-CN）"
        )
        parser.add_argument(
            "--provider",
            choices=["openai", "anthropic", "google", "azure"],
            help="AI翻译提供商（默认从配置文件读取）"
        )
        parser.add_argument(
            "--model",
            help="使用的AI模型（默认从配置文件读取）"
        )

        # 字幕选项
        parser.add_argument(
            "--formats",
            default="srt",
            help="输出字幕格式，用逗号分隔（支持: srt,vtt,ass，默认: srt）"
        )
        parser.add_argument(
            "--bilingual",
            action="store_true",
            help="生成双语字幕（原文+译文）"
        )
        parser.add_argument(
            "--monolingual",
            action="store_true",
            help="生成单语字幕（仅译文）"
        )
        parser.add_argument(
            "--subtitle-index",
            type=int,
            default=0,
            help="要提取的字幕轨道索引（默认: 0）。使用 --list-subtitles 查看可用轨道"
        )
        parser.add_argument(
            "--extract-all-subtitles",
            action="store_true",
            help="提取并翻译所有字幕轨道（忽略 --subtitle-index 选项）"
        )

        # 其他选项
        parser.add_argument(
            "--encoding",
            default="utf-8",
            help="输出文件编码（默认: utf-8）"
        )
        parser.add_argument(
            "--no-backup",
            action="store_true",
            help="不创建备份文件"
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="覆盖已存在的输出文件"
        )

        # 调试选项
        parser.add_argument(
            "-v", "--verbose",
            action="count",
            default=0,
            help="详细输出模式（-v 或 -vv）"
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="静默模式"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="试运行模式（不执行实际翻译）"
        )

        # 信息选项
        parser.add_argument(
            "--list-providers",
            action="store_true",
            help="列出可用的翻译提供商"
        )
        parser.add_argument(
            "--list-languages",
            action="store_true",
            help="列出支持的语言"
        )
        parser.add_argument(
            "--info",
            help="显示视频文件的详细信息（包括字幕轨道）"
        )
        parser.add_argument(
            "--list-subtitles",
            help="列出视频文件中的所有字幕轨道及其索引，用于选择要翻译的轨道"
        )

        return parser

    def setup_logging(self, verbose_level: int, quiet: bool):
        """设置日志级别"""
        if quiet:
            log_level = logging.WARNING
        elif verbose_level >= 2:
            log_level = logging.DEBUG
        elif verbose_level >= 1:
            log_level = logging.INFO
        else:
            log_level = logging.WARNING

        # 更新日志配置
        logging.getLogger().setLevel(log_level)

        # 为控制台处理器设置级别
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(log_level)

    def list_providers(self):
        """列出可用的翻译提供商"""
        print("可用的翻译提供商:")
        print("-" * 40)

        available_providers = self.translation_manager.get_available_providers()
        all_providers = self.config.get_translation_providers()

        for provider_key, provider_info in all_providers.items():
            provider_enum = None
            try:
                provider_enum = TranslationProvider(provider_key)
            except ValueError:
                continue

            status = "✅ 可用" if provider_enum in available_providers else "❌ 不可用"

            print(f"{provider_key:12} | {provider_info['name']:20} | {status}")

            if provider_info.get('models'):
                models = ", ".join(provider_info['models'][:3])  # 只显示前3个模型
                if len(provider_info['models']) > 3:
                    models += "..."
                print(f"{'':12} | 模型: {models}")

            print(f"{'':12} | {provider_info.get('description', '')}")
            print()

    def list_languages(self):
        """列出支持的语言"""
        print("支持的目标语言:")
        print("-" * 40)

        languages = self.config.get_supported_languages()

        # 按语言代码排序
        sorted_languages = sorted(languages.items())

        for i, (code, name) in enumerate(sorted_languages):
            print(f"{code:8} | {name}")

            # 每20个语言换行分组
            if (i + 1) % 20 == 0 and i < len(sorted_languages) - 1:
                print()

    def show_video_info(self, video_path: str):
        """显示视频文件信息"""
        try:
            path = Path(video_path)
            if not path.exists():
                print(f"❌ 文件不存在: {video_path}")
                return

            if not is_video_file(path):
                print(f"❌ 不是有效的视频文件: {video_path}")
                return

            print(f"视频文件信息: {path.name}")
            print("=" * 60)

            # 获取视频信息
            video_info = self.video_processor.get_video_info(path)

            # 基本信息
            print(f"文件路径: {video_info.file_path}")
            print(f"文件大小: {format_file_size(video_info.file_size)}")
            print(f"格式: {video_info.format_name}")
            print(f"时长: {format_duration(video_info.duration)}")
            print()

            # 视频信息
            print("视频流:")
            print(f"  分辨率: {video_info.width} x {video_info.height}")
            print(f"  编码: {video_info.video_codec}")
            print(f"  帧率: {video_info.fps:.2f} fps")
            print(f"  比特率: {video_info.bitrate} bps")
            print()

            # 音频信息
            print("音频流:")
            print(f"  编码: {video_info.audio_codec}")
            print(f"  音频流数量: {len(video_info.audio_streams)}")
            print()

            # 字幕信息
            print("字幕流:")
            print(f"  字幕轨道数量: {len(video_info.subtitle_streams)}")

            if video_info.subtitle_streams:
                for i, subtitle in enumerate(video_info.subtitle_streams):
                    print(f"  轨道 {i}: {subtitle.title} ({subtitle.language}, {subtitle.codec})")
                    if subtitle.is_default:
                        print(f"    [默认轨道]")
                    if subtitle.is_forced:
                        print(f"    [强制字幕]")
            else:
                print("  未检测到字幕轨道")

        except Exception as e:
            print(f"❌ 获取视频信息失败: {e}")
            logger.error(f"获取视频信息失败: {e}")

    def list_subtitle_tracks(self, video_path: Path):
        """列出视频文件中的字幕轨道"""
        try:
            if not video_path.exists():
                print(f"❌ 文件不存在: {video_path}")
                return

            if not is_video_file(video_path):
                print(f"❌ 不是有效的视频文件: {video_path}")
                return

            print(f"字幕轨道列表: {video_path.name}")
            print("=" * 60)

            # 获取视频信息
            video_info = self.video_processor.get_video_info(video_path)

            if not video_info.subtitle_streams:
                print("❌ 未检测到字幕轨道")
                return

            print(f"找到 {len(video_info.subtitle_streams)} 个字幕轨道:")
            print()

            for i, subtitle in enumerate(video_info.subtitle_streams):
                print(f"轨道 {subtitle.index}:")
                print(f"  标题: {subtitle.title}")
                print(f"  语言: {subtitle.language}")
                print(f"  编码: {subtitle.codec}")

                flags = []
                if subtitle.is_default:
                    flags.append("默认")
                if subtitle.is_forced:
                    flags.append("强制")

                if flags:
                    print(f"  标记: {', '.join(flags)}")

                print()

            print("使用方法:")
            print(f"  python cli.py -i \"{video_path}\" --subtitle-index <轨道索引> -o output.srt -l zh-CN")
            print("  例如:")
            for subtitle in video_info.subtitle_streams[:3]:  # 只显示前3个作为示例
                print(f"    python cli.py -i \"{video_path}\" --subtitle-index {subtitle.index} -o output_{subtitle.language}.srt -l zh-CN")

        except Exception as e:
            print(f"❌ 获取字幕轨道信息失败: {e}")
            logger.error(f"获取字幕轨道信息失败: {e}")

    def get_input_files(self, args) -> List[Path]:
        """获取输入文件列表"""
        files = []

        if args.input:
            # 单个文件
            path = Path(args.input)
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {args.input}")
            if not is_video_file(path):
                raise ValueError(f"不是有效的视频文件: {args.input}")
            files.append(path)

        elif args.input_dir:
            # 目录
            directory = Path(args.input_dir)
            if not directory.exists():
                raise FileNotFoundError(f"目录不存在: {args.input_dir}")
            if not directory.is_dir():
                raise ValueError(f"不是有效的目录: {args.input_dir}")

            video_files = get_video_files_in_directory(directory, recursive=True)
            if not video_files:
                raise ValueError(f"目录中未找到视频文件: {args.input_dir}")
            files.extend(video_files)

        elif args.input_files:
            # 多个文件
            for file_path in args.input_files:
                path = Path(file_path)
                if not path.exists():
                    print(f"⚠️  跳过不存在的文件: {file_path}")
                    continue
                if not is_video_file(path):
                    print(f"⚠️  跳过非视频文件: {file_path}")
                    continue
                files.append(path)

            if not files:
                raise ValueError("没有找到有效的视频文件")

        return files

    def get_output_path(self, input_path: Path, args) -> Path:
        """获取输出路径"""
        if args.output and len(args.input_files or [args.input]) == 1:
            # 单文件输出路径
            return Path(args.output)

        # 自动生成输出路径
        output_dir = Path(args.output_dir) if args.output_dir else input_path.parent

        # 确定输出格式
        output_format = args.formats.split(',')[0]  # 使用第一个格式
        bilingual = args.bilingual or (not args.monolingual and self.config.get('translation.output_format') == 'bilingual')

        output_filename = self.subtitle_writer.get_output_filename(
            input_path.name,
            args.language,
            output_format,
            bilingual
        )

        return output_dir / output_filename

    async def process_video_file(self, input_path: Path, args) -> bool:
        """处理单个视频文件"""
        try:
            print(f"\n📹 处理文件: {input_path.name}")

            # 获取视频信息
            video_info = self.video_processor.get_video_info(input_path)

            if not video_info.subtitle_streams:
                print(f"⚠️  跳过: 没有字幕轨道")
                return False

            print(f"   时长: {format_duration(video_info.duration)}")
            print(f"   字幕轨道: {len(video_info.subtitle_streams)} 个")

            # 确定要处理的字幕轨道
            subtitle_indexes = []
            if args.extract_all_subtitles:
                subtitle_indexes = [stream.index for stream in video_info.subtitle_streams]
            else:
                if args.subtitle_index < len(video_info.subtitle_streams):
                    subtitle_indexes = [video_info.subtitle_streams[args.subtitle_index].index]
                else:
                    print(f"❌ 字幕轨道索引 {args.subtitle_index} 不存在")
                    return False

            success_count = 0

            for subtitle_index in subtitle_indexes:
                subtitle_stream = next(
                    (s for s in video_info.subtitle_streams if s.index == subtitle_index),
                    None
                )

                if not subtitle_stream:
                    continue

                print(f"   提取字幕轨道 {subtitle_index}: {subtitle_stream.title}")

                if args.dry_run:
                    print(f"   [试运行] 跳过实际处理")
                    continue

                # 提取字幕
                subtitle_path = self.video_processor.extract_subtitle(
                    input_path,
                    subtitle_index,
                    output_format='srt'
                )

                if not subtitle_path:
                    print(f"   ❌ 字幕提取失败")
                    continue

                # 加载字幕文件
                subtitle_file = self.subtitle_extractor.load_subtitle_file(subtitle_path)
                print(f"   字幕片段: {len(subtitle_file.segments)} 个")

                # 翻译字幕
                provider = None
                if args.provider:
                    provider = TranslationProvider(args.provider)

                # 创建进度回调
                progress_callback = CLIProgressCallback(
                    len(subtitle_file.segments),
                    f"翻译 {subtitle_stream.title}"
                )

                try:
                    translated_file = await self.translation_manager.translate_subtitle_file(
                        subtitle_file,
                        args.language,
                        provider,
                        progress_callback.update
                    )

                    progress_callback.close()

                    # 保存翻译结果
                    formats = args.formats.split(',')
                    bilingual = args.bilingual or (not args.monolingual)

                    for format_name in formats:
                        format_name = format_name.strip()
                        output_path = self.get_output_path(input_path, args)

                        # 调整输出文件扩展名
                        output_path = output_path.with_suffix(f'.{format_name}')

                        # 如果有多个轨道，添加轨道标识
                        if len(subtitle_indexes) > 1:
                            stem = output_path.stem
                            output_path = output_path.with_name(f"{stem}_track{subtitle_index}.{format_name}")

                        # 检查文件是否存在
                        if output_path.exists() and not args.overwrite:
                            response = input(f"文件已存在: {output_path}\n是否覆盖? (y/N): ")
                            if response.lower() != 'y':
                                print("跳过保存")
                                continue

                        # 创建输出目录
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        # 写入文件
                        self.subtitle_writer.write_subtitle_file(
                            translated_file,
                            output_path,
                            format_name,
                            bilingual,
                            args.encoding,
                            create_backup=not args.no_backup
                        )

                        print(f"   ✅ 保存: {output_path}")
                        success_count += 1

                except Exception as e:
                    progress_callback.close()
                    print(f"   ❌ 翻译失败: {e}")
                    logger.error(f"翻译字幕失败: {e}")

                finally:
                    # 清理临时字幕文件
                    if subtitle_path and subtitle_path.exists():
                        try:
                            subtitle_path.unlink()
                        except:
                            pass

            return success_count > 0

        except Exception as e:
            print(f"❌ 处理文件失败: {e}")
            logger.error(f"处理文件失败: {e}")
            return False

    async def run(self, args):
        """运行CLI程序"""
        try:
            # 处理信息选项
            if args.list_providers:
                self.list_providers()
                return 0

            if args.list_languages:
                self.list_languages()
                return 0

            if args.info:
                self.show_video_info(Path(args.info))
                return 0

            if args.list_subtitles:
                self.list_subtitle_tracks(Path(args.list_subtitles))
                return 0

            # 验证FFmpeg
            if not check_ffmpeg_available():
                print("❌ FFmpeg未找到，请先安装FFmpeg")
                return 1

            # 获取输入文件
            input_files = self.get_input_files(args)

            print(f"找到 {len(input_files)} 个视频文件")

            if args.dry_run:
                print("🔍 试运行模式 - 不会执行实际翻译")

            # 处理文件
            success_count = 0

            for i, input_path in enumerate(input_files):
                print(f"\n[{i+1}/{len(input_files)}]", end=" ")

                success = await self.process_video_file(input_path, args)
                if success:
                    success_count += 1

            # 总结
            print(f"\n{'='*60}")
            print(f"处理完成: {success_count}/{len(input_files)} 个文件成功")

            if success_count == len(input_files):
                print("🎉 所有文件处理成功!")
                return 0
            elif success_count > 0:
                print("⚠️  部分文件处理成功")
                return 2
            else:
                print("❌ 所有文件处理失败")
                return 1

        except KeyboardInterrupt:
            print("\n\n用户中断操作")
            return 130

        except Exception as e:
            print(f"\n❌ 程序执行失败: {e}")
            logger.error(f"程序执行失败: {e}")
            return 1


def main():
    """主函数"""
    # 初始化配置和日志
    config = get_config()
    setup_logging()
    init_logger(config.get('logging', {}))

    # 创建CLI实例
    cli = VideoTranslatorCLI()

    # 创建参数解析器
    parser = cli.create_parser()
    args = parser.parse_args()

    # 设置日志级别
    cli.setup_logging(args.verbose, args.quiet)

    # 运行程序
    try:
        exit_code = asyncio.run(cli.run(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n用户中断程序")
        sys.exit(130)
    except Exception as e:
        print(f"程序运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
