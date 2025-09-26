#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印管理模块
处理文本和图片水印的创建、应用等功能
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import math
from typing import Optional, Tuple, Union


class WatermarkManager:
    """水印管理器"""
    
    def __init__(self):
        # 默认设置
        self.reset_to_defaults()
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        # 文本水印设置
        self.watermark_text = "水印文本"
        self.font_family = "Arial"
        self.font_size = 36
        self.font_bold = False
        self.font_italic = False
        self.text_color = "#000000"
        self.text_opacity = 80
        
        # 图片水印设置
        self.watermark_image_path = ""
        self.image_scale = 50
        self.image_opacity = 80
        
        # 位置设置
        self.position = "center"  # 预设位置
        self.custom_x = 50  # 百分比
        self.custom_y = 50  # 百分比
        self.rotation_angle = 0
        
        # 水印类型
        self.watermark_type = "text"  # "text" 或 "image"
    
    def get_font(self, size: Optional[int] = None) -> ImageFont.FreeTypeFont:
        """获取字体对象"""
        if size is None:
            size = self.font_size
        
        try:
            # 尝试系统字体
            font_name = self.font_family
            
            # Windows字体路径
            if os.name == 'nt':
                font_paths = {
                    "Arial": "C:/Windows/Fonts/arial.ttf",
                    "Times New Roman": "C:/Windows/Fonts/times.ttf",
                    "Helvetica": "C:/Windows/Fonts/arial.ttf",
                    "Courier": "C:/Windows/Fonts/cour.ttf",
                    "微软雅黑": "C:/Windows/Fonts/msyh.ttc",
                    "宋体": "C:/Windows/Fonts/simsun.ttc",
                    "黑体": "C:/Windows/Fonts/simhei.ttf"
                }
            else:
                # macOS/Linux字体路径
                font_paths = {
                    "Arial": "/System/Library/Fonts/Arial.ttf",
                    "Times New Roman": "/System/Library/Fonts/Times New Roman.ttf",
                    "Helvetica": "/System/Library/Fonts/Helvetica.ttc",
                    "Courier": "/System/Library/Fonts/Courier New.ttf"
                }
            
            font_path = font_paths.get(font_name)
            if font_path and os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
            
            # 如果找不到指定字体，使用默认字体
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()
    
    def hex_to_rgba(self, hex_color: str, opacity: int) -> Tuple[int, int, int, int]:
        """将十六进制颜色转换为RGBA"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        alpha = int(255 * opacity / 100)
        return rgb + (alpha,)
    
    def calculate_position(self, image_size: Tuple[int, int], 
                         watermark_size: Tuple[int, int], 
                         position: str = None) -> Tuple[int, int]:
        """计算水印位置"""
        if position is None:
            position = self.position
        
        img_width, img_height = image_size
        wm_width, wm_height = watermark_size
        
        # 预设位置
        positions_map = {
            'top_left': (20, 20),
            'top_center': ((img_width - wm_width) // 2, 20),
            'top_right': (img_width - wm_width - 20, 20),
            'middle_left': (20, (img_height - wm_height) // 2),
            'center': ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
            'middle_right': (img_width - wm_width - 20, (img_height - wm_height) // 2),
            'bottom_left': (20, img_height - wm_height - 20),
            'bottom_center': ((img_width - wm_width) // 2, img_height - wm_height - 20),
            'bottom_right': (img_width - wm_width - 20, img_height - wm_height - 20)
        }
        
        if position == 'custom':
            # 自定义位置（百分比）
            x = int(img_width * self.custom_x / 100) - wm_width // 2
            y = int(img_height * self.custom_y / 100) - wm_height // 2
        else:
            x, y = positions_map.get(position, positions_map['center'])
        
        # 确保水印不超出图像边界
        x = max(0, min(x, img_width - wm_width))
        y = max(0, min(y, img_height - wm_height))
        
        return x, y
    
    def create_text_watermark(self, image: Image.Image) -> Image.Image:
        """创建文本水印"""
        # 创建副本以避免修改原图
        watermarked = image.copy()
        
        if not self.watermark_text:
            return watermarked
        
        # 根据图像大小调整字体大小
        base_font_size = self.font_size
        scale_factor = min(image.size[0], image.size[1]) / 800
        scaled_font_size = max(12, int(base_font_size * scale_factor))
        
        # 获取字体
        font = self.get_font(scaled_font_size)
        
        # 创建文本图层
        text_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), self.watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        x, y = self.calculate_position(image.size, (text_width, text_height))
        
        # 绘制文本
        color = self.hex_to_rgba(self.text_color, self.text_opacity)
        draw.text((x, y), self.watermark_text, font=font, fill=color)
        
        # 应用旋转
        if self.rotation_angle != 0:
            text_layer = text_layer.rotate(self.rotation_angle, expand=1)
            # 重新计算位置以保持中心对齐
            new_x = (watermarked.size[0] - text_layer.size[0]) // 2
            new_y = (watermarked.size[1] - text_layer.size[1]) // 2
            
            # 创建新的文本图层
            rotated_layer = Image.new('RGBA', watermarked.size, (0, 0, 0, 0))
            rotated_layer.paste(text_layer, (new_x, new_y), text_layer)
            text_layer = rotated_layer
        
        # 合并图层
        if watermarked.mode != 'RGBA':
            watermarked = watermarked.convert('RGBA')
        
        watermarked = Image.alpha_composite(watermarked, text_layer)
        
        return watermarked
    
    def create_image_watermark(self, image: Image.Image) -> Image.Image:
        """创建图片水印"""
        if not self.watermark_image_path or not os.path.exists(self.watermark_image_path):
            return image.copy()
        
        try:
            # 加载水印图片
            watermark_img = Image.open(self.watermark_image_path)
            
            # 确保水印图片有透明通道
            if watermark_img.mode != 'RGBA':
                watermark_img = watermark_img.convert('RGBA')
            
            # 计算缩放尺寸
            original_size = watermark_img.size
            scale_factor = self.image_scale / 100.0
            new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
            
            # 缩放水印图片
            watermark_img = watermark_img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 调整透明度
            if self.image_opacity < 100:
                # 创建透明度蒙版
                alpha = watermark_img.split()[3]  # 获取alpha通道
                alpha = alpha.point(lambda p: int(p * self.image_opacity / 100))
                watermark_img.putalpha(alpha)
            
            # 计算位置
            x, y = self.calculate_position(image.size, watermark_img.size)
            
            # 应用旋转
            if self.rotation_angle != 0:
                watermark_img = watermark_img.rotate(self.rotation_angle, expand=True)
                # 重新计算位置
                x = x - (watermark_img.size[0] - new_size[0]) // 2
                y = y - (watermark_img.size[1] - new_size[1]) // 2
            
            # 创建副本并应用水印
            watermarked = image.copy()
            if watermarked.mode != 'RGBA':
                watermarked = watermarked.convert('RGBA')
            
            # 创建水印图层
            watermark_layer = Image.new('RGBA', watermarked.size, (0, 0, 0, 0))
            
            # 确保位置在图像范围内
            x = max(0, min(x, watermarked.size[0] - watermark_img.size[0]))
            y = max(0, min(y, watermarked.size[1] - watermark_img.size[1]))
            
            watermark_layer.paste(watermark_img, (x, y), watermark_img)
            
            # 合并图层
            watermarked = Image.alpha_composite(watermarked, watermark_layer)
            
            return watermarked
            
        except Exception as e:
            print(f"Error creating image watermark: {e}")
            return image.copy()
    
    def apply_watermark(self, image: Image.Image, watermark_type: str = None) -> Image.Image:
        """应用水印到图像"""
        if watermark_type is None:
            watermark_type = self.watermark_type
        
        if watermark_type == "text":
            return self.create_text_watermark(image)
        elif watermark_type == "image":
            return self.create_image_watermark(image)
        else:
            return image.copy()
    
    def get_settings(self) -> dict:
        """获取当前水印设置"""
        return {
            'watermark_text': self.watermark_text,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_bold': self.font_bold,
            'font_italic': self.font_italic,
            'text_color': self.text_color,
            'text_opacity': self.text_opacity,
            'watermark_image_path': self.watermark_image_path,
            'image_scale': self.image_scale,
            'image_opacity': self.image_opacity,
            'position': self.position,
            'custom_x': self.custom_x,
            'custom_y': self.custom_y,
            'rotation_angle': self.rotation_angle,
            'watermark_type': self.watermark_type
        }
    
    def load_settings(self, settings: dict):
        """加载水印设置"""
        for key, value in settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
