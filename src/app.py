#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主应用程序类
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import json
import configparser
from typing import List, Dict, Optional, Tuple

from .image_processor import ImageProcessor
from .watermark_manager import WatermarkManager
from .template_manager import TemplateManager
from .file_manager import FileManager


class WatermarkApp:
    """水印应用程序主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("水印应用程序 - Watermark Tool")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 初始化组件
        self.image_processor = ImageProcessor()
        self.watermark_manager = WatermarkManager()
        self.template_manager = TemplateManager()
        self.file_manager = FileManager()
        
        # 状态变量
        self.selected_images = []  # 选中的图片文件路径列表
        self.current_image_index = 0  # 当前预览的图片索引
        self.preview_image = None  # 当前预览的图片对象
        self.preview_photo = None  # 用于显示的PhotoImage对象
        
        # 创建界面
        self.create_widgets()
        self.setup_bindings()
        
        # 加载上次的设置
        self.template_manager.load_last_settings(self.watermark_manager)
        self.update_ui_from_watermark_settings()
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板 - 文件列表
        self.create_file_panel(main_frame)
        
        # 中央面板 - 预览
        self.create_preview_panel(main_frame)
        
        # 右侧面板 - 控制面板
        self.create_control_panel(main_frame)
        
        # 底部状态栏
        self.create_status_bar()
        
    def create_file_panel(self, parent):
        """创建文件面板"""
        file_frame = ttk.LabelFrame(parent, text="文件列表", padding=10)
        file_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        file_frame.configure(width=200)
        file_frame.pack_propagate(False)
        
        # 导入按钮框架
        import_frame = ttk.Frame(file_frame)
        import_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 导入单个文件按钮
        ttk.Button(import_frame, text="导入图片", 
                  command=self.import_single_file).pack(fill=tk.X, pady=(0, 5))
        
        # 批量导入按钮
        ttk.Button(import_frame, text="批量导入", 
                  command=self.import_multiple_files).pack(fill=tk.X, pady=(0, 5))
        
        # 导入文件夹按钮
        ttk.Button(import_frame, text="导入文件夹", 
                  command=self.import_folder).pack(fill=tk.X, pady=(0, 5))
        
        # 方向修正选项
        orientation_frame = ttk.Frame(import_frame)
        orientation_frame.pack(fill=tk.X, pady=(10, 5))
        
        self.auto_fix_orientation = tk.BooleanVar(value=True)
        ttk.Checkbutton(orientation_frame, text="自动修正图片方向", 
                       variable=self.auto_fix_orientation).pack(anchor=tk.W)
        
        # 强制旋转选项（用于有问题的图片）
        force_frame = ttk.Frame(import_frame)
        force_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(force_frame, text="强制旋转:", font=('Arial', 8)).pack(side=tk.LEFT)
        self.force_rotation = tk.StringVar(value="无")
        rotation_combo = ttk.Combobox(force_frame, textvariable=self.force_rotation, 
                                     values=["无", "顺时针90°", "逆时针90°", "180°"], width=10)
        rotation_combo.pack(side=tk.LEFT, padx=(5, 0))
        rotation_combo.bind('<<ComboboxSelected>>', self.on_force_rotation_change)
        
        # 文件列表
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建带滚动条的列表
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 清除列表按钮
        ttk.Button(file_frame, text="清除列表", 
                  command=self.clear_file_list).pack(fill=tk.X, pady=(10, 0))
        
    def create_preview_panel(self, parent):
        """创建预览面板"""
        preview_frame = ttk.LabelFrame(parent, text="图片预览", padding=10)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 预览画布
        self.canvas = tk.Canvas(preview_frame, bg='white', relief=tk.SUNKEN, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 在画布中添加提示文本
        self.canvas.create_text(400, 300, text="请导入图片开始使用", 
                               font=('Arial', 16), fill='gray', tags="hint")
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="水印设置", padding=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        control_frame.configure(width=300)
        control_frame.pack_propagate(False)
        
        # 创建Notebook用于分页
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 文本水印页面
        self.create_text_watermark_tab(notebook)
        
        # 图片水印页面（包含位置设置）
        self.create_image_watermark_tab(notebook)
        
        # 导出设置页面
        self.create_export_tab(notebook)
        
        # 模板管理页面
        self.create_template_tab(notebook)
    
    def create_text_watermark_tab(self, parent):
        """创建文本水印设置页面（集成位置设置）"""
        text_frame = ttk.Frame(parent)
        parent.add(text_frame, text="文本水印")
        
        # 创建滚动视图
        canvas = tk.Canvas(text_frame, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        # 绑定滚动事件
        def _bound_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Shift-MouseWheel>", _on_h_mousewheel)
            
        def _unbound_to_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Shift-MouseWheel>")
            
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        def _on_h_mousewheel(event):
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind('<Enter>', _bound_to_mousewheel)
        canvas.bind('<Leave>', _unbound_to_mousewheel)
        
        # 动态调整canvas窗口大小
        def _configure_scrollable_frame(event):
            # 更新滚动区域
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 确保frame至少与canvas一样宽
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if frame_width < canvas_width:
                canvas.itemconfig("scrollable_window", width=canvas_width)
        
        def _configure_canvas(event):
            # 当canvas大小改变时，调整frame的宽度
            canvas_width = canvas.winfo_width()
            canvas.itemconfig("scrollable_window", width=canvas_width)
        
        scrollable_frame.bind("<Configure>", _configure_scrollable_frame)
        canvas.bind('<Configure>', _configure_canvas)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="scrollable_window")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 水印文本
        ttk.Label(scrollable_frame, text="水印文本:").pack(anchor=tk.W, pady=(0, 5))
        self.watermark_text = tk.StringVar(value="水印文本")
        text_entry = ttk.Entry(scrollable_frame, textvariable=self.watermark_text, width=25)
        text_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 字体设置
        font_frame = ttk.LabelFrame(scrollable_frame, text="字体设置", padding=5)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 字体族选择
        ttk.Label(font_frame, text="字体:").pack(anchor=tk.W)
        self.font_family = tk.StringVar(value="Arial")
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_family, 
                                 values=["Arial", "Times New Roman", "Helvetica", "Courier", "微软雅黑", "宋体", "黑体"])
        font_combo.pack(fill=tk.X, pady=(0, 5))
        
        # 字体大小
        ttk.Label(font_frame, text="字体大小:").pack(anchor=tk.W)
        self.font_size = tk.IntVar(value=36)
        size_scale = ttk.Scale(font_frame, from_=12, to=100, variable=self.font_size, orient=tk.HORIZONTAL)
        size_scale.pack(fill=tk.X, pady=(0, 5))
        
        size_label = ttk.Label(font_frame, textvariable=self.font_size)
        size_label.pack(anchor=tk.W)
        
        # 字体样式
        style_frame = ttk.Frame(font_frame)
        style_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.font_bold = tk.BooleanVar()
        self.font_italic = tk.BooleanVar()
        ttk.Checkbutton(style_frame, text="粗体", variable=self.font_bold).pack(side=tk.LEFT)
        ttk.Checkbutton(style_frame, text="斜体", variable=self.font_italic).pack(side=tk.LEFT)
        
        # 颜色设置
        color_frame = ttk.LabelFrame(scrollable_frame, text="颜色设置", padding=5)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.text_color = tk.StringVar(value="#000000")
        color_btn_frame = ttk.Frame(color_frame)
        color_btn_frame.pack(fill=tk.X)
        
        ttk.Label(color_btn_frame, text="文字颜色:").pack(side=tk.LEFT)
        self.color_display = tk.Label(color_btn_frame, bg=self.text_color.get(), 
                                     width=3, height=1, relief=tk.RAISED)
        self.color_display.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(color_btn_frame, text="选择颜色", 
                  command=self.choose_text_color).pack(side=tk.RIGHT, padx=(0, 5))
        
        # 透明度设置
        ttk.Label(scrollable_frame, text="透明度:").pack(anchor=tk.W, pady=(0, 5))
        self.text_opacity = tk.IntVar(value=80)
        opacity_scale = ttk.Scale(scrollable_frame, from_=0, to=100, variable=self.text_opacity, orient=tk.HORIZONTAL)
        opacity_scale.pack(fill=tk.X, pady=(0, 5))
        
        opacity_label = ttk.Label(scrollable_frame, textvariable=self.text_opacity)
        opacity_label.pack(anchor=tk.W)
        
        # 文本样式效果设置
        style_frame = ttk.LabelFrame(scrollable_frame, text="文本样式效果", padding=5)
        style_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 阴影效果
        shadow_frame = ttk.LabelFrame(style_frame, text="阴影效果", padding=5)
        shadow_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.enable_shadow = tk.BooleanVar(value=False)
        ttk.Checkbutton(shadow_frame, text="启用阴影", variable=self.enable_shadow,
                       command=self.toggle_shadow_controls).pack(anchor=tk.W)
        
        # 阴影参数框架
        self.shadow_params_frame = ttk.Frame(shadow_frame)
        self.shadow_params_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 阴影颜色
        shadow_color_frame = ttk.Frame(self.shadow_params_frame)
        shadow_color_frame.pack(fill=tk.X, pady=(0, 3))
        
        self.shadow_color = tk.StringVar(value="#808080")
        ttk.Label(shadow_color_frame, text="阴影颜色:").pack(side=tk.LEFT)
        self.shadow_color_display = tk.Label(shadow_color_frame, bg=self.shadow_color.get(), 
                                           width=2, height=1, relief=tk.RAISED)
        self.shadow_color_display.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(shadow_color_frame, text="选择", 
                  command=self.choose_shadow_color).pack(side=tk.RIGHT, padx=(0, 5))
        
        # 阴影偏移
        shadow_offset_frame = ttk.Frame(self.shadow_params_frame)
        shadow_offset_frame.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Label(shadow_offset_frame, text="阴影偏移:").pack(side=tk.LEFT)
        self.shadow_offset_x = tk.IntVar(value=2)
        self.shadow_offset_y = tk.IntVar(value=2)
        ttk.Label(shadow_offset_frame, text="X:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(shadow_offset_frame, from_=-20, to=20, textvariable=self.shadow_offset_x, width=5).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(shadow_offset_frame, text="Y:").pack(side=tk.LEFT, padx=(5, 2))
        ttk.Spinbox(shadow_offset_frame, from_=-20, to=20, textvariable=self.shadow_offset_y, width=5).pack(side=tk.LEFT)
        
        # 阴影模糊（已简化为固定效果以提高性能）
        shadow_blur_frame = ttk.Frame(self.shadow_params_frame)
        shadow_blur_frame.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Label(shadow_blur_frame, text="阴影强度:").pack(anchor=tk.W)
        self.shadow_blur = tk.IntVar(value=1)
        shadow_blur_scale = ttk.Scale(shadow_blur_frame, from_=1, to=3, variable=self.shadow_blur, orient=tk.HORIZONTAL)
        shadow_blur_scale.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(shadow_blur_frame, text="(已优化为简洁效果)", font=('Arial', 8)).pack(anchor=tk.W)
        
        # 描边效果
        stroke_frame = ttk.LabelFrame(style_frame, text="描边效果", padding=5)
        stroke_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.enable_stroke = tk.BooleanVar(value=False)
        ttk.Checkbutton(stroke_frame, text="启用描边", variable=self.enable_stroke,
                       command=self.toggle_stroke_controls).pack(anchor=tk.W)
        
        # 描边参数框架
        self.stroke_params_frame = ttk.Frame(stroke_frame)
        self.stroke_params_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 描边颜色
        stroke_color_frame = ttk.Frame(self.stroke_params_frame)
        stroke_color_frame.pack(fill=tk.X, pady=(0, 3))
        
        self.stroke_color = tk.StringVar(value="#FFFFFF")
        ttk.Label(stroke_color_frame, text="描边颜色:").pack(side=tk.LEFT)
        self.stroke_color_display = tk.Label(stroke_color_frame, bg=self.stroke_color.get(), 
                                           width=2, height=1, relief=tk.RAISED)
        self.stroke_color_display.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(stroke_color_frame, text="选择", 
                  command=self.choose_stroke_color).pack(side=tk.RIGHT, padx=(0, 5))
        
        # 描边宽度
        stroke_width_frame = ttk.Frame(self.stroke_params_frame)
        stroke_width_frame.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Label(stroke_width_frame, text="描边宽度:").pack(anchor=tk.W)
        self.stroke_width = tk.IntVar(value=2)
        stroke_width_scale = ttk.Scale(stroke_width_frame, from_=1, to=5, variable=self.stroke_width, orient=tk.HORIZONTAL)
        stroke_width_scale.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(stroke_width_frame, text="(建议使用1-3像素)", font=('Arial', 8)).pack(anchor=tk.W)
        
        # 水印位置设置（集成到文本水印页面）
        position_frame = ttk.LabelFrame(scrollable_frame, text="水印位置设置", padding=5)
        position_frame.pack(fill=tk.X, pady=(10, 5))
        
        # 预设位置 - 九宫格
        ttk.Label(position_frame, text="预设位置:").pack(anchor=tk.W, pady=(0, 5))
        
        grid_frame = ttk.Frame(position_frame)
        grid_frame.pack(pady=(0, 10))
        
        self.position_var = tk.StringVar(value="center")
        
        positions = [
            ("左上", "top_left"), ("正上", "top_center"), ("右上", "top_right"),
            ("左中", "middle_left"), ("正中", "center"), ("右中", "middle_right"),
            ("左下", "bottom_left"), ("正下", "bottom_center"), ("右下", "bottom_right")
        ]
        
        for i, (text, value) in enumerate(positions):
            row, col = i // 3, i % 3
            ttk.Radiobutton(grid_frame, text=text, variable=self.position_var, 
                           value=value).grid(row=row, column=col, padx=3, pady=2, sticky="w")
        
        # 自定义位置
        custom_pos_frame = ttk.Frame(position_frame)
        custom_pos_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(custom_pos_frame, text="自定义位置:").pack(side=tk.LEFT)
        self.custom_x = tk.IntVar(value=50)
        self.custom_y = tk.IntVar(value=50)
        ttk.Label(custom_pos_frame, text="X:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(custom_pos_frame, from_=0, to=100, textvariable=self.custom_x, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(custom_pos_frame, text="Y:").pack(side=tk.LEFT, padx=(5, 2))
        ttk.Spinbox(custom_pos_frame, from_=0, to=100, textvariable=self.custom_y, width=8).pack(side=tk.LEFT)
        ttk.Label(custom_pos_frame, text="%").pack(side=tk.LEFT, padx=(5, 0))
        
        # 旋转角度
        rotation_frame = ttk.Frame(position_frame)
        rotation_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(rotation_frame, text="旋转角度:").pack(anchor=tk.W)
        self.rotation_angle = tk.IntVar(value=0)
        rotation_scale = ttk.Scale(rotation_frame, from_=-180, to=180, variable=self.rotation_angle, orient=tk.HORIZONTAL)
        rotation_scale.pack(fill=tk.X, pady=(2, 0))
        
        rotation_label_frame = ttk.Frame(rotation_frame)
        rotation_label_frame.pack(fill=tk.X)
        rotation_label = ttk.Label(rotation_label_frame, textvariable=self.rotation_angle)
        rotation_label.pack(side=tk.LEFT)
        ttk.Label(rotation_label_frame, text="度").pack(side=tk.LEFT, padx=(2, 0))
        
        # 初始化控件状态
        self.toggle_shadow_controls()
        self.toggle_stroke_controls()
        
        # 布局滚动组件
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置网格权重
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
    def create_image_watermark_tab(self, parent):
        """创建图片水印设置页面（包含位置设置）"""
        image_frame = ttk.Frame(parent)
        parent.add(image_frame, text="图片水印")
        
        # 创建滚动视图
        canvas = tk.Canvas(image_frame, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(image_frame, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(image_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        # 绑定滚动事件
        def _bound_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_img_mousewheel)
            canvas.bind_all("<Shift-MouseWheel>", _on_img_h_mousewheel)
            
        def _unbound_to_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Shift-MouseWheel>")
            
        def _on_img_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        def _on_img_h_mousewheel(event):
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind('<Enter>', _bound_to_mousewheel)
        canvas.bind('<Leave>', _unbound_to_mousewheel)
        
        # 动态调整canvas窗口大小
        def _configure_img_scrollable_frame(event):
            # 更新滚动区域
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 确保frame至少与canvas一样宽
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if frame_width < canvas_width:
                canvas.itemconfig("img_scrollable_window", width=canvas_width)
        
        def _configure_img_canvas(event):
            # 当canvas大小改变时，调整frame的宽度
            canvas_width = canvas.winfo_width()
            canvas.itemconfig("img_scrollable_window", width=canvas_width)
        
        scrollable_frame.bind("<Configure>", _configure_img_scrollable_frame)
        canvas.bind('<Configure>', _configure_img_canvas)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="img_scrollable_window")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 图片选择
        select_group = ttk.LabelFrame(scrollable_frame, text="水印图片选择", padding=5)
        select_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(select_group, text="选择图片文件:").pack(anchor=tk.W, pady=(0, 5))
        
        select_frame = ttk.Frame(select_group)
        select_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.watermark_image_path = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.watermark_image_path, state=tk.DISABLED).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(select_frame, text="选择", command=self.select_watermark_image).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 图片预览（小尺寸）
        self.image_preview_label = ttk.Label(select_group, text="未选择图片")
        self.image_preview_label.pack(pady=(5, 0))
        
        # 图片设置
        settings_group = ttk.LabelFrame(scrollable_frame, text="图片设置", padding=5)
        settings_group.pack(fill=tk.X, pady=(0, 10))
        
        # 图片缩放
        ttk.Label(settings_group, text="缩放比例:").pack(anchor=tk.W, pady=(0, 5))
        self.image_scale = tk.IntVar(value=50)
        scale_frame = ttk.Frame(settings_group)
        scale_frame.pack(fill=tk.X, pady=(0, 5))
        
        scale_scale = ttk.Scale(scale_frame, from_=10, to=200, variable=self.image_scale, orient=tk.HORIZONTAL)
        scale_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scale_label = ttk.Label(scale_frame, textvariable=self.image_scale, width=5)
        scale_label.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Label(scale_frame, text="%").pack(side=tk.RIGHT)
        
        # 图片透明度
        ttk.Label(settings_group, text="透明度:").pack(anchor=tk.W, pady=(10, 5))
        self.image_opacity = tk.IntVar(value=80)
        opacity_frame = ttk.Frame(settings_group)
        opacity_frame.pack(fill=tk.X, pady=(0, 5))
        
        img_opacity_scale = ttk.Scale(opacity_frame, from_=0, to=100, variable=self.image_opacity, orient=tk.HORIZONTAL)
        img_opacity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        opacity_label = ttk.Label(opacity_frame, textvariable=self.image_opacity, width=5)
        opacity_label.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Label(opacity_frame, text="%").pack(side=tk.RIGHT)
        
        # 图片水印位置设置
        img_position_frame = ttk.LabelFrame(scrollable_frame, text="图片水印位置设置", padding=5)
        img_position_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 预设位置 - 九宫格（为图片水印单独设置变量）
        ttk.Label(img_position_frame, text="预设位置:").pack(anchor=tk.W, pady=(0, 5))
        
        img_grid_frame = ttk.Frame(img_position_frame)
        img_grid_frame.pack(pady=(0, 10))
        
        self.image_position_var = tk.StringVar(value="bottom_right")
        
        positions = [
            ("左上", "top_left"), ("正上", "top_center"), ("右上", "top_right"),
            ("左中", "middle_left"), ("正中", "center"), ("右中", "middle_right"),
            ("左下", "bottom_left"), ("正下", "bottom_center"), ("右下", "bottom_right")
        ]
        
        for i, (text, value) in enumerate(positions):
            row, col = i // 3, i % 3
            ttk.Radiobutton(img_grid_frame, text=text, variable=self.image_position_var, 
                           value=value).grid(row=row, column=col, padx=3, pady=2, sticky="w")
        
        # 自定义位置（为图片水印单独设置变量）
        img_custom_pos_frame = ttk.Frame(img_position_frame)
        img_custom_pos_frame.pack(fill=tk.X, pady=(5, 5))
        
        ttk.Label(img_custom_pos_frame, text="自定义位置:").pack(side=tk.LEFT)
        self.image_custom_x = tk.IntVar(value=90)
        self.image_custom_y = tk.IntVar(value=90)
        ttk.Label(img_custom_pos_frame, text="X:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(img_custom_pos_frame, from_=0, to=100, textvariable=self.image_custom_x, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(img_custom_pos_frame, text="Y:").pack(side=tk.LEFT, padx=(5, 2))
        ttk.Spinbox(img_custom_pos_frame, from_=0, to=100, textvariable=self.image_custom_y, width=8).pack(side=tk.LEFT)
        ttk.Label(img_custom_pos_frame, text="%").pack(side=tk.LEFT, padx=(5, 0))
        
        # 图片旋转角度
        img_rotation_frame = ttk.Frame(img_position_frame)
        img_rotation_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(img_rotation_frame, text="旋转角度:").pack(anchor=tk.W)
        self.image_rotation_angle = tk.IntVar(value=0)
        img_rotation_scale = ttk.Scale(img_rotation_frame, from_=-180, to=180, variable=self.image_rotation_angle, orient=tk.HORIZONTAL)
        img_rotation_scale.pack(fill=tk.X, pady=(2, 0))
        
        img_rotation_label_frame = ttk.Frame(img_rotation_frame)
        img_rotation_label_frame.pack(fill=tk.X)
        img_rotation_label = ttk.Label(img_rotation_label_frame, textvariable=self.image_rotation_angle)
        img_rotation_label.pack(side=tk.LEFT)
        ttk.Label(img_rotation_label_frame, text="度").pack(side=tk.LEFT, padx=(2, 0))
        
        # 布局滚动组件
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置网格权重
        image_frame.grid_rowconfigure(0, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)
        
    def create_export_tab(self, parent):
        """创建导出设置页面"""
        export_frame = ttk.Frame(parent)
        parent.add(export_frame, text="导出设置")
        
        # 输出目录
        ttk.Label(export_frame, text="输出目录:").pack(anchor=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(export_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_dir = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.output_dir, state=tk.DISABLED).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="选择", command=self.select_output_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 输出格式
        ttk.Label(export_frame, text="输出格式:").pack(anchor=tk.W, pady=(10, 5))
        self.output_format = tk.StringVar(value="JPEG")
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.output_format, value="JPEG").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="PNG", variable=self.output_format, value="PNG").pack(side=tk.LEFT)
        
        # 文件命名规则
        naming_frame = ttk.LabelFrame(export_frame, text="命名规则", padding=5)
        naming_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.naming_rule = tk.StringVar(value="suffix")
        ttk.Radiobutton(naming_frame, text="保留原名", variable=self.naming_rule, value="original").pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="添加前缀", variable=self.naming_rule, value="prefix").pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="添加后缀", variable=self.naming_rule, value="suffix").pack(anchor=tk.W)
        
        # 自定义前缀/后缀
        custom_frame = ttk.Frame(naming_frame)
        custom_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(custom_frame, text="前缀:").pack(side=tk.LEFT)
        self.file_prefix = tk.StringVar(value="wm_")
        ttk.Entry(custom_frame, textvariable=self.file_prefix, width=10).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(custom_frame, text="后缀:").pack(side=tk.LEFT)
        self.file_suffix = tk.StringVar(value="_watermarked")
        ttk.Entry(custom_frame, textvariable=self.file_suffix, width=15).pack(side=tk.LEFT, padx=(5, 0))
        
        # JPEG质量设置
        quality_frame = ttk.LabelFrame(export_frame, text="JPEG质量", padding=5)
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.jpeg_quality = tk.IntVar(value=90)
        quality_scale = ttk.Scale(quality_frame, from_=10, to=100, variable=self.jpeg_quality, orient=tk.HORIZONTAL)
        quality_scale.pack(fill=tk.X, pady=(0, 5))
        
        quality_label = ttk.Label(quality_frame, textvariable=self.jpeg_quality)
        quality_label.pack(anchor=tk.W)
        
        # 图片尺寸调整设置
        resize_frame = ttk.LabelFrame(export_frame, text="图片尺寸调整", padding=5)
        resize_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 启用尺寸调整
        self.enable_resize = tk.BooleanVar(value=False)
        ttk.Checkbutton(resize_frame, text="启用尺寸调整", variable=self.enable_resize,
                       command=self.toggle_resize_controls).pack(anchor=tk.W, pady=(0, 5))
        
        # 尺寸调整选项框架
        self.resize_options_frame = ttk.Frame(resize_frame)
        self.resize_options_frame.pack(fill=tk.X)
        
        # 调整模式
        self.resize_mode = tk.StringVar(value="percentage")
        modes_frame = ttk.Frame(self.resize_options_frame)
        modes_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Radiobutton(modes_frame, text="按百分比", variable=self.resize_mode, 
                       value="percentage", command=self.on_resize_mode_change).pack(side=tk.LEFT)
        ttk.Radiobutton(modes_frame, text="按宽度", variable=self.resize_mode, 
                       value="width", command=self.on_resize_mode_change).pack(side=tk.LEFT)
        ttk.Radiobutton(modes_frame, text="按高度", variable=self.resize_mode, 
                       value="height", command=self.on_resize_mode_change).pack(side=tk.LEFT)
        ttk.Radiobutton(modes_frame, text="自定义", variable=self.resize_mode, 
                       value="custom", command=self.on_resize_mode_change).pack(side=tk.LEFT)
        
        # 参数输入框架
        self.params_frame = ttk.Frame(self.resize_options_frame)
        self.params_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 百分比输入
        self.percentage_frame = ttk.Frame(self.params_frame)
        self.resize_percentage = tk.IntVar(value=100)
        ttk.Label(self.percentage_frame, text="缩放比例:").pack(side=tk.LEFT)
        percentage_spin = ttk.Spinbox(self.percentage_frame, from_=10, to=500, 
                                     textvariable=self.resize_percentage, width=8)
        percentage_spin.pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(self.percentage_frame, text="%").pack(side=tk.LEFT)
        
        # 宽度输入
        self.width_frame = ttk.Frame(self.params_frame)
        self.resize_width = tk.IntVar(value=800)
        ttk.Label(self.width_frame, text="宽度:").pack(side=tk.LEFT)
        width_spin = ttk.Spinbox(self.width_frame, from_=100, to=10000, 
                                textvariable=self.resize_width, width=8)
        width_spin.pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(self.width_frame, text="像素").pack(side=tk.LEFT)
        
        # 高度输入
        self.height_frame = ttk.Frame(self.params_frame)
        self.resize_height = tk.IntVar(value=600)
        ttk.Label(self.height_frame, text="高度:").pack(side=tk.LEFT)
        height_spin = ttk.Spinbox(self.height_frame, from_=100, to=10000, 
                                 textvariable=self.resize_height, width=8)
        height_spin.pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(self.height_frame, text="像素").pack(side=tk.LEFT)
        
        # 自定义尺寸输入
        self.custom_frame = ttk.Frame(self.params_frame)
        custom_row1 = ttk.Frame(self.custom_frame)
        custom_row1.pack(fill=tk.X, pady=(0, 2))
        custom_row2 = ttk.Frame(self.custom_frame)
        custom_row2.pack(fill=tk.X)
        
        self.custom_width = tk.IntVar(value=800)
        self.custom_height = tk.IntVar(value=600)
        self.keep_aspect_ratio = tk.BooleanVar(value=True)
        
        ttk.Label(custom_row1, text="宽度:").pack(side=tk.LEFT)
        ttk.Spinbox(custom_row1, from_=100, to=10000, textvariable=self.custom_width, width=8).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(custom_row1, text="高度:").pack(side=tk.LEFT)
        ttk.Spinbox(custom_row1, from_=100, to=10000, textvariable=self.custom_height, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Checkbutton(custom_row2, text="保持宽高比", variable=self.keep_aspect_ratio).pack(anchor=tk.W)
        
        # 初始化显示状态
        self.on_resize_mode_change()
        self.toggle_resize_controls()
        
        # 导出按钮
        ttk.Button(export_frame, text="开始导出", command=self.start_export).pack(fill=tk.X, pady=(20, 0))
        
    def create_template_tab(self, parent):
        """创建模板管理页面"""
        template_frame = ttk.Frame(parent)
        parent.add(template_frame, text="模板管理")
        
        # 模板列表
        ttk.Label(template_frame, text="已保存模板:").pack(anchor=tk.W, pady=(0, 5))
        
        list_frame = ttk.Frame(template_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.template_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        template_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        self.template_listbox.configure(yscrollcommand=template_scrollbar.set)
        
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        template_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 模板操作按钮
        button_frame = ttk.Frame(template_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="保存当前设置", command=self.save_template).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="加载模板", command=self.load_template).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="删除模板", command=self.delete_template).pack(fill=tk.X, pady=(0, 5))
        
        # 刷新模板列表
        self.refresh_template_list()
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_bindings(self):
        """设置事件绑定"""
        # 文件列表选择事件
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # 水印设置变化事件
        for var in [self.watermark_text, self.font_family, self.font_size, self.font_bold, 
                   self.font_italic, self.text_color, self.text_opacity, self.position_var,
                   self.custom_x, self.custom_y, self.rotation_angle, self.image_scale, 
                   self.image_opacity, self.watermark_image_path, self.enable_shadow,
                   self.shadow_color, self.shadow_offset_x, self.shadow_offset_y, self.shadow_blur,
                   self.enable_stroke, self.stroke_color, self.stroke_width,
                   self.image_position_var, self.image_custom_x, self.image_custom_y, self.image_rotation_angle]:
            var.trace('w', self.on_watermark_change)
        
        # 画布点击事件（用于拖拽定位水印）
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        
        # 拖拽功能需要tkinterdnd2库，暂时注释
        # self.canvas.drop_target_register(tk.DND_FILES)
        # self.canvas.dnd_bind('<<Drop>>', self.on_file_drop)
    
    def import_single_file(self):
        """导入单个图片文件"""
        file_types = [
            ('图片文件', '*.jpg *.jpeg *.png *.bmp *.tiff *.tif'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('PNG files', '*.png'),
            ('BMP files', '*.bmp'),
            ('TIFF files', '*.tiff *.tif'),
            ('所有文件', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=file_types
        )
        
        if file_path:
            self.add_files([file_path])
    
    def import_multiple_files(self):
        """批量导入图片文件"""
        file_types = [
            ('图片文件', '*.jpg *.jpeg *.png *.bmp *.tiff *.tif'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('PNG files', '*.png'),
            ('BMP files', '*.bmp'),
            ('TIFF files', '*.tiff *.tif'),
            ('所有文件', '*.*')
        ]
        
        file_paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=file_types
        )
        
        if file_paths:
            self.add_files(list(file_paths))
    
    def import_folder(self):
        """导入文件夹中的图片"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        
        if folder_path:
            # 扫描文件夹中的图片
            image_files = self.file_manager.scan_directory_for_images(folder_path, recursive=True)
            if image_files:
                self.add_files(image_files)
                self.status_var.set(f"从文件夹导入了 {len(image_files)} 个图片文件")
            else:
                messagebox.showinfo("提示", "文件夹中未找到支持的图片文件")
    
    def clear_file_list(self):
        """清除文件列表"""
        if messagebox.askyesno("确认", "确定要清除所有文件吗？"):
            self.selected_images.clear()
            self.file_listbox.delete(0, tk.END)
            self.current_image_index = 0
            self.preview_image = None
            self.preview_photo = None
            
            # 清除画布
            self.canvas.delete("all")
            self.canvas.create_text(400, 300, text="请导入图片开始使用", 
                                   font=('Arial', 16), fill='gray', tags="hint")
            
            self.status_var.set("已清除所有文件")
    
    def on_file_select(self, event):
        """文件列表选择事件"""
        selection = self.file_listbox.curselection()
        if selection:
            self.current_image_index = selection[0]
            self.load_current_image()
    
    def add_files(self, file_paths: List[str]):
        """添加文件到列表"""
        supported_files = self.file_manager.get_supported_files(file_paths)
        
        if not supported_files:
            messagebox.showwarning("警告", "未找到支持的图片文件")
            return
        
        # 避免重复添加
        for file_path in supported_files:
            if file_path not in self.selected_images:
                self.selected_images.append(file_path)
                filename = os.path.basename(file_path)
                self.file_listbox.insert(tk.END, filename)
        
        # 如果是第一次添加文件，选中第一个
        if len(self.selected_images) == len(supported_files):
            self.file_listbox.selection_set(0)
            self.current_image_index = 0
            self.load_current_image()
        
        self.status_var.set(f"已导入 {len(self.selected_images)} 个文件")
    
    def load_current_image(self):
        """加载当前选中的图片"""
        if not self.selected_images or self.current_image_index >= len(self.selected_images):
            return
        
        current_file = self.selected_images[self.current_image_index]
        
        # 根据设置决定是否自动修正方向
        if self.auto_fix_orientation.get():
            self.preview_image = self.image_processor.load_image(current_file)
        else:
            # 不进行方向修正，直接加载
            from PIL import Image
            self.preview_image = Image.open(current_file)
            if self.preview_image.mode not in ('RGB', 'RGBA'):
                self.preview_image = self.preview_image.convert('RGB')
        
        # 应用强制旋转（如果设置了）
        if self.preview_image and self.force_rotation.get() != "无":
            self.preview_image = self.apply_force_rotation(self.preview_image)
        
        if self.preview_image:
            self.update_preview()
            filename = os.path.basename(current_file)
            self.status_var.set(f"当前图片: {filename}")
        else:
            messagebox.showerror("错误", f"无法加载图片: {current_file}")
    
    def apply_force_rotation(self, image: Image.Image) -> Image.Image:
        """应用强制旋转"""
        rotation = self.force_rotation.get()
        
        if rotation == "顺时针90°":
            return image.rotate(-90, expand=True)
        elif rotation == "逆时针90°":
            return image.rotate(90, expand=True)
        elif rotation == "180°":
            return image.rotate(180, expand=True)
        else:
            return image
    
    def on_force_rotation_change(self, event=None):
        """强制旋转选项改变时重新加载图片"""
        if hasattr(self, 'preview_image') and self.preview_image:
            self.load_current_image()
    
    def update_preview(self):
        """更新预览显示"""
        if not self.preview_image:
            return
        
        # 应用水印（使用当前水印类型）
        watermark_type = self.get_current_watermark_type()
        watermarked_image = self.watermark_manager.apply_watermark(self.preview_image, watermark_type)
        
        # 创建适合画布的预览图
        canvas_width = max(self.canvas.winfo_width(), 100)
        canvas_height = max(self.canvas.winfo_height(), 100)
        preview_display = self.image_processor.create_preview(watermarked_image, 
                                                             (canvas_width - 20, canvas_height - 20))
        
        # 转换为Tkinter格式
        self.preview_photo = self.image_processor.pil_to_tkinter(preview_display)
        
        # 更新画布
        self.canvas.delete("all")
        
        if canvas_width > 1 and canvas_height > 1:  # 确保画布已经渲染
            x = (canvas_width - self.preview_photo.width()) // 2
            y = (canvas_height - self.preview_photo.height()) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.preview_photo)
    def choose_text_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor(initialcolor=self.text_color.get())[1]
        if color:
            self.text_color.set(color)
            self.color_display.config(bg=color)
    
    def select_watermark_image(self):
        """选择水印图片"""
        file_types = [
            ('图片文件', '*.png *.jpg *.jpeg *.bmp'),
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('所有文件', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=file_types
        )
        
        if file_path:
            self.watermark_image_path.set(file_path)
            self.update_watermark_image_preview(file_path)
    
    def update_watermark_image_preview(self, image_path):
        """更新水印图片预览"""
        try:
            # 加载图片并创建小预览
            image = Image.open(image_path)
            
            # 创建缩略图（最大64x64像素）
            image.thumbnail((64, 64), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter格式
            photo = ImageTk.PhotoImage(image)
            
            # 更新预览标签
            filename = os.path.basename(image_path)
            self.image_preview_label.configure(image=photo, text="", compound=tk.TOP)
            self.image_preview_label.image = photo  # 保持引用防止被垃圾回收
            
            # 在标签下方显示文件名
            preview_text = f"{filename}\n{image.size[0]}x{image.size[1]}"
            self.image_preview_label.configure(text=preview_text, compound=tk.TOP)
            
        except Exception as e:
            self.image_preview_label.configure(image="", text=f"预览失败:\n{str(e)}")
            print(f"图片预览失败: {e}")
    
    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def start_export(self):
        """开始导出"""
        if not self.selected_images:
            messagebox.showwarning("警告", "请先导入图片文件")
            return
        
        if not self.output_dir.get():
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        # 验证输出设置
        is_valid, message = self.file_manager.validate_output_settings(
            self.selected_images, self.output_dir.get(),
            self.naming_rule.get(), self.file_prefix.get(), self.file_suffix.get(),
            self.output_format.get()
        )
        
        if not is_valid:
            messagebox.showerror("错误", message)
            return
        
        # 开始导出处理
        self.export_images()
    
    def save_template(self):
        """保存当前设置为模板"""
        import tkinter.simpledialog as simpledialog
        name = simpledialog.askstring("保存模板", "请输入模板名称:")
        if name and name.strip():
            settings = self.get_current_watermark_settings()
            if self.template_manager.save_template(name.strip(), settings):
                messagebox.showinfo("成功", f"模板 '{name}' 保存成功")
                self.refresh_template_list()
            else:
                messagebox.showerror("错误", "保存模板失败")
    
    def get_current_watermark_type(self):
        """根据当前活动页面和内容获取水印类型"""
        try:
            # 首先检查是否有图片水印路径
            if self.watermark_image_path.get() and os.path.exists(self.watermark_image_path.get()):
                return "image"
            # 然后检查是否有文本内容
            elif self.watermark_text.get().strip():
                return "text"
            else:
                # 根据当前选中的页面判断
                current_tab = self.notebook.index(self.notebook.select())
                if current_tab == 0:  # 文本水印页面
                    return "text"
                elif current_tab == 1:  # 图片水印页面
                    return "image"
                else:
                    return "text"  # 默认文本
        except:
            return "text"
    
    def load_template(self):
        """加载模板"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择要加载的模板")
            return
        
        template_name = self.template_listbox.get(selection[0])
        settings = self.template_manager.load_template(template_name)
        
        if settings:
            self.apply_watermark_settings(settings)
            messagebox.showinfo("成功", f"已加载模板 '{template_name}'")
        else:
            messagebox.showerror("错误", "加载模板失败")
    
    def delete_template(self):
        """删除模板"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的模板")
            return
        
        template_name = self.template_listbox.get(selection[0])
        
        if messagebox.askyesno("确认删除", f"确定要删除模板 '{template_name}' 吗？"):
            if self.template_manager.delete_template(template_name):
                messagebox.showinfo("成功", f"已删除模板 '{template_name}'")
                self.refresh_template_list()
            else:
                messagebox.showerror("错误", "删除模板失败")
    
    def refresh_template_list(self):
        """刷新模板列表"""
        self.template_listbox.delete(0, tk.END)
        templates = self.template_manager.get_template_list()
        for template in templates:
            self.template_listbox.insert(tk.END, template)
    
    def on_watermark_change(self, *args):
        """水印设置变化事件（带防抖动）"""
        # 更新水印管理器设置
        settings = self.get_current_watermark_settings()
        self.watermark_manager.load_settings(settings)
        
        # 取消之前的延迟更新
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        
        # 设置新的延迟更新（防抖动）
        if self.preview_image:
            self._update_timer = self.root.after(200, self.update_preview)  # 200ms防抖动
    
    def on_canvas_click(self, event):
        """画布点击事件"""
        # 如果有预览图，计算相对位置并更新自定义位置
        if self.preview_photo:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 计算点击位置相对于图片的百分比
            img_x = (canvas_width - self.preview_photo.width()) // 2
            img_y = (canvas_height - self.preview_photo.height()) // 2
            
            if (img_x <= event.x <= img_x + self.preview_photo.width() and
                img_y <= event.y <= img_y + self.preview_photo.height()):
                
                relative_x = (event.x - img_x) / self.preview_photo.width()
                relative_y = (event.y - img_y) / self.preview_photo.height()
                
                self.custom_x.set(int(relative_x * 100))
                self.custom_y.set(int(relative_y * 100))
                self.position_var.set("custom")
    
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        self.on_canvas_click(event)  # 复用点击逻辑
    
    def on_file_drop(self, event):
        """文件拖拽事件"""
        files = event.data.split()
        self.add_files(files)
    
    def update_ui_from_watermark_settings(self):
        """从水印管理器设置更新UI控件"""
        settings = self.watermark_manager.get_settings()
        
        # 更新变量（避免触发事件）
        self.watermark_text.set(settings.get('watermark_text', ''))
        self.font_family.set(settings.get('font_family', 'Arial'))
        self.font_size.set(settings.get('font_size', 36))
        self.font_bold.set(settings.get('font_bold', False))
        self.font_italic.set(settings.get('font_italic', False))
        self.text_color.set(settings.get('text_color', '#000000'))
        self.text_opacity.set(settings.get('text_opacity', 80))
        self.watermark_image_path.set(settings.get('watermark_image_path', ''))
        self.image_scale.set(settings.get('image_scale', 50))
        self.image_opacity.set(settings.get('image_opacity', 80))
        self.position_var.set(settings.get('position', 'center'))
        self.custom_x.set(settings.get('custom_x', 50))
        self.custom_y.set(settings.get('custom_y', 50))
        self.rotation_angle.set(settings.get('rotation_angle', 0))
        
        # 更新文本样式效果设置
        self.enable_shadow.set(settings.get('enable_shadow', False))
        self.shadow_color.set(settings.get('shadow_color', '#808080'))
        self.shadow_offset_x.set(settings.get('shadow_offset_x', 2))
        self.shadow_offset_y.set(settings.get('shadow_offset_y', 2))
        self.shadow_blur.set(settings.get('shadow_blur', 1))
        self.enable_stroke.set(settings.get('enable_stroke', False))
        self.stroke_color.set(settings.get('stroke_color', '#FFFFFF'))
        self.stroke_width.set(settings.get('stroke_width', 2))
        
        # 更新颜色显示控件
        self.color_display.config(bg=self.text_color.get())
        self.shadow_color_display.config(bg=self.shadow_color.get())
        self.stroke_color_display.config(bg=self.stroke_color.get())
        
        # 更新图片水印设置
        self.image_position_var.set(settings.get('image_position', 'bottom_right'))
        self.image_custom_x.set(settings.get('image_custom_x', 90))
        self.image_custom_y.set(settings.get('image_custom_y', 90))
        self.image_rotation_angle.set(settings.get('image_rotation_angle', 0))
        
        # 更新控件状态
        self.toggle_shadow_controls()
        self.toggle_stroke_controls()
    
    def export_images(self):
        """导出图片"""
        success_count = 0
        total_count = len(self.selected_images)
        
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("导出进度")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = ttk.Label(progress_window, text="准备导出...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
        progress_bar.pack(pady=10)
        progress_bar['maximum'] = total_count
        
        cancel_button = ttk.Button(progress_window, text="取消", command=progress_window.destroy)
        cancel_button.pack(pady=10)
        
        def process_images():
            nonlocal success_count
            
            for i, image_path in enumerate(self.selected_images):
                if not progress_window.winfo_exists():  # 检查窗口是否被关闭
                    break
                
                try:
                    # 更新进度
                    filename = os.path.basename(image_path)
                    progress_label.config(text=f"正在处理: {filename}")
                    progress_bar['value'] = i
                    progress_window.update()
                    
                    # 加载原图
                    original_image = self.image_processor.load_image(image_path)
                    if not original_image:
                        continue
                    
                    # 调整图片尺寸（如果启用）
                    processed_image = original_image
                    if self.enable_resize.get():
                        resize_params = self.get_resize_parameters()
                        if resize_params:
                            processed_image = self.image_processor.resize_image_advanced(
                                original_image, **resize_params
                            )
                    
                    # 应用水印
                    # 应用水印（使用当前设置的水印类型）
                    watermark_type = settings.get('watermark_type', 'text')
                    watermarked_image = self.watermark_manager.apply_watermark(processed_image, watermark_type)
                    
                    # 生成输出路径
                    output_path = self.file_manager.generate_output_path(
                        image_path, self.output_dir.get(),
                        self.naming_rule.get(), self.file_prefix.get(), self.file_suffix.get(),
                        self.output_format.get()
                    )
                    
                    # 保存图片
                    quality = self.jpeg_quality.get() if self.output_format.get() == 'JPEG' else 90
                    if self.image_processor.save_image(watermarked_image, output_path, 
                                                     self.output_format.get(), quality):
                        success_count += 1
                    
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
                    continue
            
            # 完成后关闭进度窗口
            if progress_window.winfo_exists():
                progress_window.destroy()
            
            # 显示结果
            messagebox.showinfo("导出完成", 
                              f"成功导出 {success_count}/{total_count} 个文件\n" +
                              f"输出目录: {self.output_dir.get()}")
            
            self.status_var.set(f"导出完成: {success_count}/{total_count}")
        
        # 在短暂延迟后开始处理（确保进度窗口显示）
        progress_window.after(100, process_images)
    
    def get_current_watermark_settings(self) -> dict:
        """获取当前水印设置"""
        return {
            'watermark_text': self.watermark_text.get(),
            'font_family': self.font_family.get(),
            'font_size': self.font_size.get(),
            'font_bold': self.font_bold.get(),
            'font_italic': self.font_italic.get(),
            'text_color': self.text_color.get(),
            'text_opacity': self.text_opacity.get(),
            'watermark_image_path': self.watermark_image_path.get(),
            'image_scale': self.image_scale.get(),
            'image_opacity': self.image_opacity.get(),
            'position': self.position_var.get(),
            'custom_x': self.custom_x.get(),
            'custom_y': self.custom_y.get(),
            'rotation_angle': self.rotation_angle.get(),
            'watermark_type': self.get_current_watermark_type(),
            # 文本样式效果
            'enable_shadow': self.enable_shadow.get(),
            'shadow_color': self.shadow_color.get(),
            'shadow_offset_x': self.shadow_offset_x.get(),
            'shadow_offset_y': self.shadow_offset_y.get(),
            'shadow_blur': self.shadow_blur.get(),
            'enable_stroke': self.enable_stroke.get(),
            'stroke_color': self.stroke_color.get(),
            'stroke_width': self.stroke_width.get(),
            # 图片水印设置
            'image_position': self.image_position_var.get(),
            'image_custom_x': self.image_custom_x.get(),
            'image_custom_y': self.image_custom_y.get(),
            'image_rotation_angle': self.image_rotation_angle.get()
        }
    
    def apply_watermark_settings(self, settings: dict):
        """应用水印设置"""
        # 更新水印管理器
        self.watermark_manager.load_settings(settings)
        
        # 更新UI控件
        self.update_ui_from_watermark_settings()
        
        # 刷新预览
        if self.preview_image:
            self.update_preview()
    
    def toggle_resize_controls(self):
        """切换尺寸调整控件的启用/禁用状态"""
        if self.enable_resize.get():
            # 启用尺寸调整控件
            for child in self.resize_options_frame.winfo_children():
                self._enable_widget(child)
        else:
            # 禁用尺寸调整控件
            for child in self.resize_options_frame.winfo_children():
                self._disable_widget(child)
    
    def _enable_widget(self, widget):
        """递归启用小部件"""
        try:
            widget.configure(state='normal')
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._enable_widget(child)
    
    def _disable_widget(self, widget):
        """递归禁用小部件"""
        try:
            widget.configure(state='disabled')
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._disable_widget(child)
    
    def on_resize_mode_change(self):
        """当调整模式改变时显示对应的输入框"""
        # 隐藏所有参数框
        self.percentage_frame.pack_forget()
        self.width_frame.pack_forget()
        self.height_frame.pack_forget()
        self.custom_frame.pack_forget()
        
        # 根据模式显示对应的参数框
        mode = self.resize_mode.get()
        if mode == "percentage":
            self.percentage_frame.pack(fill=tk.X)
        elif mode == "width":
            self.width_frame.pack(fill=tk.X)
        elif mode == "height":
            self.height_frame.pack(fill=tk.X)
        elif mode == "custom":
            self.custom_frame.pack(fill=tk.X)
    
    def get_resize_parameters(self):
        """获取当前的尺寸调整参数"""
        if not self.enable_resize.get():
            return None
        
        mode = self.resize_mode.get()
        params = {'mode': mode}
        
        if mode == "percentage":
            params['percentage'] = self.resize_percentage.get()
        elif mode == "width":
            params['width'] = self.resize_width.get()
        elif mode == "height":
            params['height'] = self.resize_height.get()
        elif mode == "custom":
            params['custom_width'] = self.custom_width.get()
            params['custom_height'] = self.custom_height.get()
            params['keep_aspect_ratio'] = self.keep_aspect_ratio.get()
        
        return params
    
    def toggle_shadow_controls(self):
        """切换阴影控件的启用/禁用状态"""
        if self.enable_shadow.get():
            # 启用阴影控件
            for child in self.shadow_params_frame.winfo_children():
                self._enable_widget(child)
        else:
            # 禁用阴影控件
            for child in self.shadow_params_frame.winfo_children():
                self._disable_widget(child)
    
    def toggle_stroke_controls(self):
        """切换描边控件的启用/禁用状态"""
        if self.enable_stroke.get():
            # 启用描边控件
            for child in self.stroke_params_frame.winfo_children():
                self._enable_widget(child)
        else:
            # 禁用描边控件
            for child in self.stroke_params_frame.winfo_children():
                self._disable_widget(child)
    
    def choose_shadow_color(self):
        """选择阴影颜色"""
        color = colorchooser.askcolor(initialcolor=self.shadow_color.get())[1]
        if color:
            self.shadow_color.set(color)
            self.shadow_color_display.config(bg=color)
    
    def choose_stroke_color(self):
        """选择描边颜色"""
        color = colorchooser.askcolor(initialcolor=self.stroke_color.get())[1]
        if color:
            self.stroke_color.set(color)
            self.stroke_color_display.config(bg=color)
