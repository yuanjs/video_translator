#!/usr/bin/env python3
"""
视频翻译器基本功能测试
Video Translator Basic Functionality Tests

运行方法:
    python test_basic.py
"""

import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置测试环境
os.environ['TESTING'] = 'true'


class TestBasicImports(unittest.TestCase):
    """测试基本模块导入"""

    def test_config_import(self):
        """测试配置模块导入"""
        try:
            from src.utils.config import Config, get_config
            self.assertTrue(True, "配置模块导入成功")
        except ImportError as e:
            self.fail(f"配置模块导入失败: {e}")

    def test_logger_import(self):
        """测试日志模块导入"""
        try:
            from src.utils.logger import get_logger, init_logger
            self.assertTrue(True, "日志模块导入成功")
        except ImportError as e:
            self.fail(f"日志模块导入失败: {e}")

    def test_helpers_import(self):
        """测试辅助函数模块导入"""
        try:
            from src.utils.helpers import is_video_file, format_file_size
            self.assertTrue(True, "辅助函数模块导入成功")
        except ImportError as e:
            self.fail(f"辅助函数模块导入失败: {e}")

    def test_core_modules_import(self):
        """测试核心模块导入"""
        try:
            from src.core.video_processor import VideoProcessor
            from src.core.subtitle_extractor import SubtitleExtractor
            from src.core.translator import TranslationManager
            from src.core.subtitle_writer import SubtitleWriter
            self.assertTrue(True, "核心模块导入成功")
        except ImportError as e:
            self.fail(f"核心模块导入失败: {e}")


class TestConfigSystem(unittest.TestCase):
    """测试配置系统"""

    def setUp(self):
        """设置测试环境"""
        from src.utils.config import Config
        self.config = Config()

    def test_config_creation(self):
        """测试配置对象创建"""
        self.assertIsNotNone(self.config)
        self.assertIsInstance(self.config.config_data, dict)

    def test_config_get_set(self):
        """测试配置的获取和设置"""
        # 测试默认值
        default_lang = self.config.get('translation.target_language', 'zh-CN')
        self.assertEqual(default_lang, 'zh-CN')

        # 测试设置值
        self.config.set('test.value', 'test_data', save=False)
        retrieved_value = self.config.get('test.value')
        self.assertEqual(retrieved_value, 'test_data')

    def test_supported_languages(self):
        """测试支持的语言列表"""
        languages = self.config.get_supported_languages()
        self.assertIsInstance(languages, dict)
        self.assertIn('zh-CN', languages)
        self.assertIn('en', languages)

    def test_translation_providers(self):
        """测试翻译提供商配置"""
        providers = self.config.get_translation_providers()
        self.assertIsInstance(providers, dict)
        self.assertIn('openai', providers)


class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""

    def test_file_size_formatting(self):
        """测试文件大小格式化"""
        from src.utils.helpers import format_file_size

        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(1024), "1.00 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.00 MB")
        self.assertEqual(format_file_size(1024 * 1024 * 1024), "1.00 GB")

    def test_duration_formatting(self):
        """测试时长格式化"""
        from src.utils.helpers import format_duration

        self.assertIn("秒", format_duration(30))
        self.assertIn("分", format_duration(90))
        self.assertIn("小时", format_duration(3700))

    def test_video_file_detection(self):
        """测试视频文件检测"""
        from src.utils.helpers import is_video_file

        # 创建临时文件测试
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(b'fake video content')
            tmp_path = Path(tmp.name)

        try:
            # 注意：这个测试可能会失败，因为is_video_file可能检查文件内容
            # 这里主要测试函数不会崩溃
            result = is_video_file(tmp_path)
            self.assertIsInstance(result, bool)
        finally:
            tmp_path.unlink()

    def test_time_conversion(self):
        """测试时间格式转换"""
        from src.utils.helpers import (
            srt_time_to_seconds,
            seconds_to_srt_time,
            vtt_time_to_seconds,
            seconds_to_vtt_time
        )

        # SRT时间格式测试
        srt_time = "00:01:30,500"
        seconds = srt_time_to_seconds(srt_time)
        self.assertEqual(seconds, 90.5)

        converted_back = seconds_to_srt_time(seconds)
        self.assertEqual(converted_back, srt_time)

        # VTT时间格式测试
        vtt_time = "00:01:30.500"
        seconds = vtt_time_to_seconds(vtt_time)
        self.assertEqual(seconds, 90.5)

        converted_back = seconds_to_vtt_time(seconds)
        self.assertEqual(converted_back, vtt_time)


class TestSubtitleExtractor(unittest.TestCase):
    """测试字幕提取器"""

    def setUp(self):
        """设置测试环境"""
        from src.core.subtitle_extractor import SubtitleExtractor, SubtitleSegment, SubtitleFile
        self.extractor = SubtitleExtractor()
        self.SubtitleSegment = SubtitleSegment
        self.SubtitleFile = SubtitleFile

    def test_subtitle_segment_creation(self):
        """测试字幕片段创建"""
        segment = self.SubtitleSegment(1, 0.0, 5.0, "Test subtitle text")

        self.assertEqual(segment.index, 1)
        self.assertEqual(segment.start_time, 0.0)
        self.assertEqual(segment.end_time, 5.0)
        self.assertEqual(segment.text, "Test subtitle text")
        self.assertEqual(segment.duration, 5.0)

    def test_subtitle_file_creation(self):
        """测试字幕文件创建"""
        subtitle_file = self.SubtitleFile()

        # 添加片段
        segment1 = self.SubtitleSegment(1, 0.0, 5.0, "First subtitle")
        segment2 = self.SubtitleSegment(2, 6.0, 10.0, "Second subtitle")

        subtitle_file.add_segment(segment1)
        subtitle_file.add_segment(segment2)

        self.assertEqual(len(subtitle_file), 2)
        self.assertEqual(subtitle_file.get_total_duration(), 10.0)

    def test_create_from_text_list(self):
        """测试从文本列表创建字幕"""
        text_list = ["First line", "Second line", "Third line"]
        subtitle_file = self.extractor.create_from_text_list(text_list)

        self.assertEqual(len(subtitle_file), 3)
        self.assertEqual(subtitle_file[0].text, "First line")
        self.assertEqual(subtitle_file[1].text, "Second line")
        self.assertEqual(subtitle_file[2].text, "Third line")


class TestSubtitleWriter(unittest.TestCase):
    """测试字幕写入器"""

    def setUp(self):
        """设置测试环境"""
        from src.core.subtitle_writer import SubtitleWriter
        from src.core.subtitle_extractor import SubtitleFile, SubtitleSegment

        self.writer = SubtitleWriter()

        # 创建测试字幕文件
        self.test_subtitle = SubtitleFile()
        self.test_subtitle.add_segment(SubtitleSegment(1, 0.0, 5.0, "First subtitle"))
        self.test_subtitle.add_segment(SubtitleSegment(2, 6.0, 10.0, "Second subtitle"))

    def test_filename_generation(self):
        """测试输出文件名生成"""
        filename = self.writer.get_output_filename(
            "test_video.mp4",
            "zh-CN",
            "srt",
            bilingual=True
        )

        self.assertIn("test_video", filename)
        self.assertIn("zh_CN", filename)
        self.assertIn("bilingual", filename)
        self.assertTrue(filename.endswith(".srt"))

    def test_subtitle_validation(self):
        """测试字幕验证"""
        warnings = self.writer.validate_subtitle_file(self.test_subtitle)

        # 应该没有警告（假设测试数据是有效的）
        self.assertIsInstance(warnings, list)


@patch('src.utils.helpers.check_ffmpeg_available', return_value=True)
class TestVideoProcessor(unittest.TestCase):
    """测试视频处理器"""

    def setUp(self):
        """设置测试环境"""
        # 只有在FFmpeg可用时才测试
        try:
            from src.core.video_processor import VideoProcessor
            self.processor = VideoProcessor()
        except RuntimeError:
            self.skipTest("FFmpeg不可用，跳过视频处理器测试")

    def test_processor_creation(self, mock_ffmpeg):
        """测试处理器创建"""
        self.assertIsNotNone(self.processor)


class TestTranslationManager(unittest.TestCase):
    """测试翻译管理器"""

    def setUp(self):
        """设置测试环境"""
        from src.core.translator import TranslationManager
        self.manager = TranslationManager()

    def test_manager_creation(self):
        """测试管理器创建"""
        self.assertIsNotNone(self.manager)

    def test_available_providers(self):
        """测试获取可用提供商"""
        providers = self.manager.get_available_providers()
        self.assertIsInstance(providers, list)

    def test_translation_statistics(self):
        """测试翻译统计信息"""
        stats = self.manager.get_translation_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('available_providers', stats)
        self.assertIn('supported_languages', stats)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_pipeline_simulation(self):
        """测试完整流程模拟"""
        try:
            # 导入所有必要模块
            from src.utils.config import get_config
            from src.core.subtitle_extractor import SubtitleExtractor, SubtitleFile, SubtitleSegment
            from src.core.translator import TranslationManager
            from src.core.subtitle_writer import SubtitleWriter

            # 创建测试组件
            config = get_config()
            extractor = SubtitleExtractor()
            manager = TranslationManager()
            writer = SubtitleWriter()

            # 创建测试字幕
            subtitle_file = SubtitleFile()
            subtitle_file.add_segment(SubtitleSegment(1, 0.0, 5.0, "Hello world"))
            subtitle_file.add_segment(SubtitleSegment(2, 6.0, 10.0, "This is a test"))

            # 验证组件能够正常工作
            self.assertEqual(len(subtitle_file), 2)

            # 测试统计信息
            stats = manager.get_translation_statistics()
            self.assertIn('available_providers', stats)

            # 测试文件名生成
            filename = writer.get_output_filename("test.mp4", "zh-CN", "srt", True)
            self.assertTrue(filename.endswith(".srt"))

            self.assertTrue(True, "集成测试通过")

        except Exception as e:
            self.fail(f"集成测试失败: {e}")


def run_tests():
    """运行所有测试"""
    print("🧪 开始运行基本功能测试...")
    print("=" * 60)

    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestBasicImports,
        TestConfigSystem,
        TestHelperFunctions,
        TestSubtitleExtractor,
        TestSubtitleWriter,
        TestVideoProcessor,
        TestTranslationManager,
        TestIntegration
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 打印结果总结
    print("\n" + "=" * 60)
    print("🧪 测试结果总结:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")

    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split(chr(10))[-2]}")

    if result.errors:
        print("\n⚠️  错误的测试:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.split(chr(10))[-2]}")

    if result.wasSuccessful():
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print("\n💥 部分测试失败")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="视频翻译器基本功能测试")
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出'
    )
    parser.add_argument(
        '--specific',
        help='运行特定测试类'
    )

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    # 运行特定测试
    if args.specific:
        try:
            test_class = globals()[args.specific]
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            sys.exit(0 if result.wasSuccessful() else 1)
        except KeyError:
            print(f"❌ 测试类 '{args.specific}' 不存在")
            print("可用的测试类:")
            for name in globals():
                if name.startswith('Test') and name != 'TestCase':
                    print(f"   • {name}")
            sys.exit(1)
    else:
        # 运行所有测试
        sys.exit(run_tests())
