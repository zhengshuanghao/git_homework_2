#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片尺寸调整功能测试示例
演示新增的尺寸调整功能
"""

from src.image_processor import ImageProcessor
from PIL import Image
import os

def test_resize_functionality():
    """测试尺寸调整功能"""
    print("=== 图片尺寸调整功能测试 ===\n")
    
    # 创建处理器
    processor = ImageProcessor()
    
    # 创建测试图片（如果没有真实图片的话）
    test_image = Image.new('RGB', (800, 600), color='lightblue')
    print(f"原始图片尺寸: {test_image.size}")
    
    # 测试各种调整模式
    test_cases = [
        {
            'name': '按百分比缩放（50%）',
            'mode': 'percentage',
            'kwargs': {'percentage': 50}
        },
        {
            'name': '按宽度缩放（400像素）',
            'mode': 'width', 
            'kwargs': {'width': 400}
        },
        {
            'name': '按高度缩放（300像素）',
            'mode': 'height',
            'kwargs': {'height': 300}
        },
        {
            'name': '自定义尺寸（保持宽高比）',
            'mode': 'custom',
            'kwargs': {'custom_width': 640, 'custom_height': 480, 'keep_aspect_ratio': True}
        },
        {
            'name': '自定义尺寸（不保持宽高比）', 
            'mode': 'custom',
            'kwargs': {'custom_width': 640, 'custom_height': 480, 'keep_aspect_ratio': False}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}:")
        
        try:
            resized = processor.resize_image_advanced(
                test_image, 
                test_case['mode'],
                **test_case['kwargs']
            )
            print(f"   结果尺寸: {resized.size}")
            print(f"   缩放比例: {resized.size[0]/test_image.size[0]:.2f} x {resized.size[1]/test_image.size[1]:.2f}")
        except Exception as e:
            print(f"   错误: {e}")
        
        print()
    
    print("=== 功能验证完成 ===")
    print("\n新功能说明:")
    print("• 按百分比缩放: 输入10-500%的缩放比例")
    print("• 按宽度缩放: 指定目标宽度，高度自动按比例调整")
    print("• 按高度缩放: 指定目标高度，宽度自动按比例调整")
    print("• 自定义尺寸: 可选择是否保持宽高比")
    print("\n在导出设置页面中启用'图片尺寸调整'即可使用此功能！")

if __name__ == "__main__":
    test_resize_functionality()
