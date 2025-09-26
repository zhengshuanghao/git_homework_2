#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像处理模块
处理图像的加载、缩放、格式转换等功能
"""

from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from typing import Optional, Tuple, List


class ImageProcessor:
    """图像处理器"""
    
    SUPPORTED_FORMATS = {
        'input': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'],
        'output': ['JPEG', 'PNG']
    }
    
    def __init__(self):
        self.max_preview_size = (800, 600)
    
    def is_supported_image(self, file_path: str) -> bool:
        """检查文件是否为支持的图像格式"""
        if not os.path.isfile(file_path):
            return False
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.SUPPORTED_FORMATS['input']
    
    def load_image(self, file_path: str) -> Optional[Image.Image]:
        """加载图像文件"""
        try:
            if not self.is_supported_image(file_path):
                return None
            
            image = Image.open(file_path)
            # 确保图像是RGB模式（处理透明通道）
            if image.mode in ('RGBA', 'LA'):
                # 如果有透明通道，保留RGBA模式
                if image.mode == 'LA':
                    image = image.convert('RGBA')
            elif image.mode == 'P':
                # 调色板模式转换
                if 'transparency' in image.info:
                    image = image.convert('RGBA')
                else:
                    image = image.convert('RGB')
            elif image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            return None
    
    def create_preview(self, image: Image.Image, max_size: Optional[Tuple[int, int]] = None) -> Image.Image:
        """创建预览图像（缩放到合适大小）"""
        if max_size is None:
            max_size = self.max_preview_size
        
        # 计算缩放比例
        img_width, img_height = image.size
        max_width, max_height = max_size
        
        scale = min(max_width / img_width, max_height / img_height, 1.0)
        
        if scale < 1.0:
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image.copy()
    
    def create_thumbnail(self, image: Image.Image, size: Tuple[int, int] = (100, 100)) -> Image.Image:
        """创建缩略图"""
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail
    
    def pil_to_tkinter(self, image: Image.Image) -> ImageTk.PhotoImage:
        """将PIL图像转换为Tkinter可显示的PhotoImage"""
        return ImageTk.PhotoImage(image)
    
    def save_image(self, image: Image.Image, output_path: str, format: str = 'JPEG', quality: int = 90) -> bool:
        """保存图像到指定路径"""
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if format == 'JPEG':
                # JPEG不支持透明通道，需要转换为RGB
                if image.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[3])  # 使用alpha通道作为mask
                    else:
                        background.paste(image, mask=image.split()[1])  # 使用LA的A通道
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                image.save(output_path, format, quality=quality, optimize=True)
            elif format == 'PNG':
                # PNG支持透明通道
                image.save(output_path, format, optimize=True)
            else:
                return False
            
            return True
        except Exception as e:
            print(f"Error saving image to {output_path}: {e}")
            return False
    
    def get_image_info(self, image: Image.Image) -> dict:
        """获取图像信息"""
        return {
            'size': image.size,
            'mode': image.mode,
            'format': image.format,
            'width': image.size[0],
            'height': image.size[1]
        }
    
    def resize_image(self, image: Image.Image, width: Optional[int] = None, 
                    height: Optional[int] = None, percentage: Optional[float] = None) -> Image.Image:
        """调整图像大小"""
        original_width, original_height = image.size
        
        if percentage:
            new_width = int(original_width * percentage / 100)
            new_height = int(original_height * percentage / 100)
        elif width and height:
            new_width, new_height = width, height
        elif width:
            ratio = width / original_width
            new_width = width
            new_height = int(original_height * ratio)
        elif height:
            ratio = height / original_height
            new_height = height
            new_width = int(original_width * ratio)
        else:
            return image.copy()
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def resize_image_advanced(self, image: Image.Image, mode: str, **kwargs) -> Image.Image:
        """
        高级图像尺寸调整
        
        Args:
            image: 输入图像
            mode: 调整模式 - 'percentage', 'width', 'height', 'custom'
            **kwargs: 额外参数
                - percentage: 缩放百分比 (10-500)
                - width: 目标宽度
                - height: 目标高度  
                - custom_width: 自定义宽度
                - custom_height: 自定义高度
                - keep_aspect_ratio: 是否保持宽高比
        
        Returns:
            调整后的图像
        """
        original_width, original_height = image.size
        
        if mode == "percentage":
            # 按百分比缩放
            percentage = kwargs.get('percentage', 100)
            scale_factor = percentage / 100.0
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
        elif mode == "width":
            # 按宽度缩放，保持宽高比
            target_width = kwargs.get('width', original_width)
            ratio = target_width / original_width
            new_width = target_width
            new_height = int(original_height * ratio)
            
        elif mode == "height":
            # 按高度缩放，保持宽高比
            target_height = kwargs.get('height', original_height)
            ratio = target_height / original_height
            new_width = int(original_width * ratio)
            new_height = target_height
            
        elif mode == "custom":
            # 自定义尺寸
            target_width = kwargs.get('custom_width', original_width)
            target_height = kwargs.get('custom_height', original_height)
            keep_aspect_ratio = kwargs.get('keep_aspect_ratio', True)
            
            if keep_aspect_ratio:
                # 保持宽高比，选择较小的缩放比例
                width_ratio = target_width / original_width
                height_ratio = target_height / original_height
                ratio = min(width_ratio, height_ratio)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
            else:
                # 不保持宽高比，直接使用指定尺寸
                new_width = target_width
                new_height = target_height
        else:
            # 未知模式，返回原图
            return image.copy()
        
        # 确保尺寸合理
        new_width = max(1, min(new_width, 20000))  # 限制在1-20000像素之间
        new_height = max(1, min(new_height, 20000))
        
        # 如果尺寸没有变化，返回副本
        if new_width == original_width and new_height == original_height:
            return image.copy()
        
        # 执行缩放
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
