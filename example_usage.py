#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印应用程序使用示例
演示如何程序化地使用核心功能
"""

from src.image_processor import ImageProcessor
from src.watermark_manager import WatermarkManager
from src.file_manager import FileManager

def example_usage():
    """示例：如何程序化使用水印功能"""
    
    # 初始化组件
    image_processor = ImageProcessor()
    watermark_manager = WatermarkManager()
    file_manager = FileManager()
    
    print("=== 水印应用程序使用示例 ===")
    
    # 示例1：创建文本水印
    print("\n1. 配置文本水印...")
    watermark_manager.watermark_text = "示例水印"
    watermark_manager.font_size = 48
    watermark_manager.text_color = "#FF0000"
    watermark_manager.text_opacity = 70
    watermark_manager.position = "bottom_right"
    watermark_manager.watermark_type = "text"
    
    print(f"   - 水印文本: {watermark_manager.watermark_text}")
    print(f"   - 字体大小: {watermark_manager.font_size}")
    print(f"   - 文本颜色: {watermark_manager.text_color}")
    print(f"   - 透明度: {watermark_manager.text_opacity}%")
    print(f"   - 位置: {watermark_manager.position}")
    
    # 检查支持的文件格式
    print(f"\n2. 支持的文件格式:")
    print(f"   - 输入格式: {image_processor.SUPPORTED_FORMATS['input']}")
    print(f"   - 输出格式: {image_processor.SUPPORTED_FORMATS['output']}")
    
    # 文件管理示例
    print("\n3. 文件命名示例:")
    example_file = "test_image.jpg"
    examples = [
        ("original", "", ""),
        ("prefix", "wm_", ""),
        ("suffix", "", "_watermarked")
    ]
    
    for rule, prefix, suffix in examples:
        new_name = file_manager.generate_output_filename(
            example_file, rule, prefix, suffix, "PNG"
        )
        print(f"   - {rule}: {example_file} -> {new_name}")
    
    print("\n=== 启动图形界面应用程序 ===")
    print("请运行: python main.py")

if __name__ == "__main__":
    example_usage()
