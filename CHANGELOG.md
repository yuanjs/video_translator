# 更新日志 / Changelog

本文档记录了视频翻译器项目的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [未发布] - Unreleased

### 计划中的功能
- [ ] 支持更多视频格式
- [ ] 实时字幕翻译
- [ ] 字幕质量评估
- [ ] 插件系统支持
- [ ] 语音识别集成
- [ ] 批量任务队列管理
- [ ] Web界面版本

## [1.0.0] - 2024-01-01

### 🎉 首次发布

#### 新增功能 Added
- **核心功能**
  - 视频字幕提取支持（支持内嵌字幕）
  - AI驱动的字幕翻译（OpenAI, Anthropic, Google, Azure）
  - 多种字幕格式支持（SRT, VTT, ASS）
  - 批量视频处理
  - 双语/单语字幕输出选择

- **用户界面**
  - 现代化GUI界面（基于tkinter和ttkthemes）
  - 完整的命令行界面（CLI）
  - 实时翻译进度显示
  - 详细的日志和错误报告

- **视频处理**
  - 支持主流视频格式（MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V）
  - 自动检测视频中的字幕轨道
  - 多字幕轨道提取支持
  - 视频信息分析和显示

- **翻译功能**
  - OpenAI GPT模型支持（GPT-3.5, GPT-4）
  - Anthropic Claude模型支持（Claude-3系列）
  - Google Cloud Translation API集成
  - Azure Translator服务集成
  - 智能上下文感知翻译
  - 批量翻译优化

- **配置系统**
  - YAML配置文件支持
  - 环境变量配置
  - 可自定义的翻译参数
  - 界面主题和语言设置

- **开发工具**
  - 完整的项目结构
  - 基本功能测试套件
  - 详细的文档和安装指南
  - 跨平台启动脚本

#### 支持的平台 Platforms
- Windows 10+ 
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+, Fedora 30+)

#### 支持的语言 Languages
- 简体中文 (zh-CN)
- 繁体中文 (zh-TW)
- English (en)
- 日本語 (ja)
- 한국어 (ko)
- Français (fr)
- Deutsch (de)
- Español (es)
- Русский (ru)
- العربية (ar)
- 以及其他40+种语言

#### 依赖要求 Requirements
- Python 3.8+
- FFmpeg
- 网络连接（用于API调用）
- 2GB+ RAM（推荐4GB+）

#### 技术架构 Technical Architecture
- **前端**: tkinter + ttkthemes
- **后端**: 异步处理 (asyncio)
- **视频处理**: FFmpeg + python-ffmpeg
- **字幕处理**: pysrt, webvtt-py
- **AI集成**: openai, anthropic, google-cloud-translate
- **配置管理**: PyYAML, python-dotenv
- **日志系统**: 结构化日志记录
- **测试**: unittest框架

#### 文档 Documentation
- 完整的README.md用户指南
- 详细的INSTALL.md安装指南
- API使用示例
- 故障排除指南
- 开发者文档

### ⚙️  配置选项 Configuration
- 默认目标语言: 简体中文 (zh-CN)
- 默认AI提供商: OpenAI
- 默认输出格式: 双语字幕
- 支持的字幕格式: SRT, VTT, ASS
- 可配置的批处理大小
- 自定义文件命名模板

### 🛠️ 技术特性 Technical Features
- 模块化架构设计
- 异步翻译处理
- 智能错误处理和重试机制
- 内存优化的批量处理
- 跨平台兼容性
- 详细的日志记录
- 配置热重载支持

### 📦 打包和分发 Packaging
- Python包依赖管理 (requirements.txt)
- 跨平台启动脚本 (run.py, run.bat)
- 环境配置模板 (.env.template)
- 自动化测试脚本 (test_basic.py)

---

## 版本说明 Version Notes

### 版本编号规则
- **主版本号**: 不兼容的API变更
- **次版本号**: 向下兼容的新功能
- **修订号**: 向下兼容的问题修复

### 变更类型说明
- **Added**: 新增功能
- **Changed**: 现有功能的变更
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 问题修复
- **Security**: 安全相关修复

### 支持政策
- 主要版本支持期: 12个月
- 安全更新支持期: 18个月
- LTS版本支持期: 24个月

---

## 贡献指南 Contributing

欢迎为项目贡献代码！请查看以下指南：

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型包括：
- `feat`: 新功能
- `fix`: 问题修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

---

## 致谢 Acknowledgments

感谢以下开源项目和服务：

- [FFmpeg](https://ffmpeg.org/) - 视频处理
- [tkinter](https://docs.python.org/3/library/tkinter.html) - GUI框架
- [OpenAI](https://openai.com/) - AI翻译服务
- [Anthropic](https://www.anthropic.com/) - Claude AI服务
- [Google Cloud](https://cloud.google.com/) - 翻译API
- [Microsoft Azure](https://azure.microsoft.com/) - 认知服务

以及所有贡献者和用户的支持！

---

**注意**: 本项目遵循 [MIT许可证](LICENSE)。使用时请遵守相关视频内容的版权法律法规。