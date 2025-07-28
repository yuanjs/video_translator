"""
AI翻译引擎核心模块
支持多个AI平台的字幕翻译功能
"""

import asyncio
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# AI平台客户端
import openai
import anthropic
from google.cloud import translate_v2 as translate
import requests

from .subtitle_extractor import SubtitleFile, SubtitleSegment
from ..utils.config import get_config
from ..utils.logger import get_logger, get_translation_logger, get_performance_logger
from ..utils.helpers import (
    split_text_by_length,
    retry_on_failure,
    estimate_translation_time,
    ProgressTracker
)

logger = get_logger(__name__)
translation_logger = get_translation_logger(__name__)
performance_logger = get_performance_logger(__name__)


class TranslationProvider(Enum):
    """翻译提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"


@dataclass
class TranslationRequest:
    """翻译请求"""
    text: str
    source_language: str = "auto"
    target_language: str = "zh-CN"
    context: str = ""
    max_length: int = 2000


@dataclass
class TranslationResult:
    """翻译结果"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float = 1.0
    provider: str = ""
    model: str = ""
    processing_time: float = 0.0
    token_usage: Dict[str, int] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.token_usage is None:
            self.token_usage = {}


class BaseTranslator:
    """翻译器基类"""

    def __init__(self, provider: TranslationProvider, api_key: str, **kwargs):
        self.provider = provider
        self.api_key = api_key
        self.config = get_config()
        self.kwargs = kwargs
        self._initialize_client()

    def _initialize_client(self):
        """初始化客户端"""
        pass

    async def translate(self, request: TranslationRequest) -> TranslationResult:
        """执行翻译"""
        raise NotImplementedError

    def _prepare_prompt(self, text: str, target_language: str, context: str = "") -> str:
        """准备翻译提示词"""
        language_names = self.config.get_supported_languages()
        target_lang_name = language_names.get(target_language, target_language)

        prompt = f"""请将以下文本翻译成{target_lang_name}。

要求：
1. 保持原文的语义和语调
2. 确保翻译自然流畅
3. 保持专业术语的准确性
4. 如果是字幕文本，保持适合阅读的长度

{f"上下文信息：{context}" if context else ""}

原文：
{text}

翻译："""

        return prompt

    def _extract_translation(self, response_text: str) -> str:
        """从响应中提取翻译结果"""
        # 移除常见的前缀
        prefixes = ["翻译：", "译文：", "Translation:", "翻译结果："]
        for prefix in prefixes:
            if response_text.startswith(prefix):
                response_text = response_text[len(prefix):].strip()

        return response_text.strip()


class OpenAITranslator(BaseTranslator):
    """OpenAI翻译器"""

    def _initialize_client(self):
        """初始化OpenAI客户端"""
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = self.kwargs.get('model', 'gpt-3.5-turbo')

    @retry_on_failure(max_retries=3, delay=2.0)
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        """使用OpenAI进行翻译"""
        start_time = time.time()

        try:
            prompt = self._prepare_prompt(
                request.text,
                request.target_language,
                request.context
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的翻译专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.config.get('translation.max_tokens', 2000),
                    temperature=self.config.get('translation.temperature', 0.3)
                )
            )

            translated_text = response.choices[0].message.content.strip()
            translated_text = self._extract_translation(translated_text)

            processing_time = time.time() - start_time

            return TranslationResult(
                original_text=request.text,
                translated_text=translated_text,
                source_language=request.source_language,
                target_language=request.target_language,
                provider=self.provider.value,
                model=self.model,
                processing_time=processing_time,
                token_usage={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            )

        except Exception as e:
            logger.error(f"OpenAI翻译失败: {e}")
            return TranslationResult(
                original_text=request.text,
                translated_text="",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=self.provider.value,
                model=self.model,
                processing_time=time.time() - start_time,
                error=str(e)
            )


class AnthropicTranslator(BaseTranslator):
    """Anthropic翻译器"""

    def _initialize_client(self):
        """初始化Anthropic客户端"""
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = self.kwargs.get('model', 'claude-3-sonnet-20240229')

    @retry_on_failure(max_retries=3, delay=2.0)
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        """使用Anthropic进行翻译"""
        start_time = time.time()

        try:
            prompt = self._prepare_prompt(
                request.text,
                request.target_language,
                request.context
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=self.config.get('translation.max_tokens', 2000),
                    temperature=self.config.get('translation.temperature', 0.3),
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            )

            translated_text = response.content[0].text
            translated_text = self._extract_translation(translated_text)

            processing_time = time.time() - start_time

            return TranslationResult(
                original_text=request.text,
                translated_text=translated_text,
                source_language=request.source_language,
                target_language=request.target_language,
                provider=self.provider.value,
                model=self.model,
                processing_time=processing_time,
                token_usage={
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            )

        except Exception as e:
            logger.error(f"Anthropic翻译失败: {e}")
            return TranslationResult(
                original_text=request.text,
                translated_text="",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=self.provider.value,
                model=self.model,
                processing_time=time.time() - start_time,
                error=str(e)
            )


class GoogleTranslator(BaseTranslator):
    """Google翻译器"""

    def _initialize_client(self):
        """初始化Google翻译客户端"""
        self.client = translate.Client()

    @retry_on_failure(max_retries=3, delay=1.0)
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        """使用Google进行翻译"""
        start_time = time.time()

        try:
            # Google翻译API的语言代码映射
            target_lang = self._map_language_code(request.target_language)

            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.translate(
                    request.text,
                    target_language=target_lang,
                    source_language=None  # 自动检测
                )
            )

            translated_text = result['translatedText']
            detected_lang = result.get('detectedSourceLanguage', 'unknown')

            processing_time = time.time() - start_time

            return TranslationResult(
                original_text=request.text,
                translated_text=translated_text,
                source_language=detected_lang,
                target_language=request.target_language,
                provider=self.provider.value,
                model='translate-v2',
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"Google翻译失败: {e}")
            return TranslationResult(
                original_text=request.text,
                translated_text="",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=self.provider.value,
                model='translate-v2',
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def _map_language_code(self, lang_code: str) -> str:
        """映射语言代码到Google支持的格式"""
        mapping = {
            'zh-CN': 'zh',
            'zh-TW': 'zh-TW',
            'en': 'en',
            'ja': 'ja',
            'ko': 'ko'
        }
        return mapping.get(lang_code, lang_code)


class AzureTranslator(BaseTranslator):
    """Azure翻译器"""

    def _initialize_client(self):
        """初始化Azure翻译客户端"""
        self.endpoint = self.config.get('api.azure.endpoint', 'https://api.cognitive.microsofttranslator.com')
        self.region = self.config.get('api.azure.region', 'eastus')

    @retry_on_failure(max_retries=3, delay=1.0)
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        """使用Azure进行翻译"""
        start_time = time.time()

        try:
            url = f"{self.endpoint}/translate"
            params = {
                'api-version': '3.0',
                'to': self._map_language_code(request.target_language)
            }

            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Ocp-Apim-Subscription-Region': self.region,
                'Content-Type': 'application/json'
            }

            body = [{'text': request.text}]

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(url, params=params, headers=headers, json=body)
            )

            if response.status_code == 200:
                result = response.json()[0]
                translated_text = result['translations'][0]['text']
                detected_lang = result.get('detectedLanguage', {}).get('language', 'unknown')

                processing_time = time.time() - start_time

                return TranslationResult(
                    original_text=request.text,
                    translated_text=translated_text,
                    source_language=detected_lang,
                    target_language=request.target_language,
                    provider=self.provider.value,
                    model='azure-translator',
                    processing_time=processing_time
                )
            else:
                raise Exception(f"Azure API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Azure翻译失败: {e}")
            return TranslationResult(
                original_text=request.text,
                translated_text="",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=self.provider.value,
                model='azure-translator',
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def _map_language_code(self, lang_code: str) -> str:
        """映射语言代码到Azure支持的格式"""
        mapping = {
            'zh-CN': 'zh-Hans',
            'zh-TW': 'zh-Hant',
            'en': 'en',
            'ja': 'ja',
            'ko': 'ko'
        }
        return mapping.get(lang_code, lang_code)


class TranslationManager:
    """翻译管理器"""

    def __init__(self):
        self.config = get_config()
        self.translators: Dict[TranslationProvider, BaseTranslator] = {}
        self._initialize_translators()

    def _initialize_translators(self):
        """初始化翻译器"""
        providers_config = self.config.get_translation_providers()

        for provider_key, provider_info in providers_config.items():
            try:
                provider = TranslationProvider(provider_key)
                api_key = self.config.get_api_key(provider_key)

                if not api_key:
                    logger.warning(f"未配置 {provider_key} 的API密钥")
                    continue

                translator = self._create_translator(provider, api_key)
                if translator:
                    self.translators[provider] = translator
                    logger.info(f"已初始化 {provider_key} 翻译器")

            except Exception as e:
                logger.error(f"初始化 {provider_key} 翻译器失败: {e}")

    def _create_translator(self, provider: TranslationProvider, api_key: str) -> Optional[BaseTranslator]:
        """创建翻译器实例"""
        translator_classes = {
            TranslationProvider.OPENAI: OpenAITranslator,
            TranslationProvider.ANTHROPIC: AnthropicTranslator,
            TranslationProvider.GOOGLE: GoogleTranslator,
            TranslationProvider.AZURE: AzureTranslator
        }

        translator_class = translator_classes.get(provider)
        if translator_class:
            return translator_class(provider, api_key)
        return None

    def get_available_providers(self) -> List[TranslationProvider]:
        """获取可用的翻译提供商"""
        return list(self.translators.keys())

    async def translate_text(self, text: str,
                           target_language: str = "zh-CN",
                           provider: Optional[TranslationProvider] = None,
                           context: str = "") -> TranslationResult:
        """翻译单个文本"""
        if not provider:
            provider_key = self.config.get('translation.provider', 'openai')
            provider = TranslationProvider(provider_key)

        if provider not in self.translators:
            raise ValueError(f"翻译提供商 {provider.value} 不可用")

        translator = self.translators[provider]
        request = TranslationRequest(
            text=text,
            target_language=target_language,
            context=context
        )

        return await translator.translate(request)

    async def translate_subtitle_file(self,
                                    subtitle_file: SubtitleFile,
                                    target_language: str = "zh-CN",
                                    provider: Optional[TranslationProvider] = None,
                                    progress_callback: Optional[Callable] = None) -> SubtitleFile:
        """翻译字幕文件"""
        logger.info(f"开始翻译字幕文件，共 {len(subtitle_file.segments)} 个片段")

        if not provider:
            provider_key = self.config.get('translation.provider', 'openai')
            provider = TranslationProvider(provider_key)

        # 初始化翻译日志
        translation_logger.start_translation(len(subtitle_file.segments))

        # 创建进度跟踪器
        progress_tracker = ProgressTracker(len(subtitle_file.segments))

        # 批量处理设置
        batch_size = self.config.get('translation.batch_size', 10)
        max_workers = min(batch_size, 5)  # 限制并发数

        # 分批处理字幕片段
        batches = [subtitle_file.segments[i:i + batch_size]
                  for i in range(0, len(subtitle_file.segments), batch_size)]

        translated_segments = []

        for batch_index, batch in enumerate(batches):
            logger.info(f"处理批次 {batch_index + 1}/{len(batches)}")

            # 并发翻译批次中的片段
            tasks = []
            for segment in batch:
                if segment.text.strip():
                    task = self._translate_segment(
                        segment,
                        target_language,
                        provider,
                        subtitle_file.segments  # 提供上下文
                    )
                    tasks.append((segment, task))
                else:
                    # 空文本直接跳过
                    translated_segments.append(segment)
                    progress_tracker.update()

            # 执行翻译任务
            if tasks:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_segment = {
                        executor.submit(asyncio.run, task): segment
                        for segment, task in tasks
                    }

                    for future in as_completed(future_to_segment):
                        original_segment = future_to_segment[future]
                        try:
                            result = future.result()
                            if result.error:
                                logger.error(f"片段 {original_segment.index} 翻译失败: {result.error}")
                                translation_logger.log_segment_failed(
                                    original_segment.index - 1,
                                    result.error
                                )
                                # 保持原文
                                original_segment.translated_text = original_segment.text
                            else:
                                original_segment.translated_text = result.translated_text
                                translation_logger.log_segment_translated(
                                    original_segment.index - 1,
                                    len(result.translated_text),
                                    result.provider
                                )

                            translated_segments.append(original_segment)
                            progress_tracker.update()

                            # 更新进度回调
                            if progress_callback:
                                progress_info = progress_tracker.get_progress()
                                progress_callback(
                                    progress_info['current'],
                                    progress_info['total'],
                                    progress_info['progress']
                                )

                        except Exception as e:
                            logger.error(f"处理片段 {original_segment.index} 时出错: {e}")
                            original_segment.translated_text = original_segment.text
                            translated_segments.append(original_segment)
                            progress_tracker.update()

            # 短暂延迟，避免API限速
            if batch_index < len(batches) - 1:
                await asyncio.sleep(0.5)

        # 按索引排序
        translated_segments.sort(key=lambda s: s.index)

        # 创建新的字幕文件
        translated_subtitle_file = SubtitleFile()
        translated_subtitle_file.segments = translated_segments
        translated_subtitle_file.format = subtitle_file.format
        translated_subtitle_file.encoding = subtitle_file.encoding
        translated_subtitle_file.language = target_language

        translation_logger.finish_translation()
        logger.info("字幕翻译完成")

        return translated_subtitle_file

    async def _translate_segment(self,
                               segment: SubtitleSegment,
                               target_language: str,
                               provider: TranslationProvider,
                               all_segments: List[SubtitleSegment]) -> TranslationResult:
        """翻译单个字幕片段"""
        # 构建上下文（前后几个片段的文本）
        context_segments = []
        current_index = segment.index - 1  # 转换为0基索引

        # 获取前面的片段作为上下文
        for i in range(max(0, current_index - 2), current_index):
            if i < len(all_segments):
                context_segments.append(all_segments[i].text)

        # 获取后面的片段作为上下文
        for i in range(current_index + 1, min(len(all_segments), current_index + 3)):
            context_segments.append(all_segments[i].text)

        context = " | ".join(context_segments) if context_segments else ""

        return await self.translate_text(
            segment.text,
            target_language,
            provider,
            context
        )

    def get_translation_statistics(self) -> Dict[str, Any]:
        """获取翻译统计信息"""
        return {
            'available_providers': [p.value for p in self.get_available_providers()],
            'default_provider': self.config.get('translation.provider'),
            'supported_languages': list(self.config.get_supported_languages().keys())
        }
