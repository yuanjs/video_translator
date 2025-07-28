#!/usr/bin/env python3
"""
视频翻译器环境管理脚本
Virtual Environment Management Script for Video Translator

提供虚拟环境的创建、激活、依赖管理等功能
Provides virtual environment creation, activation, dependency management, etc.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil
import json

class Colors:
    """终端颜色常量"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class EnvironmentManager:
    """环境管理器"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.is_windows = platform.system().lower() == "windows"

        # 虚拟环境中的Python和pip路径
        if self.is_windows:
            self.venv_python = self.venv_path / "Scripts" / "python.exe"
            self.venv_pip = self.venv_path / "Scripts" / "pip.exe"
            self.activate_script = self.venv_path / "Scripts" / "activate.bat"
        else:
            self.venv_python = self.venv_path / "bin" / "python"
            self.venv_pip = self.venv_path / "bin" / "pip"
            self.activate_script = self.venv_path / "bin" / "activate"

    def print_colored(self, message: str, color: str = Colors.OKBLUE):
        """打印彩色文本"""
        print(f"{color}{message}{Colors.ENDC}")

    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    def run_command(self, command: list, capture_output: bool = True, check: bool = True):
        """运行命令"""
        try:
            if capture_output:
                result = subprocess.run(command, capture_output=True, text=True, check=check)
                return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
            else:
                result = subprocess.run(command, check=check)
                return result.returncode == 0, "", ""
        except subprocess.CalledProcessError as e:
            return False, "", str(e)
        except FileNotFoundError as e:
            return False, "", f"命令未找到: {e}"

    def check_python_version(self):
        """检查Python版本"""
        version = sys.version_info
        if version >= (3, 8):
            self.print_colored(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}", Colors.OKGREEN)
            return True
        else:
            self.print_colored(f"❌ Python版本过低: {version.major}.{version.minor}", Colors.FAIL)
            self.print_colored("   需要Python 3.8或更高版本", Colors.WARNING)
            return False

    def create_venv(self):
        """创建虚拟环境"""
        self.print_header("创建虚拟环境")

        if self.venv_path.exists():
            self.print_colored("⚠️  虚拟环境已存在", Colors.WARNING)
            recreate = input("是否重新创建虚拟环境? (y/N): ").lower() == 'y'
            if recreate:
                self.remove_venv()
            else:
                return True

        self.print_colored("🔧 正在创建虚拟环境...")
        success, stdout, stderr = self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])

        if success:
            self.print_colored("✅ 虚拟环境创建成功", Colors.OKGREEN)
            return True
        else:
            self.print_colored(f"❌ 虚拟环境创建失败: {stderr}", Colors.FAIL)
            return False

    def remove_venv(self):
        """删除虚拟环境"""
        if self.venv_path.exists():
            self.print_colored("🗑️  正在删除虚拟环境...")
            try:
                shutil.rmtree(self.venv_path)
                self.print_colored("✅ 虚拟环境删除成功", Colors.OKGREEN)
                return True
            except Exception as e:
                self.print_colored(f"❌ 虚拟环境删除失败: {e}", Colors.FAIL)
                return False
        else:
            self.print_colored("ℹ️  虚拟环境不存在", Colors.OKBLUE)
            return True

    def install_dependencies(self):
        """安装依赖"""
        self.print_header("安装项目依赖")

        if not self.venv_path.exists():
            self.print_colored("❌ 虚拟环境不存在，请先创建", Colors.FAIL)
            return False

        if not self.requirements_file.exists():
            self.print_colored("❌ requirements.txt 文件不存在", Colors.FAIL)
            return False

        # 升级pip
        self.print_colored("⬆️  升级pip...")
        success, _, _ = self.run_command([str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip"])

        if not success:
            self.print_colored("⚠️  pip升级失败，但继续安装依赖", Colors.WARNING)

        # 安装依赖
        self.print_colored("📦 安装项目依赖...")
        success, stdout, stderr = self.run_command([
            str(self.venv_pip), "install", "-r", str(self.requirements_file)
        ])

        if success:
            self.print_colored("✅ 依赖安装完成", Colors.OKGREEN)
            return True
        else:
            self.print_colored(f"❌ 依赖安装失败: {stderr}", Colors.FAIL)
            return False

    def check_environment(self):
        """检查环境状态"""
        self.print_header("环境状态检查")

        # 检查虚拟环境
        if self.venv_path.exists():
            self.print_colored("✅ 虚拟环境存在", Colors.OKGREEN)

            # 检查Python版本
            if self.venv_python.exists():
                success, version, _ = self.run_command([str(self.venv_python), "--version"])
                if success:
                    self.print_colored(f"✅ 虚拟环境Python: {version}", Colors.OKGREEN)
                else:
                    self.print_colored("❌ 无法获取虚拟环境Python版本", Colors.FAIL)

            # 检查已安装的包
            if self.venv_pip.exists():
                success, packages, _ = self.run_command([str(self.venv_pip), "list", "--format=json"])
                if success:
                    try:
                        package_list = json.loads(packages)
                        self.print_colored(f"📦 已安装包数量: {len(package_list)}", Colors.OKBLUE)

                        # 检查关键依赖
                        key_packages = ["openai", "anthropic", "ffmpeg-python", "ttkthemes"]
                        installed_packages = {pkg["name"].lower() for pkg in package_list}

                        for pkg in key_packages:
                            if pkg in installed_packages:
                                self.print_colored(f"   ✅ {pkg}", Colors.OKGREEN)
                            else:
                                self.print_colored(f"   ❌ {pkg} (未安装)", Colors.FAIL)

                    except json.JSONDecodeError:
                        self.print_colored("⚠️  无法解析包列表", Colors.WARNING)
        else:
            self.print_colored("❌ 虚拟环境不存在", Colors.FAIL)

        # 检查项目文件
        essential_files = [
            "run.py",
            "requirements.txt",
            "config.yaml",
            "src/main.py",
            "src/core/translator.py"
        ]

        self.print_colored("\n📋 项目文件检查:", Colors.OKBLUE)
        for file_path in essential_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.print_colored(f"   ✅ {file_path}", Colors.OKGREEN)
            else:
                self.print_colored(f"   ❌ {file_path}", Colors.FAIL)

    def show_activation_guide(self):
        """显示环境激活指南"""
        self.print_header("环境激活指南")

        if not self.venv_path.exists():
            self.print_colored("❌ 虚拟环境不存在，请先运行: python manage_env.py create", Colors.FAIL)
            return

        self.print_colored("🔧 激活虚拟环境的方法:", Colors.OKBLUE)

        if self.is_windows:
            print(f"   Windows (CMD):    {self.venv_path}\\Scripts\\activate.bat")
            print(f"   Windows (PowerShell): {self.venv_path}\\Scripts\\Activate.ps1")
        else:
            print(f"   Linux/macOS:      source {self.activate_script}")

        self.print_colored("\n🚀 或使用便捷脚本:", Colors.OKBLUE)
        if self.is_windows:
            print("   activate_env.bat")
        else:
            print("   source activate_env.sh")

        self.print_colored("\n💡 激活后可用命令:", Colors.OKCYAN)
        commands = [
            ("python run.py", "启动图形界面"),
            ("python run.py --cli", "启动命令行界面"),
            ("python test_providers.py", "测试AI平台连接"),
            ("python setup_platforms.py", "配置新AI平台"),
            ("python demo_new_platforms.py", "查看功能演示"),
            ("deactivate", "退出虚拟环境")
        ]

        for cmd, desc in commands:
            print(f"   {cmd:<30} # {desc}")

    def setup_complete_environment(self):
        """完整环境设置"""
        self.print_header("完整环境设置")

        # 检查Python版本
        if not self.check_python_version():
            return False

        # 创建虚拟环境
        if not self.create_venv():
            return False

        # 安装依赖
        if not self.install_dependencies():
            return False

        # 最终检查
        self.check_environment()

        self.print_colored("\n🎉 环境设置完成!", Colors.OKGREEN)
        self.show_activation_guide()

        return True

    def interactive_menu(self):
        """交互式菜单"""
        while True:
            self.print_header("视频翻译器环境管理")

            print("请选择操作:")
            print("1. 创建虚拟环境")
            print("2. 安装/更新依赖")
            print("3. 检查环境状态")
            print("4. 完整环境设置")
            print("5. 删除虚拟环境")
            print("6. 显示激活指南")
            print("0. 退出")

            choice = input("\n请输入选项 (0-6): ").strip()

            if choice == "1":
                self.create_venv()
            elif choice == "2":
                self.install_dependencies()
            elif choice == "3":
                self.check_environment()
            elif choice == "4":
                self.setup_complete_environment()
            elif choice == "5":
                confirm = input("确定要删除虚拟环境吗? (y/N): ").lower() == 'y'
                if confirm:
                    self.remove_venv()
            elif choice == "6":
                self.show_activation_guide()
            elif choice == "0":
                self.print_colored("👋 再见!", Colors.OKGREEN)
                break
            else:
                self.print_colored("❌ 无效选项", Colors.FAIL)

            input("\n按回车键继续...")

def main():
    """主函数"""
    manager = EnvironmentManager()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "create":
            manager.create_venv()
        elif command == "install":
            manager.install_dependencies()
        elif command == "check":
            manager.check_environment()
        elif command == "setup":
            manager.setup_complete_environment()
        elif command == "remove":
            manager.remove_venv()
        elif command == "guide":
            manager.show_activation_guide()
        else:
            print("用法: python manage_env.py [create|install|check|setup|remove|guide]")
            print("或直接运行进入交互模式")
    else:
        manager.interactive_menu()

if __name__ == "__main__":
    main()
