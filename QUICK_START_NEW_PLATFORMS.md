# 🚀 新AI平台快速入门指南
# Quick Start Guide for New AI Platforms

本指南将帮助你快速配置和使用视频翻译器新增的DeepSeek和Ollama AI平台。

## 🆕 新增平台概览

### 🧠 DeepSeek AI
- **类型**: 云端AI服务
- **优势**: 高性价比，中文优化，快速响应
- **费用**: 按使用量付费，价格低廉
- **适用场景**: 高质量翻译需求，成本敏感项目

### 🏠 Ollama
- **类型**: 本地AI部署
- **优势**: 完全离线，隐私保护，免费使用
- **费用**: 完全免费（需要本地计算资源）
- **适用场景**: 隐私敏感内容，离线环境

## ⚡ 5分钟快速开始

### 方法1: 自动配置工具（推荐）

```bash
# 运行交互式配置工具
python setup_platforms.py

# 选择要配置的平台，按提示操作
# 工具会自动检测系统环境并引导你完成配置
```

### 方法2: 手动配置

#### 🧠 配置DeepSeek（2分钟）

1. **获取API密钥**
   - 访问 [DeepSeek开放平台](https://platform.deepseek.com/api_keys)
   - 注册账户并创建API密钥

2. **配置密钥**
   ```bash
   # 方式1: 环境变量（推荐）
   export DEEPSEEK_API_KEY="sk-your-deepseek-api-key-here"
   
   # 方式2: 配置文件
   cp api_keys_example.yaml api_keys.yaml
   # 编辑 api_keys.yaml，填入DeepSeek API密钥
   ```

3. **测试配置**
   ```bash
   python test_providers.py deepseek
   ```

#### 🏠 配置Ollama（5分钟）

1. **安装Ollama**
   ```bash
   # Linux/macOS
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows: 下载安装包
   # https://ollama.ai/download/windows
   ```

2. **启动服务并安装模型**
   ```bash
   # 启动Ollama服务
   ollama serve
   
   # 新开终端，安装推荐模型
   ollama pull llama2    # 基础模型 (3.8GB)
   ollama pull qwen      # 中文优化 (4.1GB)
   ```

3. **验证安装**
   ```bash
   # 测试模型
   ollama run llama2 "Translate to Chinese: Hello World"
   
   # 测试翻译功能
   python test_providers.py ollama
   ```

## 🎯 立即使用

### 命令行快速翻译

```bash
# 使用DeepSeek翻译
python run.py --cli -i your_video.mp4 -l zh-CN --provider deepseek

# 使用Ollama翻译
python run.py --cli -i your_video.mp4 -l zh-CN --provider ollama
```

### 图形界面使用

```bash
# 启动图形界面
python run.py

# 在界面中选择DeepSeek或Ollama作为翻译提供商
```

### 演示和测试

```bash
# 查看新平台演示
python demo_new_platforms.py

# 对比不同平台效果
python demo_new_platforms.py compare

# 测试所有平台
python test_providers.py
```

## ⚙️ 配置文件示例

### config.yaml 配置
```yaml
translation:
  provider: "deepseek"  # 或 "ollama"
  model: "deepseek-chat"  # DeepSeek
  # model: "llama2"       # Ollama
  target_language: "zh-CN"
```

### api_keys.yaml 配置
```yaml
# DeepSeek配置
deepseek:
  api_key: "sk-your-deepseek-api-key-here"

# Ollama配置（本地）
ollama:
  base_url: "http://localhost:11434/v1"
```

## 🔍 快速故障排除

### DeepSeek 问题

**问题**: API密钥无效
```bash
# 检查密钥格式
echo $DEEPSEEK_API_KEY  # 应该以 sk- 开头

# 重新设置
export DEEPSEEK_API_KEY="sk-your-correct-key"
```

**问题**: 网络连接失败
```bash
# 测试网络连接
curl -I https://api.deepseek.com

# 如果使用代理，设置代理环境变量
export https_proxy="http://your-proxy:port"
```

### Ollama 问题

**问题**: 服务未运行
```bash
# 检查服务状态
curl http://localhost:11434/api/tags

# 重启服务
ollama serve
```

**问题**: 模型未安装
```bash
# 查看已安装模型
ollama list

# 安装推荐模型
ollama pull llama2
ollama pull qwen
```

**问题**: 内存不足
```bash
# 使用较小的模型
ollama pull llama2:7b   # 而不是 llama2:13b

# 调整模型参数（在Ollama配置文件中）
# 减少context_length和batch_size
```

## 📊 性能对比参考

| 平台 | 速度 | 质量 | 成本 | 隐私 | 离线 |
|------|------|------|------|------|------|
| DeepSeek | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💰 | ⭐⭐ | ❌ |
| Ollama | ⚡⚡ | ⭐⭐⭐ | 免费 | ⭐⭐⭐⭐⭐ | ✅ |
| OpenAI | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰 | ⭐⭐ | ❌ |

## 🎓 进阶使用

### 批量翻译脚本
```bash
# 批量翻译整个目录，使用DeepSeek
python run.py --cli --input-dir ./videos --provider deepseek

# 使用Ollama处理敏感内容目录
python run.py --cli --input-dir ./private_videos --provider ollama
```

### 自定义模型配置
```yaml
# config.yaml - 使用特定模型
api:
  deepseek:
    models:
      - "deepseek-chat"
      - "deepseek-coder"  # 适合技术内容
  
  ollama:
    models:
      - "llama2"          # 通用翻译
      - "qwen"            # 中文优化
      - "mistral"         # 高质量翻译
```

## 🔗 有用链接

- **DeepSeek官网**: https://platform.deepseek.com/
- **Ollama官网**: https://ollama.ai/
- **模型下载**: https://ollama.ai/library
- **项目文档**: README.md
- **详细安装**: INSTALL.md

## 🆘 需要帮助？

1. **运行诊断**: `python test_providers.py check`
2. **查看日志**: 检查 `logs/app.log` 文件
3. **重置配置**: 删除 `config.yaml` 重新生成
4. **社区支持**: 查看项目 Issues 页面

## 🎉 成功使用检查清单

- [ ] ✅ 已安装Python 3.8+和FFmpeg
- [ ] ✅ 已安装项目依赖 (`pip install -r requirements.txt`)
- [ ] ✅ 已配置至少一个新平台（DeepSeek或Ollama）
- [ ] ✅ 测试通过 (`python test_providers.py`)
- [ ] ✅ 成功翻译测试视频

**恭喜！** 🎊 你已经成功配置了新的AI翻译平台，可以开始享受更高效、更经济的视频翻译体验了！

---

*💡 提示: 建议同时配置DeepSeek和Ollama，这样可以根据不同需求选择最合适的平台。DeepSeek适合高质量需求，Ollama适合隐私保护和离线使用。*