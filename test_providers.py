#!/usr/bin/env python3
"""
翻译提供商测试脚本
Test script for translation providers including new DeepSeek and Ollama support
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from core.translator import (
    TranslationManager,
    TranslationProvider,
    TranslationRequest,
    OpenAITranslator,
    AnthropicTranslator,
    DeepSeekTranslator,
    OllamaTranslator
)
from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)

class ProviderTester:
    """翻译提供商测试器"""

    def __init__(self):
        self.config = get_config()
        self.manager = TranslationManager()
        self.test_text = "Hello, world! This is a test for translation."
        self.target_language = "zh-CN"

    async def test_all_providers(self):
        """测试所有提供商"""
        print("🧪 开始测试翻译提供商...")
        print("=" * 60)

        results = {}

        # 测试每个提供商
        for provider in TranslationProvider:
            print(f"\n📡 测试 {provider.value.upper()} 提供商...")
            result = await self.test_provider(provider)
            results[provider.value] = result

        # 打印测试结果摘要
        self.print_summary(results)

    async def test_provider(self, provider: TranslationProvider):
        """测试单个提供商"""
        try:
            # 检查提供商是否可用
            if provider not in self.manager.translators:
                print(f"❌ {provider.value} 未配置或初始化失败")
                return {
                    'status': 'not_configured',
                    'error': '未配置API密钥或初始化失败'
                }

            # 创建翻译请求
            request = TranslationRequest(
                text=self.test_text,
                target_language=self.target_language,
                context="这是一个测试翻译"
            )

            print(f"📝 原文: {self.test_text}")
            print(f"🎯 目标语言: {self.target_language}")

            # 执行翻译
            result = await self.manager.translate_text(
                text=self.test_text,
                target_language=self.target_language,
                provider=provider
            )

            if result.error:
                print(f"❌ 翻译失败: {result.error}")
                return {
                    'status': 'error',
                    'error': result.error,
                    'processing_time': result.processing_time
                }
            else:
                print(f"✅ 翻译成功!")
                print(f"📄 译文: {result.translated_text}")
                print(f"🕒 处理时间: {result.processing_time:.2f}秒")
                print(f"🔧 使用模型: {result.model}")
                if result.token_count:
                    print(f"🪙 Token数量: {result.token_count}")

                return {
                    'status': 'success',
                    'translated_text': result.translated_text,
                    'processing_time': result.processing_time,
                    'model': result.model,
                    'token_count': result.token_count
                }

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return {
                'status': 'exception',
                'error': str(e)
            }

    def print_summary(self, results):
        """打印测试结果摘要"""
        print("\n" + "=" * 60)
        print("📊 测试结果摘要")
        print("=" * 60)

        successful = 0
        failed = 0
        not_configured = 0

        for provider, result in results.items():
            status_icon = {
                'success': '✅',
                'error': '❌',
                'exception': '💥',
                'not_configured': '⚙️'
            }.get(result['status'], '❓')

            print(f"{status_icon} {provider.upper()}: {result['status']}")

            if result['status'] == 'success':
                successful += 1
                print(f"   └─ 处理时间: {result['processing_time']:.2f}s")
                print(f"   └─ 模型: {result['model']}")
            elif result['status'] in ['error', 'exception']:
                failed += 1
                print(f"   └─ 错误: {result['error']}")
            elif result['status'] == 'not_configured':
                not_configured += 1

        print(f"\n📈 统计:")
        print(f"   ✅ 成功: {successful}")
        print(f"   ❌ 失败: {failed}")
        print(f"   ⚙️ 未配置: {not_configured}")
        print(f"   📊 总计: {len(results)}")

    def check_configurations(self):
        """检查配置状态"""
        print("🔍 检查配置状态...")
        print("-" * 40)

        providers_info = {
            'openai': {
                'name': 'OpenAI',
                'key_env': 'OPENAI_API_KEY',
                'required': True
            },
            'anthropic': {
                'name': 'Anthropic Claude',
                'key_env': 'ANTHROPIC_API_KEY',
                'required': True
            },
            'google': {
                'name': 'Google Cloud',
                'key_env': 'GOOGLE_APPLICATION_CREDENTIALS',
                'required': True
            },
            'azure': {
                'name': 'Azure Translator',
                'key_env': 'AZURE_TRANSLATOR_KEY',
                'required': True
            },
            'deepseek': {
                'name': 'DeepSeek',
                'key_env': 'DEEPSEEK_API_KEY',
                'required': True
            },
            'ollama': {
                'name': 'Ollama (本地)',
                'key_env': 'OLLAMA_BASE_URL',
                'required': False
            }
        }

        for provider_key, info in providers_info.items():
            api_key = self.config.get_api_key(provider_key)
            status = "✅ 已配置" if api_key else ("⚙️ 未配置" if info['required'] else "✅ 无需配置")

            print(f"{info['name']:20} {status}")
            if info['required'] and not api_key:
                print(f"                     └─ 设置环境变量: {info['key_env']}")

        print()

    async def test_specific_provider(self, provider_name: str):
        """测试特定提供商"""
        try:
            provider = TranslationProvider(provider_name.lower())
            print(f"🧪 测试 {provider_name.upper()} 提供商...")
            print("-" * 40)

            result = await self.test_provider(provider)

            if result['status'] == 'success':
                print(f"\n🎉 {provider_name.upper()} 测试成功!")
            else:
                print(f"\n💥 {provider_name.upper()} 测试失败: {result.get('error', '未知错误')}")

        except ValueError:
            print(f"❌ 未知的提供商: {provider_name}")
            print("支持的提供商: openai, anthropic, google, azure, deepseek, ollama")

def print_usage():
    """打印使用说明"""
    print("""
🚀 翻译提供商测试脚本使用说明

用法:
    python test_providers.py [选项]

选项:
    无参数        - 测试所有配置的提供商
    check         - 检查配置状态
    <provider>    - 测试特定提供商

支持的提供商:
    • openai      - OpenAI GPT模型
    • anthropic   - Anthropic Claude模型
    • google      - Google Cloud Translation
    • azure       - Azure Translator
    • deepseek    - DeepSeek模型 (新增)
    • ollama      - Ollama本地模型 (新增)

示例:
    python test_providers.py                # 测试所有提供商
    python test_providers.py check          # 检查配置
    python test_providers.py deepseek       # 测试DeepSeek
    python test_providers.py ollama         # 测试Ollama

注意事项:
    • 确保已正确配置API密钥
    • Ollama需要本地服务运行在 http://localhost:11434
    • 某些提供商可能需要特殊的网络访问
""")

async def main():
    """主函数"""
    tester = ProviderTester()

    if len(sys.argv) == 1:
        # 无参数，测试所有提供商
        tester.check_configurations()
        await tester.test_all_providers()
    elif len(sys.argv) == 2:
        command = sys.argv[1].lower()

        if command == 'help' or command == '-h' or command == '--help':
            print_usage()
        elif command == 'check':
            tester.check_configurations()
        else:
            # 测试特定提供商
            await tester.test_specific_provider(command)
    else:
        print("❌ 参数错误")
        print_usage()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        sys.exit(1)
