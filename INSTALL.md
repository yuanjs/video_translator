# 视频翻译器安装指南
# Video Translator Installation Guide

本文档将指导您完成视频翻译器的安装和配置过程。

## 📋 系统要求

### 最低要求
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+ (或其他Linux发行版)
- **Python**: 3.8 或更高版本
- **内存**: 2GB RAM (推荐4GB+)
- **存储空间**: 500MB 可用空间
- **网络**: 用于下载依赖和API调用

### 必需组件
- **FFmpeg**: 用于视频处理和字幕提取
- **Python pip**: 用于安装Python包

### 推荐配置
- **Python**: 3.9 或 3.10 (最佳兼容性)
- **内存**: 8GB+ RAM (处理大视频文件)
- **存储**: SSD硬盘 (提升处理速度)

## 🛠️ 环境准备

### 1. 安装Python

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/windows/)
2. 下载最新的Python 3.8+ 安装程序
3. 运行安装程序，**务必选择 "Add Python to PATH"**
4. 验证安装：
   ```cmd
   python --version
   pip --version
   ```

#### macOS
**方法1: 官方安装程序**
1. 访问 [Python官网](https://www.python.org/downloads/macos/)
2. 下载并安装最新版本

**方法2: 使用Homebrew**
```bash
# 安装Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python
brew install python@3.10
```

#### Linux (Ubuntu/Debian)
```bash
# 更新包列表
sudo apt update

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv

# 安装tkinter (某些发行版需要单独安装)
sudo apt install python3-tk
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip python3-tkinter

# Fedora
sudo dnf install python3 python3-pip python3-tkinter
```

### 2. 安装FFmpeg

#### Windows
**方法1: 使用Chocolatey (推荐)**
```cmd
# 先安装Chocolatey (以管理员身份运行PowerShell)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# 安装FFmpeg
choco install ffmpeg
```

**方法2: 手动安装**
1. 访问 [FFmpeg官网](https://ffmpeg.org/download.html#build-windows)
2. 下载预编译的Windows版本
3. 解压到任意目录 (如 `C:\ffmpeg`)
4. 将 `C:\ffmpeg\bin` 添加到系统PATH环境变量

#### macOS
**使用Homebrew (推荐):**
```bash
brew install ffmpeg
```

**使用MacPorts:**
```bash
sudo port install ffmpeg
```

#### Linux
**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL:**
```bash
# 启用EPEL和RPM Fusion仓库
sudo yum install epel-release
sudo yum localinstall --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-7.noarch.rpm

sudo yum install ffmpeg ffmpeg-devel
```

**Fedora:**
```bash
sudo dnf install ffmpeg ffmpeg-devel
```

### 3. 验证环境
运行以下命令验证环境是否正确配置：

```bash
# 检查Python版本 (应该是3.8+)
python --version

# 检查pip
pip --version

# 检查FFmpeg
ffmpeg -version

# 检查tkinter (Python图形界面库)
python -c "import tkinter; print('tkinter OK')"
```

## 📥 下载和安装

### 1. 获取项目文件

**方法1: 下载ZIP文件**
1. 从项目页面下载ZIP文件
2. 解压到所需目录

**方法2: 使用Git (如果已安装)**
```bash
git clone [项目地址]
cd video_translator
```

### 2. 创建虚拟环境 (推荐)

```bash
# 进入项目目录
cd video_translator

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. 安装Python依赖

```bash
# 确保pip是最新版本
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

**如果安装失败，尝试:**
```bash
# 清理pip缓存
pip cache purge

# 使用国内镜像源 (中国用户)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者逐个安装关键依赖
pip install ttkthemes pillow ffmpeg-python pysrt webvtt-py
pip install openai anthropic google-cloud-translate requests
pip install PyYAML tqdm colorama python-dotenv
```

## ⚙️ 配置

### 1. 配置API密钥

```bash
# 复制环境变量模板
cp .env.template .env

# 编辑.env文件
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env 或 gedit .env
```

在 `.env` 文件中配置至少一个AI服务的API密钥：

```env
# OpenAI API密钥 (推荐)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude API密钥
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Cloud Translation (需要服务账户JSON文件)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Azure Translator
AZURE_TRANSLATOR_KEY=your_azure_key_here
AZURE_TRANSLATOR_REGION=your_region_here

# DeepSeek API密钥 (新增)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Ollama (本地部署，无需API密钥)
# 确保Ollama服务运行在默认端口
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### 2. API密钥获取方法

#### OpenAI API密钥
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账户
3. 转到 API Keys 页面
4. 创建新的API密钥
5. 复制密钥到 `.env` 文件

#### Anthropic Claude API密钥
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账户
3. 创建API密钥
4. 复制到 `.env` 文件

#### Google Cloud Translation
1. 创建 [Google Cloud项目](https://console.cloud.google.com/)
2. 启用 Translation API
3. 创建服务账户
4. 下载JSON密钥文件
5. 将文件路径填入 `.env`

#### Azure Translator
1. 在 [Azure Portal](https://portal.azure.com/) 创建Translator资源
2. 获取密钥和区域信息

#### DeepSeek API密钥 (新增)
1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/api_keys)
2. 注册/登录账户
3. 创建新的API密钥
4. 复制密钥到 `.env` 文件
5. 注意：DeepSeek提供高性价比的AI翻译服务

#### Ollama 本地部署 (新增)
**优势：**
- 完全离线运行，无需API密钥
- 隐私保护，数据不上传
- 支持多种开源模型
- 一次安装，永久使用

**安装步骤：**

1. **安装Ollama**
   ```bash
   # Linux/macOS
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # 下载安装包：https://ollama.ai/download/windows
   ```

2. **启动Ollama服务**
   ```bash
   # 启动服务
   ollama serve
   ```

3. **安装翻译模型**
   ```bash
   # 推荐的翻译模型
   ollama pull llama2        # 基础模型 (3.8GB)
   ollama pull qwen          # 通义千问 (适合中文, 4.1GB)
   ollama pull mistral       # Mistral模型 (4.1GB)
   
   # 高级模型（需要更多内存）
   ollama pull llama2:13b    # 13B参数版本 (7.3GB)
   ollama pull codellama     # 代码翻译专用 (3.8GB)
   ```

4. **验证安装**
   ```bash
   # 测试模型
   ollama run llama2 "Translate: Hello World"
   
   # 查看已安装模型
   ollama list
   ```

5. **配置要求**
   - 最低8GB RAM (推荐16GB+)
   - 每个模型需要3-8GB存储空间
   - 首次下载模型需要稳定网络连接
3. 填入 `.env` 文件

## ✅ 验证安装

### 1. 运行系统检查
```bash
python run.py --check
```

### 2. 运行基本测试
```bash
python test_basic.py
```

### 3. 启动应用
```bash
# 图形界面
python run.py

# 命令行测试
python run.py --cli --list-providers
```

## 🚨 常见问题解决

### Python相关问题

**问题: "python不是内部或外部命令"**
- **解决**: 确保Python已添加到系统PATH
- **Windows**: 重新安装Python，选择"Add Python to PATH"
- **验证**: 重启命令提示符，运行 `python --version`

**问题: 权限错误**
```bash
# 使用用户目录安装
pip install --user -r requirements.txt

# 或者在虚拟环境中安装
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### FFmpeg相关问题

**问题: "ffmpeg不是内部或外部命令"**
- **解决**: 确保FFmpeg已正确安装并添加到PATH
- **验证**: 运行 `ffmpeg -version`

**Windows用户快速修复:**
```cmd
# 下载并解压FFmpeg到C:\ffmpeg
# 添加C:\ffmpeg\bin到系统PATH
# 重启命令提示符测试
```

### 依赖安装问题

**问题: tkinter导入失败**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# macOS (通常已包含)
# 如果有问题，重新安装Python
```

**问题: SSL证书错误**
```bash
# 升级证书
pip install --upgrade certifi

# 或使用不验证SSL (不推荐)
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### API配置问题

**问题: API密钥无效**
- 检查密钥是否正确复制 (无多余空格)
- 确认密钥是否已激活
- 检查账户余额/配额

**问题: 网络连接失败**
- 检查网络连接
- 如在中国大陆，可能需要配置代理
- 某些API在特定地区可能受限

### 性能问题

**问题: 处理速度慢**
- 确保使用SSD硬盘
- 增加系统内存
- 选择较快的AI模型 (如gpt-3.5-turbo而非gpt-4)

**问题: 内存不足**
- 减少批处理大小
- 处理较短的视频文件
- 关闭其他应用程序

## 🔧 高级配置

### 1. 自定义配置文件
编辑 `config.yaml` 以自定义应用行为：

```yaml
translation:
  provider: "openai"          # 默认翻译提供商
  target_language: "zh-CN"    # 默认目标语言
  batch_size: 5               # 减少并发数以节省资源

ui:
  theme: "arc"                # 界面主题
  window_size: "1000x700"     # 窗口大小
```

### 2. 代理配置
如需使用代理，可在 `.env` 中添加：

```env
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=https://proxy.example.com:8080
```

### 3. 日志配置
调整日志级别以获得更多调试信息：

```yaml
logging:
  level: "DEBUG"              # 详细日志
  enable_console: true        # 控制台输出
```

## 📝 安装完成检查清单

- [ ] Python 3.8+ 已安装并可在命令行访问
- [ ] FFmpeg 已安装并可在命令行访问
- [ ] 项目依赖已成功安装
- [ ] `.env` 文件已创建并配置了至少一个API密钥
- [ ] 系统检查通过 (`python run.py --check`)
- [ ] 基本测试通过 (`python test_basic.py`)
- [ ] 应用可以正常启动 (`python run.py`)

## 🆘 获取帮助

如果在安装过程中遇到问题：

1. **查看日志**: 检查 `logs/app.log` 中的错误信息
2. **运行诊断**: `python run.py --check`
3. **搜索文档**: 查看 `README.md` 中的故障排除部分
4. **系统信息**: 记录操作系统、Python版本等信息
5. **提交Issue**: 在项目页面报告问题

## 🎉 安装成功！

恭喜！您已成功安装视频翻译器。现在可以：

- 运行 `python run.py` 启动图形界面
- 运行 `python run.py --cli --help` 查看命令行选项
- 查看 `README.md` 了解详细使用说明

祝您使用愉快！