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
        
        # 图片水印页面
        self.create_image_watermark_tab(notebook)
        
        # 位置设置页面
        self.create_position_tab(notebook)
        
        # 导出设置页面
        self.create_export_tab(notebook)
        
        # 模板管理页面
        self.create_template_tab(notebook)
    
    def create_text_watermark_tab(self, parent):
        """创建文本水印设置页面"""
        text_frame = ttk.Frame(parent)
        parent.add(text_frame, text="文本水印")
        
        # 创建滚动视图
        canvas = tk.Canvas(text_frame)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
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
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_image_watermark_tab(self, parent):
        """创建图片水印设置页面"""
        image_frame = ttk.Frame(parent)
        parent.add(image_frame, text="图片水印")
        
        # 图片选择
        ttk.Label(image_frame, text="水印图片:").pack(anchor=tk.W, pady=(0, 5))
        
        select_frame = ttk.Frame(image_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.watermark_image_path = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.watermark_image_path, state=tk.DISABLED).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(select_frame, text="选择", command=self.select_watermark_image).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 图片缩放
        ttk.Label(image_frame, text="缩放比例:").pack(anchor=tk.W, pady=(10, 5))
        self.image_scale = tk.IntVar(value=50)
        scale_scale = ttk.Scale(image_frame, from_=10, to=200, variable=self.image_scale, orient=tk.HORIZONTAL)
        scale_scale.pack(fill=tk.X, pady=(0, 5))
        
        scale_label = ttk.Label(image_frame, textvariable=self.image_scale)
        scale_label.pack(anchor=tk.W)
        
        # 图片透明度
        ttk.Label(image_frame, text="透明度:").pack(anchor=tk.W, pady=(10, 5))
        self.image_opacity = tk.IntVar(value=80)
        img_opacity_scale = ttk.Scale(image_frame, from_=0, to=100, variable=self.image_opacity, orient=tk.HORIZONTAL)
        img_opacity_scale.pack(fill=tk.X, pady=(0, 5))
        
        img_opacity_label = ttk.Label(image_frame, textvariable=self.image_opacity)
        img_opacity_label.pack(anchor=tk.W)
        
    def create_position_tab(self, parent):
        """创建位置设置页面"""
        position_frame = ttk.Frame(parent)
        parent.add(position_frame, text="位置设置")
        
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
                           value=value).grid(row=row, column=col, padx=2, pady=2)
        
        # 自定义位置
        ttk.Label(position_frame, text="自定义位置:").pack(anchor=tk.W, pady=(20, 5))
        
        pos_frame = ttk.Frame(position_frame)
        pos_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT)
        self.custom_x = tk.IntVar(value=50)
        x_spin = ttk.Spinbox(pos_frame, from_=0, to=100, textvariable=self.custom_x, width=10)
        x_spin.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT)
        self.custom_y = tk.IntVar(value=50)
        y_spin = ttk.Spinbox(pos_frame, from_=0, to=100, textvariable=self.custom_y, width=10)
        y_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # 旋转角度
        ttk.Label(position_frame, text="旋转角度:").pack(anchor=tk.W, pady=(20, 5))
        self.rotation_angle = tk.IntVar(value=0)
        rotation_scale = ttk.Scale(position_frame, from_=-180, to=180, variable=self.rotation_angle, orient=tk.HORIZONTAL)
        rotation_scale.pack(fill=tk.X, pady=(0, 5))
        
        rotation_label = ttk.Label(position_frame, textvariable=self.rotation_angle)
        rotation_label.pack(anchor=tk.W)
        
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
                   self.image_opacity, self.watermark_image_path]:
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
        self.preview_image = self.image_processor.load_image(current_file)
        
        if self.preview_image:
            self.update_preview()
            filename = os.path.basename(current_file)
            self.status_var.set(f"当前图片: {filename}")
        else:
            messagebox.showerror("错误", f"无法加载图片: {current_file}")
    
    def update_preview(self):
        """更新预览显示"""
        if not self.preview_image:
            return
        
        # 应用水印
        watermarked_image = self.watermark_manager.apply_watermark(self.preview_image)
        
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
        """水印设置变化事件"""
        # 更新水印管理器设置
        settings = self.get_current_watermark_settings()
        self.watermark_manager.load_settings(settings)
        
        # 刷新预览
        if self.preview_image:
            # 延迟更新以避免频繁刷新
            self.root.after_idle(self.update_preview)
    
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
        
        # 更新颜色显示
        self.color_display.config(bg=self.text_color.get())
    
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
                    
                    # 应用水印
                    watermarked_image = self.watermark_manager.apply_watermark(original_image)
                    
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
            'watermark_type': "text" if self.watermark_text.get() else "image"
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
