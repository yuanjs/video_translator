"""
配置管理模块
处理应用配置的加载、保存和验证
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """配置管理类"""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self.config_data = {}
        self._load_env()
        self._load_config()

    def _load_env(self):
        """加载环境变量"""
        env_file = Path('.env')
        if env_file.exists():
            load_dotenv(env_file)

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'translation': {
                'target_language': 'zh-CN',
                'provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'output_format': 'bilingual',  # bilingual 或 monolingual
                'max_tokens': 2000,
                'temperature': 0.3,
                'batch_size': 10,  # 批量翻译大小
                'retry_count': 3,
                'timeout': 30
            },
            'subtitle': {
                'max_chars_per_line': 50,
                'max_lines': 2,
                'sync_tolerance': 0.1,
                'encoding': 'utf-8',
                'formats': ['srt', 'vtt', 'ass'],
                'auto_detect_language': True,
                'merge_short_segments': True,
                'min_segment_duration': 1.0
            },
            'video': {
                'supported_formats': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
                'ffmpeg_path': 'ffmpeg',
                'extract_audio': False,
                'audio_format': 'wav',
                'audio_sample_rate': 16000
            },
            'ui': {
                'theme': 'arc',
                'language': 'zh_CN',
                'window_size': '1200x800',
                'remember_last_dir': True,
                'auto_save_config': True,
                'show_progress_details': True
            },
            'api': {
                'openai': {
                    'base_url': 'https://api.openai.com/v1',
                    'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview']
                },
                'anthropic': {
                    'base_url': 'https://api.anthropic.com',
                    'models': ['claude-3-sonnet-20240229', 'claude-3-opus-20240229', 'claude-3-haiku-20240307']
                },
                'google': {
                    'project_id': None,
                    'location': 'global'
                },
                'azure': {
                    'endpoint': None,
                    'region': 'eastus'
                }
            },
            'output': {
                'default_dir': './output',
                'filename_template': '{original_name}_{lang}_{format}',
                'create_backup': True,
                'overwrite_existing': False
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/app.log',
                'max_size': '10MB',
                'backup_count': 5,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }

    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
                logger.info(f"配置文件已加载: {self.config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                self.config_data = {}
        else:
            self.config_data = {}

        # 合并默认配置
        default_config = self._get_default_config()
        self.config_data = self._merge_config(default_config, self.config_data)

        # 首次创建配置文件
        if not self.config_file.exists():
            self.save_config()

    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并配置"""
        result = default.copy()

        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点分割路径"""
        keys = key.split('.')
        data = self.config_data

        try:
            for k in keys:
                data = data[k]
            return data
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any, save: bool = True):
        """设置配置值，支持点分割路径"""
        keys = key.split('.')
        data = self.config_data

        # 导航到最后一级
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

        if save and self.get('ui.auto_save_config', True):
            self.save_config()

    def save_config(self):
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False,
                         allow_unicode=True, indent=2)
            logger.info(f"配置已保存到: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def get_api_key(self, provider: str) -> Optional[str]:
        """获取API密钥"""
        key_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_APPLICATION_CREDENTIALS',
            'azure': 'AZURE_TRANSLATOR_KEY'
        }

        env_key = key_map.get(provider)
        if env_key:
            return os.getenv(env_key)
        return None

    def validate_api_config(self, provider: str) -> bool:
        """验证API配置"""
        api_key = self.get_api_key(provider)

        if not api_key:
            logger.warning(f"未找到 {provider} 的API密钥")
            return False

        # 特殊验证逻辑
        if provider == 'google':
            credentials_path = Path(api_key)
            if not credentials_path.exists():
                logger.warning(f"Google服务账户文件不存在: {api_key}")
                return False

        return True

    def get_supported_languages(self) -> Dict[str, str]:
        """获取支持的语言列表"""
        return {
            'zh-CN': '简体中文',
            'zh-TW': '繁体中文',
            'en': 'English',
            'ja': '日本語',
            'ko': '한국어',
            'fr': 'Français',
            'de': 'Deutsch',
            'es': 'Español',
            'ru': 'Русский',
            'ar': 'العربية',
            'pt': 'Português',
            'it': 'Italiano',
            'nl': 'Nederlands',
            'pl': 'Polski',
            'tr': 'Türkçe',
            'vi': 'Tiếng Việt',
            'th': 'ไทย',
            'hi': 'हिन्दी',
            'bn': 'বাংলা',
            'ms': 'Bahasa Melayu',
            'id': 'Bahasa Indonesia',
            'tl': 'Filipino',
            'sv': 'Svenska',
            'da': 'Dansk',
            'no': 'Norsk',
            'fi': 'Suomi',
            'he': 'עברית',
            'fa': 'فارسی',
            'ur': 'اردو',
            'sw': 'Kiswahili',
            'am': 'አማርኛ',
            'my': 'မြန်မာ',
            'km': 'ខ្មែរ',
            'lo': 'ລາວ',
            'si': 'සිංහල',
            'ne': 'नेपाली',
            'ml': 'മലയാളം',
            'ta': 'தமிழ்',
            'te': 'తెలుగు',
            'kn': 'ಕನ್ನಡ',
            'gu': 'ગુજરાતી',
            'pa': 'ਪੰਜਾਬੀ',
            'or': 'ଓଡ଼ିଆ',
            'as': 'অসমীয়া',
            'mr': 'मराठी',
            'sd': 'سنڌي',
            'ps': 'پښتو',
            'dv': 'ދިވެހި',
            'bo': 'བོད་ཡིག',
            'ug': 'ئۇيغۇرچە',
            'kk': 'Қазақша',
            'ky': 'Кыргызча',
            'tg': 'Тоҷикӣ',
            'uz': 'O\'zbekcha',
            'mn': 'Монгол'
        }

    def get_translation_providers(self) -> Dict[str, Dict[str, Any]]:
        """获取翻译提供商信息"""
        return {
            'openai': {
                'name': 'OpenAI GPT',
                'models': self.get('api.openai.models', []),
                'requires_key': True,
                'description': '使用GPT模型进行高质量翻译'
            },
            'anthropic': {
                'name': 'Anthropic Claude',
                'models': self.get('api.anthropic.models', []),
                'requires_key': True,
                'description': '使用Claude模型进行智能翻译'
            },
            'google': {
                'name': 'Google Translate',
                'models': ['translate-v3'],
                'requires_key': True,
                'description': 'Google Cloud Translation API'
            },
            'azure': {
                'name': 'Azure Translator',
                'models': ['azure-translator'],
                'requires_key': True,
                'description': 'Microsoft Azure认知服务翻译'
            }
        }

    def update_last_used_dir(self, directory: str):
        """更新最后使用的目录"""
        if self.get('ui.remember_last_dir', True):
            self.set('ui.last_used_dir', directory)

    def get_last_used_dir(self) -> str:
        """获取最后使用的目录"""
        return self.get('ui.last_used_dir', os.path.expanduser('~'))

    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config_data = self._get_default_config()
        self.save_config()
        logger.info("配置已重置为默认值")


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取全局配置实例"""
    return config


def setup_logging():
    """设置日志配置"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('file', 'logs/app.log')

    # 创建日志目录
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # 配置日志
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
