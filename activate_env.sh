#!/bin/bash
# 视频翻译器虚拟环境激活脚本
# Virtual Environment Activation Script for Video Translator

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"

echo -e "${BLUE}🚀 视频翻译器虚拟环境管理脚本${NC}"
echo "================================================"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"

    # 创建虚拟环境
    python3 -m venv "$VENV_PATH"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
    else
        echo -e "${RED}❌ 虚拟环境创建失败${NC}"
        exit 1
    fi
fi

# 激活虚拟环境
echo -e "${BLUE}🔄 激活虚拟环境...${NC}"
source "$VENV_PATH/bin/activate"

# 检查是否成功激活
if [ "$VIRTUAL_ENV" != "" ]; then
    echo -e "${GREEN}✅ 虚拟环境已激活: $VIRTUAL_ENV${NC}"
else
    echo -e "${RED}❌ 虚拟环境激活失败${NC}"
    exit 1
fi

# 显示Python版本
echo -e "${BLUE}🐍 Python版本:${NC}"
python --version

# 检查并安装依赖
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements-minimal.txt"
# 如果最小依赖文件不存在，回退到核心依赖
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    REQUIREMENTS_FILE="$PROJECT_ROOT/requirements-core.txt"
fi
# 如果核心依赖也不存在，使用完整依赖
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
fi

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${BLUE}📦 检查依赖安装状态...${NC}"
    echo -e "${BLUE}📋 使用依赖文件: $(basename "$REQUIREMENTS_FILE")${NC}"

    # 检查是否需要安装依赖
    if [ ! -f "$VENV_PATH/pyvenv.cfg" ] || [ "$REQUIREMENTS_FILE" -nt "$VENV_PATH/pyvenv.cfg" ]; then
        echo -e "${YELLOW}🔧 安装/更新项目依赖...${NC}"
        pip install --upgrade pip
        echo -e "${BLUE}📥 安装依赖包（这可能需要几分钟）...${NC}"
        pip install -r "$REQUIREMENTS_FILE"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 依赖安装完成${NC}"
        else
            echo -e "${RED}❌ 依赖安装失败${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ 依赖已是最新版本${NC}"
    fi
fi

# 显示已安装的包数量
PACKAGE_COUNT=$(pip list | wc -l)
echo -e "${BLUE}📊 已安装包数量: $((PACKAGE_COUNT - 2))${NC}"

echo ""
echo -e "${GREEN}🎉 环境准备完成！${NC}"
echo ""
echo "可用命令："
echo "  python run.py                    # 启动图形界面"
echo "  python run.py --cli              # 启动命令行界面"
echo "  python test_providers.py         # 测试AI平台"
echo "  python setup_platforms.py       # 配置新平台"
echo "  python demo_new_platforms.py    # 查看演示"
echo ""
echo "🔧 依赖管理："
echo "  pip install -r requirements-minimal.txt   # 最小依赖（推荐）"
echo "  pip install -r requirements-core.txt      # 核心功能"
echo "  pip install -r requirements.txt           # 完整功能"
echo ""
echo -e "${YELLOW}💡 提示: 使用 'deactivate' 命令退出虚拟环境${NC}"
echo ""

# 如果是交互式shell，保持环境激活
if [[ $- == *i* ]]; then
    echo -e "${BLUE}🔧 交互模式：虚拟环境将保持激活状态${NC}"
    exec "$SHELL"
fi
