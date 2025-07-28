#!/usr/bin/env python3
"""
新增AI平台演示脚本
Demo Script for New AI Platforms (DeepSeek & Ollama)

展示如何使用DeepSeek和Ollama进行视频字幕翻译
Demonstrates how to use DeepSeek and Ollama for video subtitle translation
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from core.translator import (
        TranslationManager,
        TranslationProvider,
        TranslationRequest,
        DeepSeekTranslator,
        OllamaTranslator
    )
    from utils.config import get_config
    from utils.logger import get_logger
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)

logger = get_logger(__name__)

class NewPlatformsDemo:
    """新AI平台演示类"""

    def __init__(self):
        self.config = get_config()
        self.manager = TranslationManager()

        # 演示文本
        self.demo_texts = {
            'english': {
                'text': "Hello world! Welcome to our video translation service. This is a test message.",
                'context': "Video subtitle translation demo"
            },
            'technical': {
                'text': "The application uses FFmpeg for video processing and supports multiple subtitle formats including SRT, VTT, and ASS.",
                'context': "Technical documentation"
            },
            'casual': {
                'text': "Hey there! Thanks for watching this video. Don't forget to like and subscribe!",
                'context': "YouTube video content"
            }
        }

    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}")

    def print_result(self, provider: str, result, start_time: float):
        """打印翻译结果"""
        duration = time.time() - start_time

        print(f"\n🤖 提供商: {provider.upper()}")
        print(f"📝 原文: {result.original_text}")
        print(f"🔤 译文: {result.translated_text}")
        print(f"⚡ 处理时间: {duration:.2f}秒")
        print(f"🔧 使用模型: {result.model}")

        if result.token_count:
            print(f"🪙 Token消耗: {result.token_count}")

        if result.error:
            print(f"❌ 错误: {result.error}")

        print("-" * 60)

    async def demo_deepseek(self):
        """演示DeepSeek翻译"""
        self.print_header("🧠 DeepSeek AI 翻译演示")

        print("DeepSeek特点:")
        print("✅ 高性价比的AI翻译服务")
        print("✅ 支持中文优化的模型")
        print("✅ 快速响应和高质量翻译")
        print("✅ 支持deepseek-chat和deepseek-coder模型")

        if TranslationProvider.DEEPSEEK not in self.manager.translators:
            print("\n❌ DeepSeek未配置或不可用")
            print("请设置DEEPSEEK_API_KEY环境变量或在api_keys.yaml中配置")
            print("获取API密钥: https://platform.deepseek.com/api_keys")
            return

        print(f"\n🚀 开始DeepSeek翻译演示...")

        for demo_name, demo_data in self.demo_texts.items():
            print(f"\n📋 演示场景: {demo_name}")

            request = TranslationRequest(
                text=demo_data['text'],
                target_language="zh-CN",
                context=demo_data['context']
            )

            start_time = time.time()
            try:
                result = await self.manager.translate_text(
                    text=request.text,
                    target_language=request.target_language,
                    provider=TranslationProvider.DEEPSEEK
                )
                self.print_result("DeepSeek", result, start_time)

            except Exception as e:
                print(f"❌ DeepSeek翻译失败: {e}")

    async def demo_ollama(self):
        """演示Ollama翻译"""
        self.print_header("🏠 Ollama 本地AI翻译演示")

        print("Ollama特点:")
        print("✅ 完全本地部署，无需API密钥")
        print("✅ 数据隐私保护，不上传到云端")
        print("✅ 支持多种开源模型")
        print("✅ 一次安装，永久免费使用")

        if TranslationProvider.OLLAMA not in self.manager.translators:
            print("\n❌ Ollama未配置或服务未运行")
            print("请确保:")
            print("1. 已安装Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("2. 已启动服务: ollama serve")
            print("3. 已安装模型: ollama pull llama2")
            return

        print(f"\n🚀 开始Ollama翻译演示...")
        print("注意: 本地模型可能需要更长时间处理")

        for demo_name, demo_data in self.demo_texts.items():
            print(f"\n📋 演示场景: {demo_name}")

            request = TranslationRequest(
                text=demo_data['text'],
                target_language="zh-CN",
                context=demo_data['context']
            )

            start_time = time.time()
            try:
                result = await self.manager.translate_text(
                    text=request.text,
                    target_language=request.target_language,
                    provider=TranslationProvider.OLLAMA
                )
                self.print_result("Ollama", result, start_time)

            except Exception as e:
                print(f"❌ Ollama翻译失败: {e}")

    async def compare_platforms(self):
        """对比不同平台的翻译效果"""
        self.print_header("⚖️ 平台翻译效果对比")

        test_text = "Artificial intelligence is revolutionizing the way we process and understand multimedia content."

        print(f"测试文本: {test_text}")
        print(f"目标语言: 简体中文")

        available_providers = []

        # 检查可用的新平台
        if TranslationProvider.DEEPSEEK in self.manager.translators:
            available_providers.append(TranslationProvider.DEEPSEEK)

        if TranslationProvider.OLLAMA in self.manager.translators:
            available_providers.append(TranslationProvider.OLLAMA)

        # 添加传统平台进行对比
        if TranslationProvider.OPENAI in self.manager.translators:
            available_providers.append(TranslationProvider.OPENAI)

        if not available_providers:
            print("❌ 没有可用的翻译平台")
            return

        results = {}

        for provider in available_providers:
            print(f"\n🧪 测试 {provider.value.upper()}...")

            start_time = time.time()
            try:
                result = await self.manager.translate_text(
                    text=test_text,
                    target_language="zh-CN",
                    provider=provider
                )

                results[provider.value] = {
                    'translation': result.translated_text,
                    'time': time.time() - start_time,
                    'model': result.model,
                    'tokens': result.token_count,
                    'error': result.error
                }

                print(f"✅ 完成 ({results[provider.value]['time']:.2f}s)")

            except Exception as e:
                results[provider.value] = {
                    'translation': None,
                    'time': 0,
                    'model': 'unknown',
                    'tokens': 0,
                    'error': str(e)
                }
                print(f"❌ 失败: {e}")

        # 显示对比结果
        print(f"\n📊 翻译结果对比:")
        print("-" * 80)

        for provider, data in results.items():
            print(f"\n🤖 {provider.upper()}:")
            if data['translation']:
                print(f"   译文: {data['translation']}")
                print(f"   用时: {data['time']:.2f}秒")
                print(f"   模型: {data['model']}")
                if data['tokens']:
                    print(f"   Token: {data['tokens']}")
            else:
                print(f"   ❌ 翻译失败: {data['error']}")

    def show_configuration_guide(self):
        """显示配置指南"""
        self.print_header("🔧 配置指南")

        print("要使用新的AI平台，请按照以下步骤配置:\n")

        print("📱 DeepSeek 配置:")
        print("1. 访问 https://platform.deepseek.com/api_keys")
        print("2. 注册并获取API密钥")
        print("3. 设置环境变量或配置文件:")
        print("   环境变量: export DEEPSEEK_API_KEY='your-key'")
        print("   配置文件: 在 api_keys.yaml 中添加 deepseek 配置")

        print("\n🏠 Ollama 配置:")
        print("1. 安装Ollama:")
        print("   Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh")
        print("   Windows: 下载 https://ollama.ai/download/windows")
        print("2. 启动服务: ollama serve")
        print("3. 安装模型: ollama pull llama2")
        print("4. 验证安装: ollama list")

        print("\n🧪 快速测试:")
        print("   python test_providers.py deepseek")
        print("   python test_providers.py ollama")
        print("   python setup_platforms.py  # 交互式配置")

    async def run_demo(self):
        """运行完整演示"""
        print("🎬 视频翻译器 - 新AI平台演示")
        print("=" * 60)
        print("本演示将展示DeepSeek和Ollama两个新增AI平台的翻译功能")

        # 检查配置状态
        deepseek_available = TranslationProvider.DEEPSEEK in self.manager.translators
        ollama_available = TranslationProvider.OLLAMA in self.manager.translators

        print(f"\n📋 平台状态:")
        print(f"   DeepSeek: {'✅ 可用' if deepseek_available else '❌ 未配置'}")
        print(f"   Ollama:   {'✅ 可用' if ollama_available else '❌ 未配置'}")

        if not deepseek_available and not ollama_available:
            print(f"\n⚠️  没有可用的新平台，将显示配置指南")
            self.show_configuration_guide()
            return

        # 运行演示
        if deepseek_available:
            await self.demo_deepseek()

        if ollama_available:
            await self.demo_ollama()

        if deepseek_available or ollama_available:
            await self.compare_platforms()

        # 总结
        self.print_header("🎉 演示完成")
        print("通过本演示，您了解了:")
        print("✅ DeepSeek: 高性价比的云端AI翻译")
        print("✅ Ollama: 隐私保护的本地AI翻译")
        print("✅ 不同平台的性能和质量对比")

        print(f"\n📚 进一步学习:")
        print("- 查看 README.md 了解详细配置")
        print("- 运行 python test_providers.py 进行完整测试")
        print("- 使用 python run.py 启动图形界面")

        if not deepseek_available or not ollama_available:
            print(f"\n🔧 配置其他平台:")
            print("- 运行 python setup_platforms.py 进行交互式配置")

def main():
    """主函数"""
    demo = NewPlatformsDemo()

    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()

            if command == 'deepseek':
                asyncio.run(demo.demo_deepseek())
            elif command == 'ollama':
                asyncio.run(demo.demo_ollama())
            elif command == 'compare':
                asyncio.run(demo.compare_platforms())
            elif command == 'config':
                demo.show_configuration_guide()
            else:
                print("用法: python demo_new_platforms.py [deepseek|ollama|compare|config]")
                print("或直接运行查看完整演示")
        else:
            # 运行完整演示
            asyncio.run(demo.run_demo())

    except KeyboardInterrupt:
        print(f"\n\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n💥 演示过程中发生错误: {e}")
        print("请检查配置和依赖是否正确安装")

if __name__ == "__main__":
    main()
