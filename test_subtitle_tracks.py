#!/usr/bin/env python3
"""
字幕轨道选择功能测试脚本
Test script for subtitle track selection functionality
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from tkinter import ttk

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.video_processor import VideoProcessor, VideoInfo, SubtitleStream
from src.core.subtitle_extractor import SubtitleExtractor
from src.gui.main_window import VideoTranslatorGUI
from src.cli import VideoTranslatorCLI


class TestSubtitleTrackSelection(unittest.TestCase):
    """测试字幕轨道选择功能"""

    def setUp(self):
        """测试前准备"""
        self.video_processor = VideoProcessor()
        self.subtitle_extractor = SubtitleExtractor()

        # 创建模拟的视频信息对象
        self.mock_video_info = self._create_mock_video_info()

    def _create_mock_video_info(self):
        """创建模拟的视频信息对象"""
        # 创建多个字幕轨道
        subtitle_streams = [
            SubtitleStream(0, "subrip", "en", "English"),
            SubtitleStream(1, "subrip", "zh-CN", "简体中文"),
            SubtitleStream(2, "subrip", "ja", "Japanese"),
            SubtitleStream(3, "ass", "ko", "Korean")
        ]

        # 设置默认和强制标记
        subtitle_streams[0].is_default = True
        subtitle_streams[2].is_forced = True

        video_info = VideoInfo(file_path=Path("test_video.mp4"))
        video_info.file_size = 1024*1024*100  # 100MB
        video_info.format_name = "mp4"
        video_info.duration = 3600.0  # 1小时
        video_info.width = 1920
        video_info.height = 1080
        video_info.video_codec = "h264"
        video_info.audio_codec = "aac"
        video_info.fps = 25.0
        video_info.bitrate = 5000000
        video_info.audio_streams = []
        video_info.subtitle_streams = subtitle_streams

        return video_info

    def test_subtitle_stream_creation(self):
        """测试字幕流对象创建"""
        stream = SubtitleStream(0, "subrip", "en", "English")
        self.assertEqual(stream.index, 0)
        self.assertEqual(stream.codec, "subrip")
        self.assertEqual(stream.language, "en")
        self.assertEqual(stream.title, "English")
        self.assertFalse(stream.is_default)
        self.assertFalse(stream.is_forced)

        # 测试字符串表示
        expected_str = "Stream 0: English (en, subrip)"
        self.assertEqual(str(stream), expected_str)

    def test_video_info_subtitle_streams(self):
        """测试视频信息中的字幕流"""
        self.assertEqual(len(self.mock_video_info.subtitle_streams), 4)

        # 检查各个轨道的属性
        en_track = self.mock_video_info.subtitle_streams[0]
        self.assertEqual(en_track.language, "en")
        self.assertTrue(en_track.is_default)

        zh_track = self.mock_video_info.subtitle_streams[1]
        self.assertEqual(zh_track.language, "zh-CN")
        self.assertFalse(zh_track.is_default)

        ja_track = self.mock_video_info.subtitle_streams[2]
        self.assertTrue(ja_track.is_forced)

    @patch('src.core.video_processor.VideoProcessor.get_video_info')
    def test_cli_list_subtitle_tracks(self, mock_get_video_info):
        """测试CLI列出字幕轨道功能"""
        mock_get_video_info.return_value = self.mock_video_info

        cli = VideoTranslatorCLI()

        # 重定向标准输出来捕获打印内容
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            cli.list_subtitle_tracks(Path("test_video.mp4"))

        output = f.getvalue()

        # 验证输出包含预期内容
        self.assertIn("字幕轨道列表", output)
        self.assertIn("找到 4 个字幕轨道", output)
        self.assertIn("轨道 0:", output)
        self.assertIn("English", output)
        self.assertIn("轨道 1:", output)
        self.assertIn("简体中文", output)
        self.assertIn("默认", output)
        self.assertIn("强制", output)
        self.assertIn("使用方法:", output)

    @patch('src.core.video_processor.VideoProcessor.extract_subtitle')
    @patch('src.core.video_processor.VideoProcessor.get_video_info')
    def test_extract_specific_subtitle_track(self, mock_get_video_info, mock_extract):
        """测试提取特定字幕轨道"""
        mock_get_video_info.return_value = self.mock_video_info
        mock_extract.return_value = Path("output.srt")

        # 测试提取第2个轨道（索引1）
        result = self.video_processor.extract_subtitle(
            Path("test_video.mp4"),
            subtitle_index=1,
            output_path=Path("chinese.srt")
        )

        # 验证调用参数
        mock_extract.assert_called_once_with(
            Path("test_video.mp4"),
            subtitle_index=1,
            output_path=Path("chinese.srt")
        )

    def test_gui_subtitle_track_selection(self):
        """测试GUI字幕轨道选择功能"""
        # 这个测试需要模拟Tkinter环境
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口

            # 创建GUI实例
            with patch('src.gui.main_window.VideoTranslatorGUI.setup_logging'):
                gui = VideoTranslatorGUI(root)

            # 模拟视频信息加载
            gui.current_video_info = self.mock_video_info
            gui.display_video_info(self.mock_video_info)

            # 检查字幕轨道选择器是否正确填充
            track_values = gui.subtitle_track_combo['values']
            self.assertEqual(len(track_values), 4)

            # 检查第一个选项的格式
            first_option = track_values[0]
            self.assertIn("轨道 0", first_option)
            self.assertIn("English", first_option)
            self.assertIn("subrip", first_option)

            # 测试获取选定轨道索引
            gui.subtitle_track_var.set(track_values[1])  # 选择第二个轨道
            selected_index = gui._get_selected_subtitle_track_index(self.mock_video_info)
            self.assertEqual(selected_index, 1)

            root.destroy()

        except tk.TclError:
            # 如果没有图形环境，跳过GUI测试
            self.skipTest("No display available for GUI testing")

    def test_gui_extract_all_change_handler(self):
        """测试GUI提取所有轨道选项变化处理"""
        try:
            root = tk.Tk()
            root.withdraw()

            with patch('src.gui.main_window.VideoTranslatorGUI.setup_logging'):
                gui = VideoTranslatorGUI(root)

            # 模拟有字幕轨道的情况
            gui.subtitle_track_combo['values'] = ["Track 1", "Track 2"]

            # 测试选择提取所有轨道
            gui.extract_all_var.set(True)
            gui._handle_extract_all_change()
            self.assertEqual(gui.subtitle_track_combo.cget('state'), 'disabled')

            # 测试取消提取所有轨道
            gui.extract_all_var.set(False)
            gui._handle_extract_all_change()
            self.assertEqual(gui.subtitle_track_combo.cget('state'), 'readonly')

            root.destroy()

        except tk.TclError:
            self.skipTest("No display available for GUI testing")

    def test_invalid_subtitle_track_index(self):
        """测试无效的字幕轨道索引处理"""
        with patch('src.core.video_processor.VideoProcessor.get_video_info') as mock_get_info:
            mock_get_info.return_value = self.mock_video_info

            # 测试无效索引
            with self.assertRaises(ValueError) as context:
                self.video_processor.extract_subtitle(
                    Path("test_video.mp4"),
                    subtitle_index=99  # 不存在的索引
                )

            self.assertIn("字幕轨道索引 99 不存在", str(context.exception))

    def test_no_subtitle_tracks(self):
        """测试没有字幕轨道的视频"""
        # 创建没有字幕的视频信息
        no_subtitle_video = VideoInfo(file_path=Path("no_subtitle.mp4"))
        no_subtitle_video.file_size = 1024*1024*50
        no_subtitle_video.format_name = "mp4"
        no_subtitle_video.duration = 1800.0
        no_subtitle_video.width = 1280
        no_subtitle_video.height = 720
        no_subtitle_video.video_codec = "h264"
        no_subtitle_video.audio_codec = "aac"
        no_subtitle_video.fps = 30.0
        no_subtitle_video.bitrate = 3000000
        no_subtitle_video.audio_streams = []
        no_subtitle_video.subtitle_streams = []  # 没有字幕轨道

        with patch('src.core.video_processor.VideoProcessor.get_video_info') as mock_get_info:
            mock_get_info.return_value = no_subtitle_video

            result = self.video_processor.extract_subtitle(Path("no_subtitle.mp4"))
            self.assertIsNone(result)

    def test_cli_help_includes_subtitle_options(self):
        """测试CLI帮助信息包含字幕选项"""
        cli = VideoTranslatorCLI()
        parser = cli.create_parser()

        help_text = parser.format_help()

        self.assertIn("--list-subtitles", help_text)
        self.assertIn("--subtitle-index", help_text)
        self.assertIn("--extract-all-subtitles", help_text)
        self.assertIn("查看可用轨道", help_text)

    def test_gui_track_selection_regex(self):
        """测试GUI轨道选择的正则表达式解析"""
        try:
            root = tk.Tk()
            root.withdraw()

            with patch('src.gui.main_window.VideoTranslatorGUI.setup_logging'):
                gui = VideoTranslatorGUI(root)

            # 测试正确格式的轨道字符串
            test_cases = [
                ("轨道 0: English (en, subrip)", 0),
                ("轨道 15: 简体中文 (zh-CN, ass)", 15),
                ("轨道 123: Japanese (ja, subrip)", 123),
            ]

            for track_string, expected_index in test_cases:
                gui.subtitle_track_var.set(track_string)
                result = gui._get_selected_subtitle_track_index(self.mock_video_info)
                self.assertEqual(result, expected_index)

            # 测试无效格式
            gui.subtitle_track_var.set("Invalid format")
            result = gui._get_selected_subtitle_track_index(self.mock_video_info)
            self.assertIsNone(result)

            root.destroy()

        except tk.TclError:
            self.skipTest("No display available for GUI testing")

    @patch('src.core.video_processor.VideoProcessor.extract_all_subtitles')
    @patch('src.core.video_processor.VideoProcessor.get_video_info')
    def test_extract_all_subtitles(self, mock_get_info, mock_extract_all):
        """测试提取所有字幕轨道"""
        mock_get_info.return_value = self.mock_video_info
        mock_extract_all.return_value = {
            0: Path("english.srt"),
            1: Path("chinese.srt"),
            2: Path("japanese.srt"),
            3: Path("korean.srt")
        }

        result = self.video_processor.extract_all_subtitles(Path("test_video.mp4"))

        self.assertEqual(len(result), 4)
        self.assertIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)


def create_demo_video_info():
    """创建演示用的视频信息"""
    print("创建演示视频信息...")

    subtitle_streams = [
        SubtitleStream(0, "subrip", "en", "English"),
        SubtitleStream(1, "subrip", "zh-CN", "简体中文"),
        SubtitleStream(2, "ass", "ja", "Japanese"),
        SubtitleStream(3, "subrip", "fr", "Français"),
        SubtitleStream(4, "webvtt", "es", "Español")
    ]

    subtitle_streams[0].is_default = True
    subtitle_streams[2].is_forced = True

    video_info = VideoInfo(file_path=Path("demo_movie.mkv"))
    video_info.file_size = 1024*1024*1500  # 1.5GB
    video_info.format_name = "matroska"
    video_info.duration = 7200.0  # 2小时
    video_info.width = 1920
    video_info.height = 1080
    video_info.video_codec = "h264"
    video_info.audio_codec = "ac3"
    video_info.fps = 23.976
    video_info.bitrate = 8000000
    video_info.audio_streams = []
    video_info.subtitle_streams = subtitle_streams

    print(f"视频文件: {video_info.file_path}")
    print(f"时长: {video_info.duration/3600:.1f} 小时")
    print(f"分辨率: {video_info.width}x{video_info.height}")
    print(f"字幕轨道数量: {len(video_info.subtitle_streams)}")
    print("\n字幕轨道详情:")

    for i, stream in enumerate(video_info.subtitle_streams):
        flags = []
        if stream.is_default:
            flags.append("默认")
        if stream.is_forced:
            flags.append("强制")

        flag_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"  轨道 {stream.index}: {stream.title} ({stream.language}, {stream.codec}){flag_str}")

    return video_info


def run_interactive_demo():
    """运行交互式演示"""
    print("=" * 60)
    print("字幕轨道选择功能演示")
    print("=" * 60)

    # 创建演示数据
    video_info = create_demo_video_info()

    print("\n可用操作:")
    print("1. 模拟CLI --list-subtitles 命令")
    print("2. 模拟GUI字幕轨道选择")
    print("3. 运行单元测试")
    print("0. 退出")

    while True:
        try:
            choice = input("\n请选择操作 (0-3): ").strip()

            if choice == "0":
                print("演示结束")
                break
            elif choice == "1":
                print("\n--- CLI 字幕轨道列表演示 ---")
                cli = VideoTranslatorCLI()
                with patch('src.core.video_processor.VideoProcessor.get_video_info') as mock:
                    mock.return_value = video_info
                    cli.list_subtitle_tracks(Path("demo_movie.mkv"))

            elif choice == "2":
                print("\n--- GUI 字幕轨道选择演示 ---")
                try:
                    root = tk.Tk()
                    root.withdraw()

                    with patch('src.gui.main_window.VideoTranslatorGUI.setup_logging'):
                        gui = VideoTranslatorGUI(root)

                    gui.display_video_info(video_info)
                    track_values = gui.subtitle_track_combo['values']

                    print("GUI字幕轨道选择器选项:")
                    for i, option in enumerate(track_values):
                        print(f"  {i}: {option}")

                    # 模拟选择第二个轨道
                    gui.subtitle_track_var.set(track_values[1])
                    selected_index = gui._get_selected_subtitle_track_index(video_info)
                    print(f"\n模拟选择: {track_values[1]}")
                    print(f"解析出的轨道索引: {selected_index}")

                    root.destroy()

                except tk.TclError:
                    print("错误: 无法创建GUI (可能没有图形显示环境)")

            elif choice == "3":
                print("\n--- 运行单元测试 ---")
                unittest.main(verbosity=2, exit=False)

            else:
                print("无效选择，请输入 0-3")

        except KeyboardInterrupt:
            print("\n\n演示被中断")
            break
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="字幕轨道选择功能测试")
    parser.add_argument("--test", action="store_true", help="运行单元测试")
    parser.add_argument("--demo", action="store_true", help="运行交互式演示")

    args = parser.parse_args()

    if args.test:
        # 运行单元测试
        unittest.main(verbosity=2)
    elif args.demo:
        # 运行交互式演示
        run_interactive_demo()
    else:
        # 默认运行演示
        print("使用 --test 运行单元测试，或 --demo 运行交互式演示")
        print("直接运行默认为交互式演示模式")
        run_interactive_demo()
