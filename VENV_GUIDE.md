# 🌍 虚拟环境使用指南
# Virtual Environment Usage Guide

本指南将详细介绍如何在视频翻译器项目中使用Python虚拟环境。

## 📖 什么是虚拟环境？

虚拟环境是Python项目的独立运行环境，它可以：
- ✅ 隔离项目依赖，避免版本冲突
- ✅ 确保项目在不同机器上的一致性
- ✅ 方便管理和部署项目
- ✅ 保持系统Python环境的整洁

## 🚀 快速开始

### 方法1: 使用便捷脚本（推荐）

#### Linux/macOS:
```bash
# 自动创建环境并安装依赖
source activate_env.sh
```

#### Windows:
```batch
REM 自动创建环境并安装依赖
activate_env.bat
```

### 方法2: 使用管理脚本
```bash
# 交互式环境管理
python manage_env.py

# 或直接完整设置
python manage_env.py setup
```

### 方法3: 手动操作
```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活环境
source venv/bin/activate      # Linux/macOS
# 或
venv\Scripts\activate.bat     # Windows

# 3. 安装依赖
pip install -r requirements-core.txt
```

## 📋 环境管理命令

### 基本操作

```bash
# 检查环境状态
python manage_env.py check

# 创建新的虚拟环境
python manage_env.py create

# 安装/更新依赖
python manage_env.py install

# 删除虚拟环境
python manage_env.py remove

# 显示激活指南
python manage_env.py guide
```

### 激活/停用环境

```bash
# 激活虚拟环境
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate.bat     # Windows CMD
venv\Scripts\Activate.ps1     # Windows PowerShell

# 停用虚拟环境
deactivate
```

### 验证环境

```bash
# 检查Python路径
which python                  # Linux/macOS
where python                  # Windows

# 检查已安装的包
pip list

# 测试项目功能
python -c "from src.core.translator import TranslationProvider; print('Available providers:', [p.value for p in TranslationProvider])"
```

## 📦 依赖管理

### 依赖文件说明

- **`requirements-core.txt`**: 核心依赖（推荐）
  - 包含运行项目必需的最小依赖
  - 不包含GUI组件，适合服务器环境
  - 安装速度快，兼容性好

- **`requirements.txt`**: 完整依赖
  - 包含所有功能的依赖
  - 包含GUI和开发工具
  - 可能需要额外的系统依赖

### 安装不同依赖集

```bash
# 安装核心依赖（推荐）
pip install -r requirements-core.txt

# 安装完整依赖
pip install -r requirements.txt

# 只安装开发依赖
pip install -r requirements.txt[dev]

# 安装GUI依赖
pip install -r requirements.txt[gui]
```

### 更新依赖

```bash
# 更新所有包到最新版本
pip install --upgrade -r requirements-core.txt

# 更新单个包
pip install --upgrade openai

# 检查过时的包
pip list --outdated
```

## 🔧 常见问题解决

### 问题1: 虚拟环境创建失败

**症状**: `python -m venv venv` 失败

**解决方案**:
```bash
# 确保Python版本正确
python --version  # 需要3.8+

# Ubuntu/Debian系统可能需要
sudo apt install python3-venv

# 或使用virtualenv
pip install virtualenv
virtualenv venv
```

### 问题2: 激活脚本不存在

**症状**: `source venv/bin/activate` 找不到文件

**解决方案**:
```bash
# 检查虚拟环境是否正确创建
ls -la venv/

# 重新创建虚拟环境
rm -rf venv
python -m venv venv
```

### 问题3: 依赖安装失败

**症状**: pip install 报错

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 清理缓存
pip cache purge

# 使用国内镜像（中国大陆用户）
pip install -r requirements-core.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 单独安装问题包
pip install problematic-package --verbose
```

### 问题4: 模块导入错误

**症状**: `ModuleNotFoundError` 或 `ImportError`

**解决方案**:
```bash
# 确保在虚拟环境中
which python

# 设置PYTHONPATH
export PYTHONPATH=.

# 或使用项目根目录运行
cd /path/to/video_translator
python -m src.main
```

### 问题5: GUI依赖安装失败

**症状**: tkinter相关错误

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# 或使用核心依赖（不包含GUI）
pip install -r requirements-core.txt
```

## 🖥️ 平台特定说明

### Linux系统

```bash
# Ubuntu/Debian安装系统依赖
sudo apt update
sudo apt install python3-venv python3-pip python3-dev

# CentOS/RHEL
sudo yum install python3-venv python3-pip python3-devel

# 设置权限
chmod +x activate_env.sh
```

### macOS系统

```bash
# 使用Homebrew安装Python
brew install python

# 或使用系统Python
python3 -m venv venv
```

### Windows系统

```batch
REM 确保Python在PATH中
python --version

REM 如果遇到执行策略问题（PowerShell）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

REM 使用CMD而不是PowerShell可能更稳定
```

## 🔄 开发工作流

### 日常开发

```bash
# 1. 激活环境
source activate_env.sh

# 2. 开发和测试
python test_providers.py
python run.py --cli

# 3. 停用环境
deactivate
```

### 添加新依赖

```bash
# 1. 激活环境
source venv/bin/activate

# 2. 安装新包
pip install new-package

# 3. 更新requirements文件
pip freeze > requirements-new.txt

# 4. 手动编辑requirements-core.txt添加必要依赖
```

### 环境迁移

```bash
# 导出当前环境
pip freeze > requirements-snapshot.txt

# 在新机器上
python -m venv venv
source venv/bin/activate
pip install -r requirements-snapshot.txt
```

## 🧪 测试环境

### 运行测试

```bash
# 激活环境
source venv/bin/activate

# 基本功能测试
python -c "from src.core.translator import TranslationManager; print('✅ Core modules working')"

# 翻译器测试
python test_providers.py check

# 配置工具测试
python setup_platforms.py check

# 演示脚本测试
python demo_new_platforms.py config
```

### 性能测试

```bash
# 检查内存使用
python -c "
import psutil
import sys
print(f'Python进程内存使用: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB')
print(f'Python版本: {sys.version}')
"

# 检查依赖大小
pip list --format=freeze | wc -l
```

## 📚 最佳实践

### 1. 环境命名
```bash
# 项目特定的环境名
python -m venv video-translator-env

# 版本特定的环境
python -m venv venv-python39
```

### 2. 依赖管理
```bash
# 固定主要依赖版本
openai>=1.12.0,<2.0.0

# 使用依赖组
pip install -e .[dev,test]
```

### 3. 环境备份
```bash
# 定期备份环境配置
pip freeze > requirements-$(date +%Y%m%d).txt

# 备份虚拟环境（不推荐，建议重新创建）
tar -czf venv-backup.tar.gz venv/
```

### 4. 多环境管理
```bash
# 使用conda（如果安装了）
conda create -n video-translator python=3.9
conda activate video-translator
pip install -r requirements-core.txt

# 使用pyenv-virtualenv
pyenv virtualenv 3.9.0 video-translator
pyenv activate video-translator
```

## 🆘 获取帮助

### 诊断命令
```bash
# 环境诊断
python manage_env.py check

# 系统信息
python -c "
import sys, platform
print(f'Python版本: {sys.version}')
print(f'平台: {platform.platform()}')
print(f'架构: {platform.machine()}')
"

# 依赖检查
pip check
```

### 重置环境
```bash
# 完全重置
rm -rf venv/
python manage_env.py setup
```

### 寻求支持
- 📖 查看项目README.md
- 🐛 检查GitHub Issues
- 🔧 运行诊断脚本
- 📝 提供完整错误信息

## 🎯 快速命令参考

```bash
# 环境管理
python -m venv venv                    # 创建环境
source venv/bin/activate               # 激活环境（Linux/Mac）
venv\Scripts\activate.bat              # 激活环境（Windows）
deactivate                             # 停用环境

# 依赖管理
pip install -r requirements-core.txt  # 安装依赖
pip freeze > requirements.txt         # 导出依赖
pip list --outdated                   # 检查更新

# 项目命令
python run.py                         # 启动GUI
python run.py --cli                   # 启动CLI
python test_providers.py             # 测试平台
python setup_platforms.py            # 配置平台
```

---

💡 **提示**: 建议将这些命令添加到你的shell配置文件（如`.bashrc`或`.zshrc`）中作为别名，方便日常使用。

🔗 **相关文档**: 
- [QUICK_START_NEW_PLATFORMS.md](QUICK_START_NEW_PLATFORMS.md) - 新平台快速入门
- [README.md](README.md) - 项目总览
- [INSTALL.md](INSTALL.md) - 详细安装指南