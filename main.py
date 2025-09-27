#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印应用程序 - 主入口
支持Windows和MacOS的桌面水印应用程序
支持拖拽功能
"""

import tkinter as tk

# 检查是否安装了拖拽支持
try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

from src.app import WatermarkApp

def main():
    """主函数"""
    # 如果支持拖拽，使用TkinterDnD.Tk，否则使用普通的Tk
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = WatermarkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
