@echo off
echo ========================================
echo           安装拖拽功能支持
echo ========================================
echo.
echo 正在安装 tkinterdnd2 库...
echo.

pip install tkinterdnd2>=0.3.0

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 拖拽功能安装成功！
    echo.
    echo 现在您可以：
    echo • 直接将图片文件拖拽到预览区域
    echo • 支持多文件拖拽导入
    echo • 拖拽时有视觉反馈提示
    echo.
) else (
    echo.
    echo ❌ 安装失败，请检查网络连接或尝试：
    echo    pip install --upgrade pip
    echo    pip install tkinterdnd2
    echo.
)

echo 按任意键继续...
pause >nul
