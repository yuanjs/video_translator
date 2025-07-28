#!/usr/bin/env python3
"""
AI平台快速配置脚本
Quick Setup Script for AI Platforms

自动化配置DeepSeek和Ollama等新增AI平台的工具
Automated tool for configuring new AI platforms like DeepSeek and Ollama
"""

import os
import sys
import json
import yaml
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time

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
    UNDERLINE = '\033[4m'

class PlatformSetup:
    """AI平台设置类"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "config.yaml"
        self.api_keys_file = self.project_root / "api_keys.yaml"
        self.api_keys_example = self.project_root / "api_keys_example.yaml"

    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    def print_success(self, message: str):
        """打印成功信息"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

    def print_warning(self, message: str):
        """打印警告信息"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

    def print_error(self, message: str):
        """打印错误信息"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

    def print_info(self, message: str):
        """打印信息"""
        print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")

    def run_command(self, command: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """运行系统命令"""
        try:
            if capture_output:
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                return result.returncode == 0, result.stdout.strip()
            else:
                result = subprocess.run(command, timeout=60)
                return result.returncode == 0, ""
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return False, str(e)

    def check_system_requirements(self) -> bool:
        """检查系统要求"""
        self.print_header("系统要求检查")

        all_passed = True

        # 检查Python版本
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.print_success(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            self.print_error(f"Python版本过低: {python_version.major}.{python_version.minor}")
            self.print_info("请安装Python 3.8或更高版本")
            all_passed = False

        # 检查pip
        success, pip_version = self.run_command([sys.executable, "-m", "pip", "--version"])
        if success:
            self.print_success(f"pip已安装: {pip_version.split()[1]}")
        else:
            self.print_error("pip未找到")
            all_passed = False

        # 检查网络连接
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                self.print_success("网络连接正常")
            else:
                self.print_warning("网络连接可能不稳定")
        except:
            self.print_warning("无法检测网络连接")

        # 检查FFmpeg
        success, ffmpeg_version = self.run_command(["ffmpeg", "-version"])
        if success:
            version_line = ffmpeg_version.split('\n')[0]
            self.print_success(f"FFmpeg已安装: {version_line}")
        else:
            self.print_warning("FFmpeg未找到")
            self.print_info("某些视频处理功能可能不可用")

        return all_passed

    def create_api_keys_file(self):
        """创建API密钥配置文件"""
        if self.api_keys_file.exists():
            self.print_info("API密钥文件已存在")
            return

        if self.api_keys_example.exists():
            # 复制示例文件
            with open(self.api_keys_example, 'r', encoding='utf-8') as f:
                content = f.read()

            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.print_success(f"已创建API密钥配置文件: {self.api_keys_file}")
        else:
            # 创建基本配置文件
            basic_config = {
                'openai': {'api_key': ''},
                'anthropic': {'api_key': ''},
                'google': {'api_key': '', 'project_id': ''},
                'azure': {'api_key': '', 'endpoint': '', 'region': ''},
                'deepseek': {'api_key': ''},
                'ollama': {'base_url': 'http://localhost:11434/v1'}
            }

            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                yaml.dump(basic_config, f, default_flow_style=False, allow_unicode=True)

            self.print_success(f"已创建基本API密钥配置文件: {self.api_keys_file}")

    def configure_deepseek(self):
        """配置DeepSeek"""
        self.print_header("配置 DeepSeek AI")

        print("DeepSeek是一个高性价比的AI翻译服务")
        print("官网: https://platform.deepseek.com/")
        print()

        # 检查是否已配置
        if os.getenv('DEEPSEEK_API_KEY'):
            self.print_success("DeepSeek API密钥已通过环境变量配置")
            return True

        # 交互式配置
        print("请按照以下步骤获取DeepSeek API密钥:")
        print("1. 访问 https://platform.deepseek.com/api_keys")
        print("2. 注册/登录账户")
        print("3. 创建新的API密钥")
        print("4. 复制API密钥")
        print()

        api_key = input("请输入您的DeepSeek API密钥 (或按Enter跳过): ").strip()

        if not api_key:
            self.print_warning("跳过DeepSeek配置")
            return False

        if not api_key.startswith('sk-'):
            self.print_warning("API密钥格式可能不正确，但仍会保存")

        # 测试API密钥
        if self.test_deepseek_connection(api_key):
            # 保存到配置文件
            self.save_api_key('deepseek', {'api_key': api_key})
            self.print_success("DeepSeek配置成功!")
            return True
        else:
            self.print_error("DeepSeek API密钥测试失败")
            save_anyway = input("是否仍要保存此密钥? (y/N): ").lower() == 'y'
            if save_anyway:
                self.save_api_key('deepseek', {'api_key': api_key})
                self.print_warning("已保存DeepSeek API密钥（未验证）")
            return False

    def test_deepseek_connection(self, api_key: str) -> bool:
        """测试DeepSeek连接"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'deepseek-chat',
                'messages': [{'role': 'user', 'content': 'Hello'}],
                'max_tokens': 10
            }

            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )

            return response.status_code == 200
        except:
            return False

    def configure_ollama(self):
        """配置Ollama"""
        self.print_header("配置 Ollama (本地AI)")

        print("Ollama是本地部署的开源AI模型服务")
        print("优势: 离线使用、隐私保护、无API费用")
        print("官网: https://ollama.ai/")
        print()

        # 检查Ollama是否已安装
        success, version = self.run_command(['ollama', '--version'])
        if success:
            self.print_success(f"Ollama已安装: {version}")
            return self.setup_ollama_models()
        else:
            self.print_warning("Ollama未安装")
            return self.install_ollama()

    def install_ollama(self) -> bool:
        """安装Ollama"""
        print("是否要安装Ollama? (推荐)")
        print("安装方法:")

        system = sys.platform
        if system.startswith('linux') or system.startswith('darwin'):
            print("Linux/macOS: curl -fsSL https://ollama.ai/install.sh | sh")
        elif system.startswith('win'):
            print("Windows: 下载安装包 https://ollama.ai/download/windows")

        print()
        install = input("是否现在安装Ollama? (y/N): ").lower() == 'y'

        if not install:
            self.print_info("跳过Ollama安装")
            return False

        if system.startswith('linux') or system.startswith('darwin'):
            print("正在安装Ollama...")
            success, output = self.run_command(['curl', '-fsSL', 'https://ollama.ai/install.sh'], False)
            if success:
                success, _ = self.run_command(['sh'], False)
                if success:
                    self.print_success("Ollama安装成功!")
                    return self.setup_ollama_models()
                else:
                    self.print_error("Ollama安装失败")
                    return False
            else:
                self.print_error("无法下载Ollama安装脚本")
                return False
        else:
            self.print_info("请手动下载安装包: https://ollama.ai/download/windows")
            return False

    def setup_ollama_models(self) -> bool:
        """设置Ollama模型"""
        # 检查Ollama服务是否运行
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    self.print_success(f"Ollama服务运行中，已安装{len(models)}个模型")
                    for model in models[:3]:  # 显示前3个模型
                        print(f"  - {model['name']}")
                    return True
        except:
            pass

        self.print_warning("Ollama服务未运行或无已安装模型")

        start_service = input("是否启动Ollama服务并安装推荐模型? (y/N): ").lower() == 'y'
        if not start_service:
            self.print_info("跳过Ollama模型安装")
            return False

        # 推荐的模型列表
        recommended_models = [
            ('llama2', '基础对话模型 (3.8GB)', True),
            ('qwen', '通义千问中文模型 (4.1GB)', True),
            ('mistral', 'Mistral高质量模型 (4.1GB)', False),
            ('codellama', '代码专用模型 (3.8GB)', False)
        ]

        print("\n推荐安装的模型:")
        for i, (model, desc, default) in enumerate(recommended_models, 1):
            status = "✅" if default else "  "
            print(f"{status} {i}. {model}: {desc}")

        print("\n选择要安装的模型 (输入序号，用空格分隔，如: 1 2):")
        choice = input("模型选择 (默认: 1 2): ").strip()

        if not choice:
            choice = "1 2"

        try:
            indices = [int(x) - 1 for x in choice.split()]
            selected_models = [recommended_models[i][0] for i in indices if 0 <= i < len(recommended_models)]
        except:
            selected_models = ['llama2', 'qwen']

        # 启动Ollama服务
        print("\n正在启动Ollama服务...")
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)  # 等待服务启动

        # 安装选中的模型
        success_count = 0
        for model in selected_models:
            print(f"\n正在安装模型: {model}")
            print("注意: 首次安装需要几分钟下载时间...")

            success, output = self.run_command(['ollama', 'pull', model], False)
            if success:
                self.print_success(f"模型 {model} 安装成功")
                success_count += 1
            else:
                self.print_error(f"模型 {model} 安装失败")

        if success_count > 0:
            self.print_success(f"成功安装 {success_count} 个模型")
            self.save_api_key('ollama', {'base_url': 'http://localhost:11434/v1'})
            return True
        else:
            self.print_error("未能安装任何模型")
            return False

    def save_api_key(self, provider: str, config: Dict):
        """保存API密钥到配置文件"""
        try:
            if self.api_keys_file.exists():
                with open(self.api_keys_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
            else:
                data = {}

            data[provider] = config

            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)

        except Exception as e:
            self.print_error(f"保存配置失败: {e}")

    def test_all_platforms(self):
        """测试所有平台"""
        self.print_header("测试AI平台连接")

        # 导入测试模块
        try:
            sys.path.insert(0, str(self.project_root))
            from test_providers import ProviderTester

            print("正在运行完整的平台测试...")
            print("这可能需要几分钟时间...")
            print()

            # 异步运行测试
            import asyncio
            tester = ProviderTester()
            asyncio.run(tester.test_all_providers())

        except ImportError as e:
            self.print_error(f"无法导入测试模块: {e}")
            self.print_info("请确保所有依赖已安装: pip install -r requirements.txt")
        except Exception as e:
            self.print_error(f"测试过程中发生错误: {e}")

    def interactive_setup(self):
        """交互式设置"""
        self.print_header("🚀 AI平台快速配置向导")

        print("欢迎使用视频翻译器AI平台配置向导!")
        print("此工具将帮助您配置DeepSeek和Ollama等新增AI平台")
        print()

        # 系统检查
        if not self.check_system_requirements():
            print("\n系统要求检查未完全通过，但可以继续配置")
            continue_setup = input("是否继续? (y/N): ").lower() == 'y'
            if not continue_setup:
                return

        # 创建配置文件
        self.create_api_keys_file()

        # 配置选项
        print("\n请选择要配置的AI平台:")
        print("1. DeepSeek AI (推荐，高性价比)")
        print("2. Ollama (本地部署，完全免费)")
        print("3. 两者都配置")
        print("4. 跳过配置，直接测试现有平台")

        choice = input("\n请选择 (1-4): ").strip()

        deepseek_configured = False
        ollama_configured = False

        if choice in ['1', '3']:
            deepseek_configured = self.configure_deepseek()

        if choice in ['2', '3']:
            ollama_configured = self.configure_ollama()

        # 配置完成总结
        self.print_header("配置完成")

        if choice == '4' or deepseek_configured or ollama_configured:
            print("配置状态:")
            if deepseek_configured:
                self.print_success("DeepSeek: 已配置")
            if ollama_configured:
                self.print_success("Ollama: 已配置")

            # 询问是否运行测试
            run_test = input("\n是否运行平台连接测试? (Y/n): ").lower() != 'n'
            if run_test:
                self.test_all_platforms()

        # 使用指南
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}🎉 配置完成!{Colors.ENDC}")
        print(f"\n下一步:")
        print(f"1. 启动应用: python run.py")
        print(f"2. 测试翻译: python test_providers.py")
        print(f"3. 查看文档: README.md")

        if deepseek_configured or ollama_configured:
            print(f"\n🆕 新平台使用提示:")
            if deepseek_configured:
                print(f"- DeepSeek: 高质量中文翻译，成本低廉")
            if ollama_configured:
                print(f"- Ollama: 完全离线，隐私保护，适合敏感内容")

def main():
    """主函数"""
    setup = PlatformSetup()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'deepseek':
            setup.configure_deepseek()
        elif command == 'ollama':
            setup.configure_ollama()
        elif command == 'test':
            setup.test_all_platforms()
        elif command == 'check':
            setup.check_system_requirements()
        else:
            print("用法: python setup_platforms.py [deepseek|ollama|test|check]")
            print("或直接运行进入交互模式: python setup_platforms.py")
    else:
        # 交互式设置
        setup.interactive_setup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⏹️  设置被用户中断{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}💥 设置过程中发生错误: {e}{Colors.ENDC}")
        sys.exit(1)
