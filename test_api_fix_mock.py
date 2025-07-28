#!/usr/bin/env python3
"""
API修复验证测试脚本（完全模拟版本）
Test script to verify the API fix for TranslationResult token_count issue using mocks
"""

import sys
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.translator import (
    TranslationResult,
    TranslationRequest,
    DeepSeekTranslator,
    OllamaTranslator,
    TranslationProvider
)


def test_translation_result_creation():
    """测试 TranslationResult 对象创建"""
    print("=" * 60)
    print("测试 TranslationResult 对象创建")
    print("=" * 60)

    try:
        # 测试基本创建
        result1 = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh-CN"
        )
        print("✅ 基本 TranslationResult 创建成功")

        # 测试带 token_usage 的创建
        result2 = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh-CN",
            token_usage={'total_tokens': 10, 'prompt_tokens': 5, 'completion_tokens': 5}
        )
        print("✅ 带 token_usage 的 TranslationResult 创建成功")
        print(f"   Token usage: {result2.token_usage}")

        # 测试所有参数的创建
        result3 = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh-CN",
            confidence=0.95,
            provider="deepseek",
            model="deepseek-chat",
            processing_time=1.23,
            token_usage={'total_tokens': 15},
            error=None
        )
        print("✅ 完整参数 TranslationResult 创建成功")
        print(f"   提供商: {result3.provider}")
        print(f"   模型: {result3.model}")
        print(f"   处理时间: {result3.processing_time}s")
        print(f"   Token usage: {result3.token_usage}")

        return True

    except Exception as e:
        print(f"❌ TranslationResult 创建失败: {e}")
        return False


def test_translation_result_old_params():
    """测试使用旧参数 token_count 应该失败"""
    print("=" * 60)
    print("测试旧参数 token_count (应该失败)")
    print("=" * 60)

    try:
        # 这应该失败，因为 token_count 不是有效参数
        result = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh-CN",
            token_count=10  # 这个参数不存在
        )
        print("❌ 意外成功：token_count 参数应该被拒绝")
        return False

    except TypeError as e:
        if "token_count" in str(e):
            print("✅ 正确拒绝了 token_count 参数")
            print(f"   错误信息: {e}")
            return True
        else:
            print(f"❌ 意外的错误类型: {e}")
            return False

    except Exception as e:
        print(f"❌ 意外的异常: {e}")
        return False


def test_token_usage_access():
    """测试 token_usage 的各种访问方式"""
    print("=" * 60)
    print("测试 token_usage 访问方式")
    print("=" * 60)

    try:
        # 创建带有详细 token 信息的结果
        result = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh-CN",
            token_usage={
                'total_tokens': 20,
                'prompt_tokens': 12,
                'completion_tokens': 8,
                'input_tokens': 12,  # Anthropic 格式
                'output_tokens': 8   # Anthropic 格式
            }
        )

        # 测试各种访问方式
        total_tokens = result.token_usage.get('total_tokens', 0)
        prompt_tokens = result.token_usage.get('prompt_tokens', 0)
        completion_tokens = result.token_usage.get('completion_tokens', 0)

        print("✅ Token usage 访问测试成功")
        print(f"   总 tokens: {total_tokens}")
        print(f"   输入 tokens: {prompt_tokens}")
        print(f"   输出 tokens: {completion_tokens}")

        # 测试兼容性：检查是否有 total_tokens
        if result.token_usage and result.token_usage.get('total_tokens'):
            print(f"   ✅ 兼容性检查通过: total_tokens = {result.token_usage.get('total_tokens')}")

        # 测试空值处理
        empty_result = TranslationResult(
            original_text="Test",
            translated_text="测试",
            source_language="en",
            target_language="zh-CN"
        )

        safe_tokens = empty_result.token_usage.get('total_tokens', 0) if empty_result.token_usage else 0
        print(f"   ✅ 空值处理: {safe_tokens}")

        return True

    except Exception as e:
        print(f"❌ Token usage 访问测试失败: {e}")
        return False


class MockConfig:
    """模拟配置类"""
    def get(self, key, default=None):
        defaults = {
            'translation.max_tokens': 2000,
            'translation.temperature': 0.3,
            'translation.timeout': 30,
            'api.deepseek.models': ['deepseek-chat'],
            'api.ollama.models': ['llama2'],
            'translation.model': 'deepseek-chat'
        }
        return defaults.get(key, default)

    def get_supported_languages(self):
        """模拟获取支持的语言列表"""
        return {
            'zh-CN': '简体中文',
            'en': 'English',
            'ja': '日本語',
            'ko': '한국어',
            'fr': 'Français',
            'de': 'Deutsch'
        }

    def get_api_key(self, provider):
        """模拟获取API密钥"""
        return "mock-api-key"

    def validate_api_config(self, provider):
        """模拟验证API配置"""
        return True


class MockResponse:
    """模拟API响应类"""
    def __init__(self, text="你好世界", total_tokens=15):
        self.choices = [Mock()]
        self.choices[0].message = Mock()
        self.choices[0].message.content = text
        self.usage = Mock()
        self.usage.total_tokens = total_tokens
        self.usage.prompt_tokens = total_tokens // 2
        self.usage.completion_tokens = total_tokens - (total_tokens // 2)


class MockOpenAI:
    """模拟OpenAI客户端类"""
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key
        self.base_url = base_url
        self.chat = Mock()
        self.chat.completions = Mock()
        self.chat.completions.create = self.create_completion

    def create_completion(self, model=None, messages=None, max_tokens=None, temperature=None, timeout=None):
        """模拟创建完成请求"""
        # 提取提示中的文本用于模拟翻译
        text = ""
        if messages and len(messages) > 0:
            text = messages[0].get('content', '')

        # 如果提示中包含 "Hello world"，返回 "你好世界"
        if "Hello world" in text:
            return MockResponse(text="你好世界", total_tokens=15)
        return MockResponse()


def test_deepseek_translator():
    """测试 DeepSeek 翻译器的 token_usage 处理"""
    print("=" * 60)
    print("测试 DeepSeek 翻译器")
    print("=" * 60)

    try:
        # 使用patch模拟配置和OpenAI客户端
        with patch('src.core.translator.get_config', return_value=MockConfig()):
            with patch('src.core.translator.openai.OpenAI', new=MockOpenAI):
                # 创建翻译器
                translator = DeepSeekTranslator(
                    provider=TranslationProvider.DEEPSEEK,
                    api_key="test-key"
                )

                # 创建翻译请求
                request = TranslationRequest(
                    text="Hello world",
                    source_language="en",
                    target_language="zh-CN"
                )

                # 执行翻译
                result = asyncio.run(translator.translate(request))

                # 验证结果
                if result.original_text != "Hello world":
                    raise AssertionError(f"原文不匹配: {result.original_text}")

                if result.translated_text != "你好世界":
                    raise AssertionError(f"译文不匹配: {result.translated_text}")

                if result.provider != "deepseek":
                    raise AssertionError(f"提供商不匹配: {result.provider}")

                if not result.token_usage:
                    raise AssertionError("token_usage为空")

                if result.token_usage.get('total_tokens') != 15:
                    raise AssertionError(f"total_tokens不匹配: {result.token_usage.get('total_tokens')}")

                print("✅ DeepSeek 翻译器测试成功")
                print(f"   原文: {result.original_text}")
                print(f"   译文: {result.translated_text}")
                print(f"   提供商: {result.provider}")
                print(f"   Token usage: {result.token_usage}")

        return True

    except Exception as e:
        print(f"❌ DeepSeek 翻译器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ollama_translator():
    """测试 Ollama 翻译器的 token_usage 处理"""
    print("=" * 60)
    print("测试 Ollama 翻译器")
    print("=" * 60)

    try:
        # 使用patch模拟配置和OpenAI客户端
        with patch('src.core.translator.get_config', return_value=MockConfig()):
            with patch('src.core.translator.openai.OpenAI', new=MockOpenAI):
                # 创建翻译器
                translator = OllamaTranslator(
                    provider=TranslationProvider.OLLAMA,
                    api_key="not-needed"
                )

                # 创建翻译请求
                request = TranslationRequest(
                    text="Hello world",
                    source_language="en",
                    target_language="zh-CN"
                )

                # 执行翻译
                result = asyncio.run(translator.translate(request))

                # 验证结果
                if result.original_text != "Hello world":
                    raise AssertionError(f"原文不匹配: {result.original_text}")

                if result.translated_text != "你好世界":
                    raise AssertionError(f"译文不匹配: {result.translated_text}")

                if result.provider != "ollama":
                    raise AssertionError(f"提供商不匹配: {result.provider}")

                if not result.token_usage:
                    raise AssertionError("token_usage为空")

                if result.token_usage.get('total_tokens') != 15:
                    raise AssertionError(f"total_tokens不匹配: {result.token_usage.get('total_tokens')}")

                print("✅ Ollama 翻译器测试成功")
                print(f"   原文: {result.original_text}")
                print(f"   译文: {result.translated_text}")
                print(f"   提供商: {result.provider}")
                print(f"   Token usage: {result.token_usage}")

        return True

    except Exception as e:
        print(f"❌ Ollama 翻译器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


class ErrorMockOpenAI:
    """模拟出错的OpenAI客户端类"""
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key
        self.base_url = base_url
        self.chat = Mock()
        self.chat.completions = Mock()
        self.chat.completions.create = self.create_completion

    def create_completion(self, model=None, messages=None, max_tokens=None, temperature=None, timeout=None):
        """模拟API错误"""
        # 确保错误信息包含 "API Error"
        raise Exception("API Error: 模拟API调用失败")


def test_error_handling():
    """测试错误处理情况下的 TranslationResult 创建"""
    print("=" * 60)
    print("测试错误处理")
    print("=" * 60)

    try:
        # 使用patch模拟配置和出错的OpenAI客户端
        with patch('src.core.translator.get_config', return_value=MockConfig()):
            with patch('src.core.translator.openai.OpenAI', new=ErrorMockOpenAI):
                # 创建翻译器
                translator = DeepSeekTranslator(
                    provider=TranslationProvider.DEEPSEEK,
                    api_key="test-key"
                )

                # 创建翻译请求
                request = TranslationRequest(
                    text="Hello world",
                    source_language="en",
                    target_language="zh-CN"
                )

                # 执行翻译（应该返回错误结果）
                result = asyncio.run(translator.translate(request))

                # 验证错误结果
                if result.original_text != "Hello world":
                    raise AssertionError(f"原文不匹配: {result.original_text}")

                if result.translated_text != "":
                    raise AssertionError(f"错误时译文应为空: {result.translated_text}")

                if "API Error" not in result.error:
                    raise AssertionError(f"错误信息不包含'API Error': {result.error}")

                if result.provider != "deepseek":
                    raise AssertionError(f"提供商不匹配: {result.provider}")

                print("✅ 错误处理测试成功")
                print(f"   原文: {result.original_text}")
                print(f"   译文: {result.translated_text}")
                print(f"   错误: {result.error}")
                print(f"   提供商: {result.provider}")

        return True

    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🧪 API修复验证测试开始 (完全模拟版本)")
    print("目标：验证 TranslationResult token_count -> token_usage 修复")
    print()

    tests = [
        ("TranslationResult 基本创建", test_translation_result_creation()),
        ("拒绝旧参数 token_count", test_translation_result_old_params()),
        ("Token usage 访问方式", test_token_usage_access()),
        ("DeepSeek 翻译器", test_deepseek_translator()),
        ("Ollama 翻译器", test_ollama_translator()),
        ("错误处理", test_error_handling()),
    ]

    passed = 0
    total = len(tests)

    for test_name, result in tests:
        if result:
            passed += 1
            print(f"✅ {test_name}: 通过")
        else:
            print(f"❌ {test_name}: 失败")

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")

    if passed == total:
        print("""
==================================================
🎉 所有测试通过！API修复成功！
==================================================

修复总结:
- ✅ TranslationResult 不再接受 token_count 参数
- ✅ 使用 token_usage 字典存储token信息
- ✅ 兼容各种访问模式
- ✅ DeepSeek和Ollama翻译器现在使用正确的参数
""")
        return 0
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        sys.exit(1)
