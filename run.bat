@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 视频翻译器 Windows 启动脚本
REM Video Translator Windows Launcher

title 视频翻译器 - Video Translator

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                     视频翻译器 v1.0.0                        ║
echo ║                   Video Translator v1.0.0                   ║
echo ║                                                              ║
echo ║  Windows 启动脚本                                             ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 检查Python是否安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo.
    echo 请先安装Python 3.8或更高版本：
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 获取Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

REM 检查FFmpeg
echo 🔍 检查FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告: 未找到FFmpeg
    echo 某些功能可能无法使用。请从以下地址下载并安装FFmpeg：
    echo https://ffmpeg.org/download.html#build-windows
    echo.
    set /p continue="是否继续启动？(y/N): "
    if /i not "!continue!"=="y" (
        exit /b 1
    )
) else (
    echo ✅ FFmpeg已安装
)

REM 检查requirements.txt
if not exist "requirements.txt" (
    echo ❌ 错误: 未找到requirements.txt文件
    echo 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

REM 检查.env文件
echo 🔍 检查配置文件...
if not exist ".env" (
    echo ⚠️  未找到.env配置文件
    if exist ".env.template" (
        echo.
        echo 发现.env.template模板文件
        set /p create_env="是否创建.env配置文件？(y/N): "
        if /i "!create_env!"=="y" (
            copy ".env.template" ".env" >nul
            echo ✅ 已创建.env文件
            echo.
            echo 📝 请编辑.env文件并配置您的API密钥
            echo 按任意键打开.env文件进行编辑...
            pause >nul
            notepad .env
            echo.
            echo 配置完成后请重新运行此脚本
            pause
            exit /b 0
        )
    ) else (
        echo ❌ 也未找到.env.template模板文件
    )
    echo.
    echo 没有API密钥配置，某些翻译功能将无法使用
    set /p continue_without_env="是否继续启动？(y/N): "
    if /i not "!continue_without_env!"=="y" (
        exit /b 1
    )
) else (
    echo ✅ 找到.env配置文件
)

REM 检查并安装依赖
echo 🔍 检查Python依赖...
python -c "import ttkthemes" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  检测到缺少依赖包
    set /p install_deps="是否自动安装依赖？(y/N): "
    if /i "!install_deps!"=="y" (
        echo 📦 正在安装依赖包...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo ❌ 依赖安装失败
            echo 请手动运行: pip install -r requirements.txt
            pause
            exit /b 1
        )
        echo ✅ 依赖安装完成
    ) else (
        echo ⚠️  跳过依赖安装，程序可能无法正常运行
        echo 如需安装依赖，请运行: pip install -r requirements.txt
    )
) else (
    echo ✅ 主要依赖已安装
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 显示启动选项
:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                     视频翻译器 v1.0.0                        ║
echo ║                   Video Translator v1.0.0                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 请选择启动模式：
echo.
echo   1. 🖥️  启动图形界面 (GUI)
echo   2. 💻 启动命令行界面 (CLI)
echo   3. 🔧 系统环境检查
echo   4. 📚 查看帮助信息
echo   5. 🚪 退出
echo.
set /p choice="请输入选项 (1-5): "

if "!choice!"=="1" goto start_gui
if "!choice!"=="2" goto start_cli
if "!choice!"=="3" goto check_system
if "!choice!"=="4" goto show_help
if "!choice!"=="5" goto exit
echo 无效选项，请重新选择
timeout /t 2 >nul
goto menu

:start_gui
echo.
echo 🚀 正在启动图形界面...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python run.py
if errorlevel 1 (
    echo.
    echo ❌ GUI启动失败
    echo 请检查错误信息或尝试使用命令行模式
    pause
)
goto menu

:start_cli
echo.
echo 💻 启动命令行界面...
echo 输入 --help 查看可用命令
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python run.py --cli
if errorlevel 1 (
    echo.
    echo ❌ CLI启动失败
    pause
)
goto menu

:check_system
echo.
echo 🔧 系统环境检查...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python run.py --check
echo.
pause
goto menu

:show_help
cls
echo.
echo 📚 视频翻译器使用帮助
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎯 主要功能:
echo   • 从视频文件中提取字幕
echo   • 使用AI服务翻译字幕
echo   • 支持多种字幕格式输出
echo   • 批量处理多个视频文件
echo.
echo 📋 支持的视频格式:
echo   MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V 等
echo.
echo 🤖 支持的AI翻译服务:
echo   • OpenAI GPT (需要API密钥)
echo   • Anthropic Claude (需要API密钥)
echo   • Google Translate (需要服务账户)
echo   • Azure Translator (需要API密钥)
echo.
echo 🔧 快速命令示例:
echo   python run.py --cli -i video.mp4 -l zh-CN
echo   python run.py --cli --input-dir C:\Videos -l zh-CN
echo   python run.py --cli --list-languages
echo.
echo 📁 重要文件:
echo   • .env - API密钥配置文件
echo   • config.yaml - 应用配置文件
echo   • logs/ - 日志文件目录
echo   • output/ - 默认输出目录
echo.
echo 🆘 获取帮助:
echo   • GitHub: [项目地址]
echo   • 文档: README.md
echo   • 命令行帮助: python run.py --cli --help
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pause
goto menu

:exit
echo.
echo 👋 感谢使用视频翻译器！
timeout /t 2 >nul
exit /b 0

REM 错误处理
:error
echo.
echo ❌ 发生错误，程序即将退出
pause
exit /b 1
