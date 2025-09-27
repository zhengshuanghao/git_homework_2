@echo off
echo ========================================
echo       构建带拖拽功能的水印应用程序
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python环境未配置，请安装Python
    pause
    exit /b 1
)

echo ✅ Python环境已就绪

REM 安装/更新依赖
echo.
echo 📦 安装依赖包...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

REM 检查pathlib冲突
echo.
echo 🔍 检查pathlib冲突...
python -c "import pathlib; print('pathlib导入成功')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  检测到pathlib冲突，请运行 fix_pathlib_conflict.bat
    echo    或手动执行：
    echo    conda remove pathlib -y
    echo    pip uninstall pathlib -y
    pause
    exit /b 1
)

echo ✅ 无pathlib冲突

REM 构建EXE
echo.
echo 🔨 开始构建EXE...
pyinstaller --onefile ^
    --windowed ^
    --name "WatermarkApp_Drag" ^
    --icon=icon.ico ^
    --add-data "templates;templates" ^
    --add-data "src;src" ^
    --exclude-module windnd ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 构建成功！
    echo.
    echo 📁 文件位置：dist\WatermarkApp_Drag.exe
    echo 📊 预计大小：~250MB
    echo.
    echo 🆕 新功能：
    echo • 支持拖拽图片到预览区域
    echo • 多文件拖拽导入
    echo • 拖拽时视觉反馈
    echo.
    echo 🎯 立即测试：
    echo    cd dist
    echo    .\WatermarkApp_Drag.exe
    echo.
) else (
    echo.
    echo ❌ 构建失败，请检查错误信息
    echo.
)

echo 按任意键继续...
pause >nul
