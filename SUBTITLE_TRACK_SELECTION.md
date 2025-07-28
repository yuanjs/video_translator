# 字幕轨道选择功能

## 概述

视频翻译器现在支持选择特定的字幕轨道进行翻译，而不是只能翻译第一个轨道。这个功能让用户能够：

- 查看视频中所有可用的字幕轨道
- 选择特定语言或类型的字幕轨道进行翻译
- 了解每个轨道的详细信息（语言、编码、标记等）

## 功能特性

### ✅ 新增功能

- **字幕轨道信息显示**：显示每个轨道的索引、标题、语言、编码格式
- **轨道状态标识**：标识默认轨道和强制字幕轨道
- **GUI轨道选择器**：下拉菜单选择要翻译的特定轨道
- **CLI轨道列表命令**：`--list-subtitles` 命令查看所有轨道
- **CLI轨道索引选择**：`--subtitle-index` 参数指定要翻译的轨道
- **智能轨道选择**：如果指定轨道不存在，提供明确的错误信息

### 📈 改进功能

- **提取所有轨道选项**：保留原有功能，可选择翻译所有轨道
- **更详细的视频信息**：在GUI和CLI中显示完整的轨道信息
- **更好的用户体验**：GUI界面动态启用/禁用相关控件

## GUI 使用方法

### 1. 选择视频文件
- 点击"选择文件"或"选择目录"按钮
- 选择包含多个字幕轨道的视频文件

### 2. 查看字幕轨道信息
- 在右侧信息面板查看视频的字幕轨道详情
- 每个轨道显示：索引、标题、语言、编码格式、特殊标记

### 3. 选择要翻译的轨道
#### 方式一：选择特定轨道
- 在"选择字幕轨道"下拉框中选择目标轨道
- 轨道显示格式：`轨道 X: 标题 (语言, 编码)`

#### 方式二：翻译所有轨道
- 勾选"提取所有字幕轨道"复选框
- 此时轨道选择下拉框会被禁用

### 4. 设置翻译参数
- 选择翻译提供商（OpenAI、Claude、Google等）
- 选择目标语言
- 选择输出格式

### 5. 开始翻译
- 点击"开始翻译"按钮
- 查看进度和日志信息

## CLI 使用方法

### 1. 查看视频的字幕轨道

```bash
# 列出视频中的所有字幕轨道
python src/cli.py --list-subtitles movie.mp4
```

输出示例：
```
字幕轨道列表: movie.mp4
============================================================
找到 3 个字幕轨道:

轨道 0:
  标题: English
  语言: en
  编码: subrip
  标记: 默认

轨道 1:
  标题: 简体中文
  语言: zh-CN
  编码: subrip

轨道 2:
  标题: Japanese
  语言: ja
  编码: ass
  标记: 强制

使用方法:
  python cli.py -i "movie.mp4" --subtitle-index <轨道索引> -o output.srt -l zh-CN
```

### 2. 查看视频的完整信息

```bash
# 显示视频的详细信息（包括字幕轨道）
python src/cli.py --info movie.mp4
```

### 3. 翻译特定轨道

```bash
# 翻译轨道 0（通常是默认轨道）
python src/cli.py -i movie.mp4 --subtitle-index 0 -o english.srt -l zh-CN

# 翻译轨道 2（日语轨道）
python src/cli.py -i movie.mp4 --subtitle-index 2 -o japanese.srt -l zh-CN
```

### 4. 翻译所有轨道

```bash
# 提取并翻译所有字幕轨道
python src/cli.py -i movie.mp4 --extract-all-subtitles --output-dir ./output -l zh-CN
```

### 5. 批量处理

```bash
# 批量处理目录中所有视频的第1个轨道
python src/cli.py --input-dir ./videos --subtitle-index 1 --output-dir ./output -l zh-CN

# 批量处理所有视频的所有轨道
python src/cli.py --input-dir ./videos --extract-all-subtitles --output-dir ./output -l zh-CN
```

## 实际使用场景

### 场景1：多语言电影
**视频**: 好莱坞电影，包含英语、中文、日语字幕
- 轨道 0: English (默认)
- 轨道 1: 简体中文
- 轨道 2: Japanese

**需求**: 只翻译英语字幕到中文
```bash
python src/cli.py -i movie.mp4 --subtitle-index 0 -o movie_en_to_zh.srt -l zh-CN
```

### 场景2：动漫视频
**视频**: 日本动漫，包含对话和歌词字幕
- 轨道 0: Dialogue (ja, ass) - 对话字幕
- 轨道 1: Signs & Songs (ja, ass) - 标识和歌词（强制字幕）
- 轨道 2: English Dub (en, subrip) - 英语配音字幕

**需求**: 分别翻译对话和歌词字幕
```bash
# 翻译对话字幕
python src/cli.py -i anime.mkv --subtitle-index 0 -o dialogue_zh.srt -l zh-CN

# 翻译歌词字幕
python src/cli.py -i anime.mkv --subtitle-index 1 -o songs_zh.srt -l zh-CN
```

### 场景3：学习材料
**视频**: 多语言教学视频
- 轨道 0: English (默认)
- 轨道 1: Français
- 轨道 2: Deutsch
- 轨道 3: Español

**需求**: 把所有外语字幕都翻译成中文
```bash
python src/cli.py -i lesson.mp4 --extract-all-subtitles --output-dir ./chinese_subs -l zh-CN
```

## 轨道信息说明

### 轨道属性
- **索引 (Index)**: 轨道在视频文件中的编号，从0开始
- **标题 (Title)**: 轨道的显示名称
- **语言 (Language)**: 字幕语言代码（如 en, zh-CN, ja）
- **编码 (Codec)**: 字幕格式（如 subrip, ass, webvtt）

### 轨道标记
- **默认 (Default)**: 播放器默认选择的字幕轨道
- **强制 (Forced)**: 强制显示的字幕（通常用于外语对话或标识）

## 错误处理

### 轨道不存在
如果指定的轨道索引不存在，程序会显示可用的轨道列表：

```
❌ 字幕轨道索引 5 不存在。可用索引: [0, 1, 2]
```

### 没有字幕轨道
如果视频没有内嵌字幕轨道：

```
❌ 未检测到字幕轨道
```

### 文件不存在
如果指定的视频文件不存在：

```
❌ 文件不存在: movie.mp4
```

## 技术实现

### 核心类和方法

#### `SubtitleStream` 类
```python
class SubtitleStream:
    def __init__(self, index: int, codec: str, language: str = None, title: str = None):
        self.index = index          # 轨道索引
        self.codec = codec          # 编码格式
        self.language = language    # 语言代码
        self.title = title          # 显示标题
        self.is_forced = False      # 是否强制字幕
        self.is_default = False     # 是否默认轨道
```

#### 关键方法
- `VideoProcessor.get_video_info()`: 获取视频信息，包括所有字幕轨道
- `VideoProcessor.extract_subtitle()`: 提取指定索引的字幕轨道
- `VideoProcessor.extract_all_subtitles()`: 提取所有字幕轨道
- `CLI.list_subtitle_tracks()`: CLI显示轨道列表
- `GUI._get_selected_subtitle_track_index()`: GUI获取选中轨道索引

### GUI实现细节
- 字幕轨道选择器在视频加载时动态填充
- "提取所有轨道"选项会禁用轨道选择器
- 轨道显示格式：`轨道 索引: 标题 (语言, 编码)`
- 使用正则表达式解析选中的轨道索引

### CLI实现细节
- `--list-subtitles` 参数显示详细的轨道信息
- `--subtitle-index` 参数指定要提取的轨道（默认0）
- `--extract-all-subtitles` 参数提取所有轨道（忽略subtitle-index）
- 提供使用示例和错误提示

## 兼容性

### 向后兼容
- 保留原有的"提取所有字幕轨道"功能
- 默认行为：如果不指定轨道，使用第一个轨道（索引0）
- 所有现有的配置和参数都继续有效

### 支持的字幕格式
- SRT (SubRip)
- VTT (WebVTT) 
- ASS/SSA (Advanced SubStation Alpha)
- SUB (MicroDVD)
- TXT (纯文本)

### 支持的容器格式
- MP4
- MKV (Matroska)
- AVI
- MOV
- WMV
- FLV
- WebM
- M4V

## 常见问题

### Q: 如何知道视频有哪些字幕轨道？
A: 使用 `python src/cli.py --list-subtitles video.mp4` 命令查看，或在GUI中选择视频文件后查看右侧信息面板。

### Q: 轨道索引是从0还是1开始？
A: 轨道索引从0开始。第一个轨道是0，第二个轨道是1，以此类推。

### Q: 如果选择了不存在的轨道索引会怎样？
A: 程序会显示错误信息并列出所有可用的轨道索引。

### Q: "默认"和"强制"轨道有什么区别？
A: 
- **默认轨道**: 播放器通常会自动选择的字幕轨道
- **强制轨道**: 包含重要信息（如外语对话翻译）的字幕，建议始终显示

### Q: 可以同时翻译多个特定轨道吗？
A: 目前CLI一次只能选择一个特定轨道，但可以使用 `--extract-all-subtitles` 翻译所有轨道。GUI同样支持单轨道或全部轨道的选择。

### Q: 输出文件如何命名？
A: 
- 单轨道: 使用指定的输出文件名
- 所有轨道: 自动生成格式为 `原文件名_sub_轨道索引_语言.格式` 的文件名

## 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 新增字幕轨道选择功能
- ✅ 添加 `--list-subtitles` CLI命令
- ✅ GUI添加字幕轨道选择下拉框
- ✅ 改进视频信息显示
- ✅ 添加轨道状态标识（默认/强制）
- ✅ 完善错误处理和用户提示
- ✅ 保持向后兼容性

## 贡献

如果您发现问题或有改进建议，欢迎：
1. 提交Issue报告问题
2. 提交Pull Request贡献代码
3. 改进文档和示例

## 许可证

本功能遵循项目的整体许可证条款。