#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印应用程序 - 主入口
支持Windows和MacOS的桌面水印应用程序
"""

import tkinter as tk
from src.app import WatermarkApp

def main():
    """主函数"""
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
