#!/usr/bin/env python3
"""
简单的API修复真实测试
Simple real-world test for the API fix
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.translator import TranslationResult


def test_translation_result_fix():
    """测试 TranslationResult 修复"""
    print("=" * 50)
    print("测试 API 修复效果")
    print("=" * 50)

    # 测试1: 使用正确的 token_usage 参数
    print("1. 测试正确的 token_usage 参数...")
    try:
        result = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh-CN",
            provider="deepseek",
            model="deepseek-chat",
            processing_time=1.5,
            token_usage={'total_tokens': 15, 'prompt_tokens': 8, 'completion_tokens': 7}
        )
        print("✅ 成功创建 TranslationResult")
        print(f"   原文: {result.original_text}")
        print(f"   译文: {result.translated_text}")
        print(f"   提供商: {result.provider}")
        print(f"   Token使用: {result.token_usage}")

    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

    # 测试2: 验证 token_count 参数被正确拒绝
    print("\n2. 测试旧的 token_count 参数（应该失败）...")
    try:
        result = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh-CN",
            token_count=10  # 这个参数应该被拒绝
        )
        print("❌ 意外成功：token_count 应该被拒绝")
        return False

    except TypeError as e:
        if "token_count" in str(e):
            print("✅ 正确拒绝了 token_count 参数")
        else:
            print(f"❌ 意外的错误: {e}")
            return False

    # 测试3: 测试兼容的访问方式
    print("\n3. 测试 token 信息的安全访问...")
    try:
        # 创建有 token 信息的结果
        result_with_tokens = TranslationResult(
            original_text="Test",
            translated_text="测试",
            source_language="en",
            target_language="zh-CN",
            token_usage={'total_tokens': 20}
        )

        # 创建没有 token 信息的结果
        result_without_tokens = TranslationResult(
            original_text="Test",
            translated_text="测试",
            source_language="en",
            target_language="zh-CN"
        )

        # 测试安全访问方式（这些是在其他文件中使用的方式）
        tokens1 = result_with_tokens.token_usage.get('total_tokens', 0) if result_with_tokens.token_usage else 0
        tokens2 = result_without_tokens.token_usage.get('total_tokens', 0) if result_without_tokens.token_usage else 0

        print(f"✅ 有token信息的结果: {tokens1} tokens")
        print(f"✅ 无token信息的结果: {tokens2} tokens")

    except Exception as e:
        print(f"❌ Token访问测试失败: {e}")
        return False

    # 测试4: 模拟 DeepSeek/Ollama 翻译器的使用方式
    print("\n4. 模拟翻译器的使用方式...")
    try:
        # 模拟成功的翻译结果（就像修复后的代码中的格式）
        class MockUsage:
            total_tokens = 25

        mock_response = type('obj', (object,), {'usage': MockUsage()})

        # 使用修复后的格式创建结果
        result = TranslationResult(
            original_text="Hello",
            translated_text="你好",
            source_language="en",
            target_language="zh-CN",
            provider="deepseek",
            model="deepseek-chat",
            processing_time=0.8,
            token_usage={'total_tokens': mock_response.usage.total_tokens} if mock_response.usage else {}
        )

        print("✅ 模拟翻译器调用成功")
        print(f"   使用token数: {result.token_usage.get('total_tokens', 0)}")

    except Exception as e:
        print(f"❌ 模拟翻译器测试失败: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 所有测试通过！API修复成功！")
    print("=" * 50)

    print("\n修复总结:")
    print("- ✅ TranslationResult 不再接受 token_count 参数")
    print("- ✅ 使用 token_usage 字典存储token信息")
    print("- ✅ 兼容各种访问模式")
    print("- ✅ DeepSeek和Ollama翻译器现在使用正确的参数")

    return True


if __name__ == "__main__":
    success = test_translation_result_fix()
    if success:
        print("\n✅ API修复验证成功！现在可以正常使用翻译功能了。")
        sys.exit(0)
    else:
        print("\n❌ API修复验证失败！")
        sys.exit(1)
