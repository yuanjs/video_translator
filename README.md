# 视频翻译器 (Video Translator)

一个功能强大的视频字幕提取和翻译工具，支持批量处理视频文件，利用AI平台进行高质量翻译。

## 功能特性

### 📹 视频文件处理
- 支持单个视频文件翻译
- 支持批量处理目录下所有视频文件
- 支持多选视频文件处理
- 支持常见视频格式：MP4, AVI, MKV, MOV, WMV, FLV等

### 📝 字幕处理
- 自动检测并提取视频内嵌字幕
- 支持多种字幕格式：SRT, VTT, ASS, SSA
- 可选择特定语言轨道进行提取
- 支持外挂字幕文件导入

### 🤖 AI翻译支持
- **OpenAI GPT**：支持GPT-3.5和GPT-4模型
- **Anthropic Claude**：支持Claude-3系列模型
- **Google Translate**：支持Google Cloud Translation API
- **Azure Translator**：支持Microsoft Azure翻译服务
- **DeepSeek**：支持DeepSeek-Chat和DeepSeek-Coder模型 🆕
- **Ollama**：支持本地部署的开源大语言模型 🆕
- 智能分段翻译，保持上下文连贯性

### 🌐 翻译选项
- **目标语言**：默认简体中文，支持50+语言
- **输出格式**：
  - 双语字幕（原文+译文）
  - 单语字幕（仅译文）
  - 可自定义字幕样式和格式

### 🎨 用户界面
- 现代化GUI界面，支持深色/浅色主题
- 实时翻译进度显示
- 批量任务管理
- 错误日志和状态监控

## 快速开始

### 1. 环境准备
```bash
# 确保Python 3.8+已安装
python --version

# 确保FFmpeg已安装
ffmpeg -version
```

### 2. 安装依赖
```bash
# 克隆或下载项目
cd video_translator

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置API密钥
```bash
# 复制API密钥配置模板
cp api_keys_example.yaml api_keys.yaml

# 编辑api_keys.yaml文件，填入您的API密钥
# 至少需要配置一个AI翻译服务的API密钥

# 或者使用环境变量方式
export OPENAI_API_KEY="your-openai-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
# Ollama无需API密钥，但需要本地服务运行
```

### 4. 开始使用

**图形界面模式：**
```bash
python run.py
```

**命令行模式：**
```bash
# 翻译单个视频文件
python run.py --cli -i your_video.mp4 -l zh-CN

# 批量翻译目录
python run.py --cli --input-dir /path/to/videos -l zh-CN
```

### 5. 首次使用提示
- 确保视频文件包含字幕轨道
- 首次翻译建议使用较短的视频进行测试
- 检查输出目录中生成的字幕文件

---

## 详细安装说明

### 系统要求
- Python 3.8+
- FFmpeg（用于视频处理）
- 2GB+ 可用内存

### 安装FFmpeg

**Windows:**
```bash
# 使用chocolatey
choco install ffmpeg

# 或下载预编译版本
# https://ffmpeg.org/download.html#build-windows
```

**macOS:**
```bash
# 使用Homebrew
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 安装Python依赖

```bash
# 克隆项目
git clone <repository-url>
cd video_translator

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 配置说明

### API密钥配置

创建 `.env` 文件并配置您的API密钥：

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google Cloud Translation API
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json

# Azure Translator API
AZURE_TRANSLATOR_KEY=your_azure_key
AZURE_TRANSLATOR_REGION=your_region

# DeepSeek API (新增)
DEEPSEEK_API_KEY=your_deepseek_api_key

# Ollama (本地部署，无需API密钥)
# 确保Ollama服务运行在 http://localhost:11434
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### 配置文件

应用会自动创建 `config.yaml` 配置文件，您可以自定义：

```yaml
# 默认翻译设置
translation:
  target_language: "zh-CN"  # 目标语言
  provider: "openai"        # AI翻译提供商 (openai/anthropic/google/azure/deepseek/ollama)
  model: "gpt-3.5-turbo"   # 使用的模型
  output_format: "bilingual" # 输出格式：bilingual/monolingual

# API配置
api:
  # DeepSeek配置
  deepseek:
    base_url: "https://api.deepseek.com/v1"
    models:
      - "deepseek-chat"
      - "deepseek-coder"
  
  # Ollama配置 (本地部署)
  ollama:
    base_url: "http://localhost:11434/v1"
    models:
      - "llama2"
      - "llama2:13b"
      - "codellama"
      - "mistral"
      - "qwen"
      - "gemma"
```
  
# 字幕设置
subtitle:
  max_chars_per_line: 50    # 每行最大字符数
  max_lines: 2              # 最大行数
  sync_tolerance: 0.1       # 时间同步容差（秒）

# 界面设置
ui:
  theme: "arc"              # 主题名称
  language: "zh_CN"         # 界面语言
```

## 使用指南

### 启动应用

**推荐方式（使用启动脚本）：**
```bash
# 启动图形界面
python run.py

# 启动命令行界面
python run.py --cli

# 检查系统环境
python run.py --check

# 显示版本信息
python run.py --version
```

**直接启动：**
```bash
# 图形界面
python src/main.py

# 命令行界面
python src/cli.py --help
```

### 基本操作流程

1. **选择视频文件**
   - 单文件：点击"选择视频文件"
   - 批量处理：点击"选择文件夹"
   - 多选文件：按住Ctrl/Cmd选择多个文件

2. **配置翻译选项**
   - 选择AI翻译提供商
   - 设置目标语言
   - 选择输出格式（双语/单语）

3. **字幕处理选项**
   - 如果视频有多个字幕轨道，选择要翻译的轨道
   - 设置字幕文件输出路径

4. **开始翻译**
   - 点击"开始翻译"按钮
   - 实时查看翻译进度
   - 翻译完成后自动保存字幕文件

### 命令行使用

```bash
# 翻译单个视频
python run.py --cli -i video.mp4 -o translated.srt -l zh-CN

# 批量翻译目录
python run.py --cli --input-dir /path/to/videos --output-dir /path/to/output -l zh-CN

# 指定翻译提供商和模型
python run.py --cli -i video.mp4 --provider openai --model gpt-4 -l zh-CN

# 生成多种格式字幕
python run.py --cli -i video.mp4 --formats srt,vtt,ass -l zh-CN

# 查看视频信息
python run.py --cli --info video.mp4

# 列出可用的翻译提供商
python run.py --cli --list-providers

# 列出支持的语言
python run.py --cli --list-languages
```

## 支持的语言

目标语言支持包括但不限于：
- 中文（简体/繁体）
- 英语
- 日语
- 韩语
- 法语
- 德语
- 西班牙语
- 俄语
- 阿拉伯语
- 等50+种语言

## 故障排除

### 常见问题

**1. FFmpeg未找到**
```
确保FFmpeg已正确安装并添加到系统PATH中
```

**2. API密钥错误**
```
检查.env文件中的API密钥是否正确设置
验证API密钥是否有效且有足够的配额
```

**3. 字幕提取失败**
```
确认视频文件包含字幕轨道
尝试使用不同的字幕提取方法
检查视频文件是否损坏
```

**4. 翻译质量问题**
```
尝试使用不同的AI模型
调整翻译提示词
检查原字幕文本质量
```

### 日志文件

应用日志保存在 `logs/` 目录中：
- `app.log`：应用运行日志
- `translation.log`：翻译过程日志
- `error.log`：错误日志

## 测试与开发

### 运行测试
```bash
# 运行基本功能测试
python test_basic.py

# 运行特定测试类
python test_basic.py --specific TestConfigSystem

# 详细测试输出
python test_basic.py -v
```

### 开发环境设置
```bash
# 安装开发依赖
pip install pytest pytest-asyncio black flake8

# 代码格式化
black src/

# 代码检查
flake8 src/
```

## 开发说明

### 项目结构

```
video_translator/
├── src/
│   ├── main.py              # 应用入口
│   ├── cli.py               # 命令行界面
│   ├── gui/                 # GUI组件
│   │   ├── main_window.py   # 主窗口
│   │   ├── dialogs.py       # 对话框
│   │   └── widgets.py       # 自定义组件
│   ├── core/                # 核心功能
│   │   ├── video_processor.py   # 视频处理
│   │   ├── subtitle_extractor.py # 字幕提取
│   │   ├── translator.py        # 翻译引擎
│   │   └── subtitle_writer.py   # 字幕写入
│   └── utils/               # 工具函数
│       ├── config.py        # 配置管理
│       ├── logger.py        # 日志系统
│       └── helpers.py       # 辅助函数
├── tests/                   # 测试文件
├── docs/                    # 文档
├── config.yaml              # 配置文件
├── requirements.txt         # 依赖清单
└── README.md               # 项目说明
```

### 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 提交Pull Request

## 🆕 新增AI平台配置指南

### DeepSeek 配置

**1. 获取API密钥**
- 访问 [DeepSeek开放平台](https://platform.deepseek.com/api_keys)
- 注册并创建API密钥

**2. 配置密钥**
```bash
# 方式1：环境变量
export DEEPSEEK_API_KEY="sk-your-deepseek-api-key-here"

# 方式2：在api_keys.yaml中配置  
deepseek:
  api_key: "sk-your-deepseek-api-key-here"
```

**3. 使用DeepSeek**
```bash
# 在config.yaml中设置
translation:
  provider: "deepseek"
  model: "deepseek-chat"  # 或 "deepseek-coder"
```

### Ollama 本地部署配置

**1. 安装Ollama**
```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 下载安装包：https://ollama.ai/download/windows
```

**2. 启动Ollama服务**
```bash
# 启动Ollama服务
ollama serve

# 在新终端中拉取模型
ollama pull llama2        # 基础模型
ollama pull llama2:13b    # 13B参数版本
ollama pull qwen          # 通义千问
ollama pull mistral       # Mistral模型
```

**3. 验证安装**
```bash
# 测试模型
ollama run llama2 "Hello, how are you?"

# 查看已安装的模型
ollama list
```

**4. 配置使用**
```yaml
# config.yaml
translation:
  provider: "ollama"
  model: "llama2"  # 使用已安装的模型
  
api:
  ollama:
    base_url: "http://localhost:11434/v1"  # 默认地址
```

**注意事项：**
- Ollama无需API密钥，但需要本地运行服务
- 首次使用需要下载模型文件（几GB大小）
- 推荐至少8GB内存用于运行大模型
- 可以通过修改`base_url`连接远程Ollama服务

### 测试新平台

使用提供的测试脚本验证配置：

```bash
# 测试所有平台
python test_providers.py

# 测试特定平台
python test_providers.py deepseek
python test_providers.py ollama

# 检查配置状态
python test_providers.py check
```

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue：[GitHub Issues](issues-url)
- 邮箱：your-email@example.com

---

**注意**：使用本工具时请遵守相关视频内容的版权法律法规。