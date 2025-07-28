#!/usr/bin/env python3
"""
字幕轨道选择功能演示脚本
Subtitle Track Selection Feature Demo
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.video_processor import VideoProcessor, VideoInfo, SubtitleStream
from src.cli import VideoTranslatorCLI


def create_sample_video_info():
    """创建示例视频信息，包含多个字幕轨道"""
    # 创建多个字幕轨道
    subtitle_streams = [
        SubtitleStream(0, "subrip", "en", "English"),
        SubtitleStream(1, "subrip", "zh-CN", "简体中文"),
        SubtitleStream(2, "ass", "ja", "Japanese"),
        SubtitleStream(3, "subrip", "fr", "Français"),
        SubtitleStream(4, "webvtt", "es", "Español")
    ]

    # 设置一些标记
    subtitle_streams[0].is_default = True  # English 是默认轨道
    subtitle_streams[2].is_forced = True   # Japanese 是强制字幕

    # 创建视频信息对象
    video_info = VideoInfo(file_path=Path("sample_movie.mkv"))
    video_info.file_size = 1024*1024*1200  # 1.2GB
    video_info.format_name = "matroska"
    video_info.duration = 5400.0  # 1.5小时
    video_info.width = 1920
    video_info.height = 1080
    video_info.video_codec = "h264"
    video_info.audio_codec = "ac3"
    video_info.fps = 23.976
    video_info.bitrate = 6000000
    video_info.subtitle_streams = subtitle_streams

    return video_info


def demo_cli_functionality():
    """演示CLI功能"""
    print("=" * 60)
    print("CLI 字幕轨道选择功能演示")
    print("=" * 60)

    # 创建示例数据
    video_info = create_sample_video_info()

    print("1. 使用 --list-subtitles 查看视频中的字幕轨道:")
    print("   命令: python src/cli.py --list-subtitles sample_movie.mkv")
    print()

    # 模拟 CLI 的 list_subtitle_tracks 功能
    cli = VideoTranslatorCLI()
    with patch('src.core.video_processor.VideoProcessor.get_video_info') as mock:
        mock.return_value = video_info
        cli.list_subtitle_tracks(Path("sample_movie.mkv"))

    print("\n" + "=" * 60)
    print("2. 翻译特定字幕轨道的示例命令:")
    print()

    for i, stream in enumerate(video_info.subtitle_streams):
        if i < 3:  # 只显示前3个作为示例
            print(f"   # 翻译{stream.title}轨道:")
            print(f"   python src/cli.py -i sample_movie.mkv --subtitle-index {stream.index} \\")
            print(f"                     -o subtitle_{stream.language}.srt -l zh-CN")
            print()

    print("   # 翻译所有字幕轨道:")
    print("   python src/cli.py -i sample_movie.mkv --extract-all-subtitles \\")
    print("                     --output-dir ./output -l zh-CN")


def demo_gui_functionality():
    """演示GUI功能"""
    print("\n" + "=" * 60)
    print("GUI 字幕轨道选择功能演示")
    print("=" * 60)

    video_info = create_sample_video_info()

    print("GUI界面新增功能:")
    print("1. 字幕轨道选择下拉框")
    print("2. '提取所有字幕轨道' 复选框的改进")
    print()

    print("模拟GUI字幕轨道选择器的选项:")
    for stream in video_info.subtitle_streams:
        flags = []
        if stream.is_default:
            flags.append("默认")
        if stream.is_forced:
            flags.append("强制")

        flag_str = f" [{', '.join(flags)}]" if flags else ""
        track_display = f"轨道 {stream.index}: {stream.title} ({stream.language}, {stream.codec})"
        print(f"   {track_display}{flag_str}")

    print("\nGUI使用流程:")
    print("1. 选择视频文件")
    print("2. 查看右侧显示的视频信息和字幕轨道详情")
    print("3. 在'选择字幕轨道'下拉框中选择要翻译的轨道")
    print("4. 或者勾选'提取所有字幕轨道'来翻译所有轨道")
    print("5. 选择翻译提供商和目标语言")
    print("6. 点击'开始翻译'")


def demo_feature_comparison():
    """功能对比演示"""
    print("\n" + "=" * 60)
    print("新旧功能对比")
    print("=" * 60)

    print("【之前的版本】")
    print("- ❌ 只能翻译第一个字幕轨道")
    print("- ❌ 无法选择特定语言的字幕轨道")
    print("- ❌ 不知道视频中有哪些字幕轨道")
    print("- ✅ 可以选择提取所有轨道")
    print()

    print("【改进后的版本】")
    print("- ✅ 可以查看视频中所有字幕轨道的详细信息")
    print("- ✅ 可以选择任意轨道进行翻译")
    print("- ✅ GUI界面提供友好的轨道选择器")
    print("- ✅ CLI提供 --list-subtitles 命令查看轨道")
    print("- ✅ CLI提供 --subtitle-index 参数选择轨道")
    print("- ✅ 显示轨道的语言、编码、默认/强制标记")
    print("- ✅ 保留原有的'提取所有轨道'功能")


def demo_real_world_scenarios():
    """真实使用场景演示"""
    print("\n" + "=" * 60)
    print("真实使用场景")
    print("=" * 60)

    scenarios = [
        {
            "title": "场景1: 多语言电影",
            "description": "一部电影包含英语、日语、韩语字幕",
            "tracks": [
                ("轨道 0", "English", "en", "subrip", True, False),
                ("轨道 1", "日本語", "ja", "ass", False, False),
                ("轨道 2", "한국어", "ko", "subrip", False, False)
            ],
            "use_case": "用户只想翻译日语字幕到中文"
        },
        {
            "title": "场景2: 动漫视频",
            "description": "动漫视频包含对话字幕和歌词字幕",
            "tracks": [
                ("轨道 0", "Dialogue", "ja", "ass", True, False),
                ("轨道 1", "Signs & Songs", "ja", "ass", False, True),
                ("轨道 2", "English Dub", "en", "subrip", False, False)
            ],
            "use_case": "用户想分别翻译对话和歌词字幕"
        },
        {
            "title": "场景3: 学习材料",
            "description": "教学视频包含多种语言的字幕",
            "tracks": [
                ("轨道 0", "English", "en", "webvtt", True, False),
                ("轨道 1", "Français", "fr", "webvtt", False, False),
                ("轨道 2", "Deutsch", "de", "webvtt", False, False),
                ("轨道 3", "Español", "es", "webvtt", False, False)
            ],
            "use_case": "用户想把所有外语字幕都翻译成中文"
        }
    ]

    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print(f"描述: {scenario['description']}")
        print("字幕轨道:")

        for track, title, lang, codec, is_default, is_forced in scenario['tracks']:
            flags = []
            if is_default:
                flags.append("默认")
            if is_forced:
                flags.append("强制")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"  {track}: {title} ({lang}, {codec}){flag_str}")

        print(f"使用场景: {scenario['use_case']}")
        print()


def demo_cli_commands():
    """演示各种CLI命令"""
    print("=" * 60)
    print("CLI 命令示例")
    print("=" * 60)

    commands = [
        {
            "desc": "查看视频的详细信息（包括字幕轨道）",
            "cmd": "python src/cli.py --info movie.mp4"
        },
        {
            "desc": "列出视频中的所有字幕轨道",
            "cmd": "python src/cli.py --list-subtitles movie.mp4"
        },
        {
            "desc": "翻译第0个字幕轨道",
            "cmd": "python src/cli.py -i movie.mp4 --subtitle-index 0 -o output.srt -l zh-CN"
        },
        {
            "desc": "翻译第2个字幕轨道（日语）",
            "cmd": "python src/cli.py -i movie.mp4 --subtitle-index 2 -o japanese_sub.srt -l zh-CN"
        },
        {
            "desc": "翻译所有字幕轨道",
            "cmd": "python src/cli.py -i movie.mp4 --extract-all-subtitles --output-dir ./output -l zh-CN"
        },
        {
            "desc": "批量处理目录中的所有视频的第1个轨道",
            "cmd": "python src/cli.py --input-dir ./videos --subtitle-index 1 --output-dir ./output -l zh-CN"
        }
    ]

    for i, cmd_info in enumerate(commands, 1):
        print(f"{i}. {cmd_info['desc']}")
        print(f"   {cmd_info['cmd']}")
        print()


def main():
    """主演示函数"""
    print("视频翻译器 - 字幕轨道选择功能演示")
    print("Video Translator - Subtitle Track Selection Feature Demo")
    print("版本: 1.0.0")
    print()

    try:
        # CLI功能演示
        demo_cli_functionality()

        # GUI功能演示
        demo_gui_functionality()

        # 功能对比
        demo_feature_comparison()

        # 真实场景
        demo_real_world_scenarios()

        # CLI命令示例
        demo_cli_commands()

        print("\n" + "=" * 60)
        print("演示完成")
        print("=" * 60)
        print()
        print("要使用这些功能，请：")
        print("1. 对于GUI: 运行 python run.py")
        print("2. 对于CLI: 运行 python src/cli.py --help 查看所有选项")
        print("3. 查看具体视频的字幕轨道: python src/cli.py --list-subtitles <video_file>")

    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
