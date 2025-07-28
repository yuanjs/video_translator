# 🔧 依赖安装指南
# Dependency Installation Guide

本指南帮助你解决视频翻译器项目中的依赖安装问题，提供多种安装策略和故障排除方案。

## 📋 依赖安装策略

### 🎯 推荐安装顺序

#### 1. 最小依赖（推荐首选）
```bash
# 安装核心功能，最稳定
pip install -r requirements-minimal.txt
```

**包含功能**:
- ✅ OpenAI, Anthropic, DeepSeek, Ollama 翻译
- ✅ 视频处理和字幕提取
- ✅ 命令行界面
- ✅ 基本图形界面支持（无主题）

#### 2. 核心依赖（功能较全）
```bash
# 安装大部分功能
pip install -r requirements-core.txt
```

**额外功能**:
- ✅ Google Cloud Translation（需额外配置）
- ✅ 更多字幕格式支持

#### 3. 完整依赖（可选）
```bash
# 安装所有功能（可能遇到兼容性问题）
pip install -r requirements.txt
```

**额外功能**:
- ✅ 图形界面主题
- ✅ 开发工具
- ✅ 测试框架

## 🔍 常见依赖问题解决

### 问题1: Azure翻译依赖错误

**错误信息**:
```
ERROR: Could not find a version that satisfies the requirement azure-cognitiveservices-language-translation
```

**解决方案**:
```bash
# 方案1: 使用REST API（已内置，无需额外安装）
# Azure翻译器已更新为使用REST API，不需要特定SDK

# 方案2: 如果需要新版Azure SDK
pip install azure-ai-translation-text>=1.0.0

# 方案3: 跳过Azure，使用其他平台
# 在config.yaml中禁用Azure或使用其他翻译服务
```

### 问题2: Google Cloud依赖问题

**错误信息**:
```
ImportError: No module named 'google.cloud'
```

**解决方案**:
```bash
# 方案1: 安装Google Cloud SDK
pip install google-cloud-translate>=3.12.0

# 方案2: 设置服务账户
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# 方案3: 跳过Google Cloud
# 使用其他翻译服务，如DeepSeek或Ollama
```

### 问题3: GUI依赖问题（Linux）

**错误信息**:
```
ImportError: libtk8.6.so: cannot open shared object file
```

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# 或使用纯命令行模式
python run.py --cli  # 跳过GUI依赖
```

### 问题4: FFmpeg依赖问题

**错误信息**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载FFmpeg并添加到PATH，或使用chocolatey:
# choco install ffmpeg

# 临时解决：设置FFmpeg路径
export FFMPEG_PATH="/path/to/ffmpeg"
```

## 📦 分层安装策略

### 第1层：核心翻译功能
```bash
pip install openai anthropic requests PyYAML python-dotenv tqdm rich
```

### 第2层：视频处理
```bash
pip install ffmpeg-python pysrt webvtt-py pysubs2
```

### 第3层：增强功能
```bash
pip install aiohttp httpx psutil colorama pathvalidate
```

### 第4层：可选服务
```bash
# Google Cloud (可选)
pip install google-cloud-translate

# Azure AI (可选)  
pip install azure-ai-translation-text

# GUI主题 (可选)
pip install ttkthemes Pillow
```

## 🌍 平台特定解决方案

### Linux系统

#### Ubuntu/Debian
```bash
# 系统依赖
sudo apt update
sudo apt install python3-dev python3-venv python3-tk ffmpeg

# Python依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

#### CentOS/RHEL
```bash
# 系统依赖
sudo yum install python3-devel python3-tkinter ffmpeg

# 或使用dnf (新版本)
sudo dnf install python3-devel python3-tkinter ffmpeg
```

### macOS系统

```bash
# 使用Homebrew
brew install python ffmpeg

# 如果遇到SSL问题
/Applications/Python\ 3.x/Install\ Certificates.command

# Python依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

### Windows系统

```batch
REM 确保Python和pip正确安装
python --version
pip --version

REM 如果遇到权限问题，以管理员身份运行
pip install --user -r requirements-minimal.txt

REM 或使用虚拟环境
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements-minimal.txt
```

## 🔄 故障排除工作流

### 步骤1: 环境诊断
```bash
# 检查Python版本
python --version  # 需要3.8+

# 检查pip版本
pip --version

# 检查虚拟环境
echo $VIRTUAL_ENV  # 应该指向项目的venv目录
```

### 步骤2: 清理和重试
```bash
# 清理pip缓存
pip cache purge

# 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 重新安装
pip install -r requirements-minimal.txt
```

### 步骤3: 逐步安装
```bash
# 逐个安装核心包，识别问题包
pip install openai
pip install anthropic
pip install requests
pip install PyYAML
# ... 继续其他包
```

### 步骤4: 替代方案
```bash
# 如果某个包失败，找替代品
# 例如：用requests替代httpx
# 或跳过可选功能
```

## 🚀 快速修复命令集

### 修复1: 最小可用环境
```bash
# 创建最小工作环境
python -m venv venv-minimal
source venv-minimal/bin/activate  # Linux/Mac
pip install openai anthropic requests PyYAML python-dotenv
pip install ffmpeg-python pysrt tqdm rich click
```

### 修复2: 无GUI环境
```bash
# 纯命令行环境
pip install -r requirements-minimal.txt
python run.py --cli  # 启动命令行模式
```

### 修复3: 本地AI环境
```bash
# 只安装Ollama支持，完全本地化
pip install requests PyYAML python-dotenv tqdm rich
# 然后安装Ollama: curl -fsSL https://ollama.ai/install.sh | sh
```

## 📊 依赖兼容性矩阵

| 平台 | Python 3.8 | Python 3.9 | Python 3.10 | Python 3.11 | Python 3.12+ |
|------|-------------|-------------|--------------|--------------|---------------|
| Windows 10+ | ✅ | ✅ | ✅ | ✅ | ✅ |
| macOS 10.14+ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Ubuntu 18.04+ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CentOS 7+ | ✅ | ✅ | ✅ | ⚠️ | ❌ |

**图例**: ✅ 完全支持 | ⚠️ 部分兼容问题 | ❌ 不支持

## 🔧 自定义依赖配置

### 创建你的requirements文件
```bash
# 基于成功安装的包创建
pip freeze > my-requirements.txt

# 手动创建最小集合
cat > my-minimal.txt << EOF
openai>=1.12.0
anthropic>=0.7.0  
requests>=2.31.0
PyYAML>=6.0.0
python-dotenv>=1.0.0
tqdm>=4.66.0
rich>=13.0.0
EOF
```

### 条件依赖安装
```bash
# 只在特定条件下安装
if command -v ffmpeg &> /dev/null; then
    pip install ffmpeg-python
else
    echo "FFmpeg not found, skipping video processing"
fi
```

## 🆘 最后手段解决方案

### 方案1: Docker容器（推荐）
```dockerfile
# 使用预配置的Docker环境
# 参考项目中的Dockerfile（如果提供）
```

### 方案2: 在线服务
```bash
# 使用Google Colab或其他在线Python环境
# 上传项目文件并在线运行
```

### 方案3: 降级策略
```bash
# 使用较旧但稳定的包版本
pip install openai==1.3.0 anthropic==0.7.0 requests==2.28.0
```

## 📞 获取帮助

### 诊断信息收集
```bash
# 运行诊断脚本
python manage_env.py check

# 生成环境报告
pip list > installed_packages.txt
python --version > python_info.txt
uname -a > system_info.txt  # Linux/Mac
```

### 社区支持
1. 查看项目GitHub Issues
2. 搜索相似错误信息
3. 提交包含诊断信息的新Issue

### 替代方案
如果所有依赖都无法解决：
1. 使用纯API方式调用翻译服务
2. 使用在线翻译工具的API
3. 考虑使用项目的Docker版本

---

## 🎯 成功安装检查清单

- [ ] Python 3.8+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 至少一个requirements文件安装成功
- [ ] 核心模块可以导入：`from src.core.translator import TranslationManager`
- [ ] 至少一个AI平台可用
- [ ] 基本功能测试通过：`python test_providers.py check`

完成以上步骤后，你就可以开始使用视频翻译器了！

**记住**: 即使某些依赖失败，只要核心翻译功能可用，项目仍然可以正常工作。优先确保OpenAI、Anthropic、DeepSeek或Ollama中至少一个平台可用。