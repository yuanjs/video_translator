#!/usr/bin/env python3
"""
视频翻译器主入口文件
Video Translator Main Entry Point
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 导入应用模块
try:
    from src.gui.main_window import VideoTranslatorGUI
    from src.utils.config import get_config, setup_logging
    from src.utils.logger import init_logger, get_logger
    from src.utils.helpers import check_ffmpeg_available, get_system_info
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖都已正确安装")
    sys.exit(1)


def check_dependencies():
    """检查依赖环境"""
    issues = []

    # 检查Python版本
    if sys.version_info < (3, 8):
        issues.append("需要Python 3.8或更高版本")

    # 检查FFmpeg
    if not check_ffmpeg_available():
        issues.append("FFmpeg未找到，请安装FFmpeg")

    # 检查必要的Python包
    required_packages = [
        'tkinter', 'ttkthemes', 'Pillow', 'ffmpeg-python',
        'pysrt', 'webvtt-py', 'openai', 'anthropic',
        'requests', 'PyYAML', 'tqdm', 'colorama'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'ttkthemes':
                import ttkthemes
            elif package == 'Pillow':
                import PIL
            elif package == 'ffmpeg-python':
                import ffmpeg
            elif package == 'pysrt':
                import pysrt
            elif package == 'webvtt-py':
                import webvtt
            elif package == 'openai':
                import openai
            elif package == 'anthropic':
                import anthropic
            elif package == 'requests':
                import requests
            elif package == 'PyYAML':
                import yaml
            elif package == 'tqdm':
                import tqdm
            elif package == 'colorama':
                import colorama
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        issues.append(f"缺少Python包: {', '.join(missing_packages)}")

    return issues


def setup_environment():
    """设置运行环境"""
    # 设置工作目录
    os.chdir(project_root)

    # 创建必要的目录
    directories = ['logs', 'output', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    # 初始化配置
    config = get_config()

    # 初始化日志系统
    setup_logging()
    init_logger(config.get('logging', {}))

    return config


def print_startup_info():
    """打印启动信息"""
    print("=" * 60)
    print("视频翻译器 (Video Translator)")
    print("版本: 1.0.0")
    print("=" * 60)

    # 打印系统信息
    system_info = get_system_info()
    print(f"操作系统: {system_info.get('platform', 'Unknown')}")
    print(f"Python版本: {system_info.get('python_version', 'Unknown')}")
    print(f"工作目录: {os.getcwd()}")
    print("-" * 60)


def create_env_template():
    """创建环境变量模板文件"""
    env_template_path = project_root / '.env.template'

    if not env_template_path.exists():
        env_template_content = """# API密钥配置模板
# 复制此文件为 .env 并填入您的API密钥

# OpenAI API密钥
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude API密钥
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Cloud Translation API服务账户文件路径
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json

# Azure Translator API密钥和区域
AZURE_TRANSLATOR_KEY=your_azure_translator_key_here
AZURE_TRANSLATOR_REGION=your_azure_region_here

# 可选：自定义API端点
# OPENAI_BASE_URL=https://api.openai.com/v1
# ANTHROPIC_BASE_URL=https://api.anthropic.com
"""

        try:
            with open(env_template_path, 'w', encoding='utf-8') as f:
                f.write(env_template_content)
            print(f"已创建环境变量模板文件: {env_template_path}")
            print("请复制为 .env 文件并配置您的API密钥")
        except Exception as e:
            print(f"创建环境变量模板文件失败: {e}")


def main():
    """主函数"""
    try:
        # 打印启动信息
        print_startup_info()

        # 检查依赖
        print("检查系统依赖...")
        issues = check_dependencies()

        if issues:
            print("\n❌ 发现以下问题:")
            for issue in issues:
                print(f"  - {issue}")
            print("\n请解决上述问题后重新运行程序")

            # 如果只是缺少API密钥，可以继续运行
            critical_issues = [issue for issue in issues if 'FFmpeg' in issue or 'Python' in issue or '包' in issue]
            if critical_issues:
                return 1
            else:
                print("\n⚠️  警告: 某些功能可能无法正常使用")
        else:
            print("✅ 所有依赖检查通过")

        # 设置环境
        print("初始化运行环境...")
        config = setup_environment()

        # 创建环境变量模板
        create_env_template()

        # 检查是否存在.env文件
        env_file = project_root / '.env'
        if not env_file.exists():
            print(f"\n⚠️  未找到 .env 文件")
            print(f"请根据 .env.template 创建 .env 文件并配置API密钥")

        # 获取日志记录器
        logger = get_logger(__name__)
        logger.info("视频翻译器启动")
        logger.info(f"Python版本: {sys.version}")
        logger.info(f"工作目录: {os.getcwd()}")

        # 启动GUI应用
        print("启动图形界面...")
        print("-" * 60)

        app = VideoTranslatorGUI()
        app.run()

        return 0

    except KeyboardInterrupt:
        print("\n用户中断程序")
        return 1

    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")

        # 尝试记录错误日志
        try:
            logger = get_logger(__name__)
            logger.error(f"程序运行出错: {e}", exc_info=True)
        except:
            pass

        return 1


if __name__ == "__main__":
    # 设置异常处理
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        print(f"\n❌ 未处理的异常: {exc_type.__name__}: {exc_value}")

        try:
            logger = get_logger(__name__)
            logger.critical("未处理的异常", exc_info=(exc_type, exc_value, exc_traceback))
        except:
            pass

    sys.excepthook = handle_exception

    # 运行主程序
    exit_code = main()
    sys.exit(exit_code)
