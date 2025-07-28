#!/usr/bin/env python3
"""
视频翻译器启动脚本
Video Translator Launcher

用法:
    python run.py              # 启动GUI界面
    python run.py --cli         # 启动命令行界面
    python run.py --help        # 显示帮助信息
"""

import os
import sys
import argparse
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                     视频翻译器 v1.0.0                        ║
║                   Video Translator v1.0.0                   ║
║                                                              ║
║  功能特性:                                                    ║
║  • 支持多种视频格式                                           ║
║  • 智能字幕提取                                               ║
║  • AI翻译集成 (OpenAI, Claude, Google, Azure)                ║
║  • 批量处理                                                   ║
║  • 多种输出格式                                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"   当前版本: Python {sys.version}")
        print("   请升级Python后重试")
        return False
    return True


def check_basic_dependencies():
    """检查基本依赖"""
    required_packages = {
        'tkinter': '图形界面库',
        'pathlib': '路径处理库',
        'argparse': '命令行参数解析库',
        'asyncio': '异步处理库'
    }

    missing = []

    for package, description in required_packages.items():
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'pathlib':
                from pathlib import Path
            elif package == 'argparse':
                import argparse
            elif package == 'asyncio':
                import asyncio
        except ImportError:
            missing.append(f"{package} ({description})")

    if missing:
        print("❌ 缺少基本依赖:")
        for pkg in missing:
            print(f"   • {pkg}")
        print("\n请安装missing依赖后重试")
        return False

    return True


def setup_environment():
    """设置运行环境"""
    # 创建必要的目录
    directories = ['logs', 'output', 'temp']
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)

    # 设置工作目录
    os.chdir(project_root)


def create_env_file_if_missing():
    """如果.env文件不存在，提示用户创建"""
    env_file = project_root / '.env'
    env_template = project_root / '.env.template'

    if not env_file.exists():
        print("⚠️  未找到 .env 配置文件")

        if env_template.exists():
            print(f"💡 提示: 请复制 {env_template.name} 为 .env 并配置您的API密钥")

            response = input("是否现在创建 .env 文件? (y/N): ").strip().lower()
            if response == 'y':
                try:
                    import shutil
                    shutil.copy2(env_template, env_file)
                    print(f"✅ 已创建 {env_file}")
                    print("请编辑 .env 文件并配置您的API密钥")

                    # 询问是否打开文件编辑
                    edit_response = input("是否打开文件进行编辑? (y/N): ").strip().lower()
                    if edit_response == 'y':
                        try:
                            if sys.platform.startswith('win'):
                                os.startfile(env_file)
                            elif sys.platform.startswith('darwin'):
                                os.system(f'open "{env_file}"')
                            else:
                                os.system(f'xdg-open "{env_file}"')
                        except:
                            print(f"请手动编辑文件: {env_file}")

                    print("\n配置完成后请重新运行程序")
                    return False

                except Exception as e:
                    print(f"❌ 创建 .env 文件失败: {e}")
        else:
            print("请手动创建 .env 文件并配置API密钥")

        print("\n没有API密钥将无法进行翻译，但可以使用字幕提取功能")
        response = input("是否继续启动? (y/N): ").strip().lower()
        if response != 'y':
            return False

    return True


def launch_gui():
    """启动GUI界面"""
    try:
        print("🚀 启动图形界面...")
        from src.main import main
        return main()
    except ImportError as e:
        print(f"❌ 导入GUI模块失败: {e}")
        print("请检查依赖是否正确安装:")
        print("   pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")
        return 1


def launch_cli(cli_args):
    """启动命令行界面"""
    try:
        print("🚀 启动命令行界面...")
        from src.cli import main

        # 将命令行参数传递给CLI
        original_argv = sys.argv
        sys.argv = ['cli.py'] + cli_args

        try:
            return main()
        finally:
            sys.argv = original_argv

    except ImportError as e:
        print(f"❌ 导入CLI模块失败: {e}")
        print("请检查依赖是否正确安装:")
        print("   pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ CLI启动失败: {e}")
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="视频翻译器启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run.py                    # 启动GUI界面
  python run.py --cli              # 启动CLI界面
  python run.py --cli --help       # 显示CLI帮助
  python run.py --version          # 显示版本信息
  python run.py --check            # 检查系统环境
        """
    )

    parser.add_argument(
        '--cli',
        action='store_true',
        help='启动命令行界面'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='视频翻译器 v1.0.0'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='检查系统环境和依赖'
    )

    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='不显示启动横幅'
    )

    # 解析已知参数，剩余参数传递给CLI
    args, remaining_args = parser.parse_known_args()

    # 显示横幅
    if not args.no_banner:
        print_banner()

    # 基本检查
    if not check_python_version():
        return 1

    if not check_basic_dependencies():
        return 1

    # 设置环境
    setup_environment()

    # 如果只是检查环境
    if args.check:
        print("🔍 系统环境检查:")
        print(f"✅ Python版本: {sys.version}")
        print(f"✅ 工作目录: {os.getcwd()}")
        print(f"✅ 项目路径: {project_root}")

        # 检查主要依赖
        print("\n📦 主要依赖检查:")
        dependencies = [
            ('ttkthemes', '主题库'),
            ('ffmpeg-python', 'FFmpeg Python接口'),
            ('pysrt', 'SRT字幕处理'),
            ('openai', 'OpenAI API'),
            ('anthropic', 'Anthropic API'),
            ('requests', 'HTTP请求库'),
            ('PyYAML', 'YAML配置文件'),
            ('tqdm', '进度条库')
        ]

        for package, description in dependencies:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package} ({description})")
            except ImportError:
                print(f"❌ {package} ({description}) - 未安装")

        # 检查FFmpeg
        print("\n🎬 FFmpeg检查:")
        try:
            from src.utils.helpers import check_ffmpeg_available
            if check_ffmpeg_available():
                print("✅ FFmpeg 可用")
            else:
                print("❌ FFmpeg 不可用")
        except:
            print("❓ 无法检查FFmpeg状态")

        # 检查配置文件
        print("\n⚙️  配置文件检查:")
        config_file = project_root / 'config.yaml'
        env_file = project_root / '.env'

        print(f"{'✅' if config_file.exists() else '❌'} config.yaml: {'存在' if config_file.exists() else '不存在'}")
        print(f"{'✅' if env_file.exists() else '❌'} .env: {'存在' if env_file.exists() else '不存在'}")

        return 0

    # 检查环境变量文件
    if not create_env_file_if_missing():
        return 1

    try:
        if args.cli:
            # 启动CLI
            return launch_cli(remaining_args)
        else:
            # 启动GUI
            return launch_gui()

    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
        return 130
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"启动脚本执行失败: {e}")
        sys.exit(1)
