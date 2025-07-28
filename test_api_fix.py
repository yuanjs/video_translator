#!/usr/bin/env python3
"""
API修复验证测试脚本
Test script to verify the API fix for TranslationResult token_count issue
"""

import sys
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.translator import (
    TranslationResult,
    TranslationRequest,
    DeepSeekTranslator,
    OllamaTranslator,
    TranslationProvider,
    BaseTranslator
)
from src.utils.config import get_config


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

    print()


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

    print()


async def test_deepseek_translator():
    """测试 DeepSeek 翻译器的 token_usage 处理"""
    print("=" * 60)
    print("测试 DeepSeek 翻译器")
    print("=" * 60)

    try:
        # 创建模拟的 API 响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "你好世界"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 15
        mock_response.usage.prompt_tokens = 8
        mock_response.usage.completion_tokens = 7

        # 创建模拟的配置
        with patch('src.core.translator.get_config', return_value=get_config()):
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

        # 模拟 openai.OpenAI().chat.completions.create
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            # 执行翻译
            result = await translator.translate(request)

            # 验证结果
            assert result.original_text == "Hello world"
            assert result.translated_text == "你好世界"
            assert result.provider == "deepseek"
            assert result.token_usage is not None
            assert result.token_usage.get('total_tokens') == 15

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

    print()


async def test_ollama_translator():
    """测试 Ollama 翻译器的 token_usage 处理"""
    print("=" * 60)
    print("测试 Ollama 翻译器")
    print("=" * 60)

    try:
        # 创建模拟的 API 响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "你好世界"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 12

        # 创建模拟的配置
        with patch('src.core.translator.get_config', return_value=get_config()):
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

        # 模拟 openai.OpenAI().chat.completions.create
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response

            # 执行翻译
            result = await translator.translate(request)

            # 验证结果
            assert result.original_text == "Hello world"
            assert result.translated_text == "你好世界"
            assert result.provider == "ollama"
            assert result.token_usage is not None
            assert result.token_usage.get('total_tokens') == 12

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

    print()


async def test_error_handling():
    """测试错误处理情况下的 TranslationResult 创建"""
    print("=" * 60)
    print("测试错误处理")
    print("=" * 60)

    try:
        # 创建模拟的配置
        with patch('src.core.translator.get_config', return_value=get_config()):
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

        # 模拟 API 错误
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            # 执行翻译（应该返回错误结果）
            result = await translator.translate(request)

            # 验证错误结果
            assert result.original_text == "Hello world"
            assert result.translated_text == ""
            assert "API Error" in result.error  # 检查错误信息是否包含API Error
            assert result.provider == "deepseek"

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

    print()


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

    print()


async def main():
    """主测试函数"""
    print("🧪 API修复验证测试开始")
    print("目标：验证 TranslationResult token_count -> token_usage 修复")
    print()

    tests = [
        ("TranslationResult 基本创建", test_translation_result_creation()),
        ("拒绝旧参数 token_count", test_translation_result_old_params()),
        ("Token usage 访问方式", test_token_usage_access()),
        ("DeepSeek 翻译器", await test_deepseek_translator()),
        ("Ollama 翻译器", await test_ollama_translator()),
        ("错误处理", await test_error_handling()),
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
        print("🎉 所有测试通过！API修复成功！")
        return 0
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return 1


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
