@echo off
rem 视频翻译器虚拟环境激活脚本 (Windows)
rem Virtual Environment Activation Script for Video Translator (Windows)

setlocal enabledelayedexpansion

echo 🚀 视频翻译器虚拟环境管理脚本
echo ================================================

rem 设置项目根目录
set "PROJECT_ROOT=%~dp0"
set "VENV_PATH=%PROJECT_ROOT%venv"

rem 检查虚拟环境是否存在
if not exist "%VENV_PATH%" (
    echo ⚠️  虚拟环境不存在，正在创建...

    rem 创建虚拟环境
    python -m venv "%VENV_PATH%"

    if !errorlevel! equ 0 (
        echo ✅ 虚拟环境创建成功
    ) else (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
)

rem 激活虚拟环境
echo 🔄 激活虚拟环境...
call "%VENV_PATH%\Scripts\activate.bat"

if !errorlevel! equ 0 (
    echo ✅ 虚拟环境已激活: %VIRTUAL_ENV%
) else (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)

rem 显示Python版本
echo 🐍 Python版本:
python --version

rem 检查并安装依赖
set "REQUIREMENTS_FILE=%PROJECT_ROOT%requirements.txt"
if exist "%REQUIREMENTS_FILE%" (
    echo 📦 检查依赖安装状态...

    rem 检查pip包列表，如果为空或很少则需要安装依赖
    for /f %%i in ('pip list ^| find /c /v ""') do set PACKAGE_COUNT=%%i

    if !PACKAGE_COUNT! lss 10 (
        echo 🔧 安装/更新项目依赖...
        python -m pip install --upgrade pip
        pip install -r "%REQUIREMENTS_FILE%"

        if !errorlevel! equ 0 (
            echo ✅ 依赖安装完成
        ) else (
            echo ❌ 依赖安装失败
            pause
            exit /b 1
        )
    ) else (
        echo ✅ 依赖已安装
    )
)

rem 显示已安装的包数量
for /f %%i in ('pip list ^| find /c /v ""') do set FINAL_COUNT=%%i
set /a PACKAGE_COUNT=!FINAL_COUNT! - 2
echo 📊 已安装包数量: !PACKAGE_COUNT!

echo.
echo 🎉 环境准备完成！
echo.
echo 可用命令：
echo   python run.py                    # 启动图形界面
echo   python run.py --cli              # 启动命令行界面
echo   python test_providers.py         # 测试AI平台
echo   python setup_platforms.py       # 配置新平台
echo   python demo_new_platforms.py    # 查看演示
echo.
echo 💡 提示: 使用 'deactivate' 命令退出虚拟环境
echo.

rem 保持命令窗口打开，用户可以继续使用
cmd /k
