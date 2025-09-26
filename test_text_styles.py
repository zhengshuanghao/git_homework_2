#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本水印样式效果测试示例
演示新增的阴影和描边效果功能
"""

from src.watermark_manager import WatermarkManager
from src.image_processor import ImageProcessor
from PIL import Image
import os

def test_text_styles():
    """测试文本样式功能"""
    print("=== 文本水印样式效果测试 ===\n")
    
    # 创建处理器和水印管理器
    watermark_manager = WatermarkManager()
    image_processor = ImageProcessor()
    
    # 创建测试图片（彩色渐变背景，方便看清楚效果）
    test_image = Image.new('RGB', (800, 600), color='lightblue')
    # 添加一些复杂背景
    from PIL import ImageDraw
    draw = ImageDraw.Draw(test_image)
    for i in range(0, 800, 50):
        for j in range(0, 600, 50):
            color = (int(255 * (i/800)), int(255 * (j/600)), 200)
            draw.rectangle([i, j, i+40, j+40], fill=color)
    
    print(f"测试图片尺寸: {test_image.size}")
    
    # 测试各种样式效果
    test_cases = [
        {
            'name': '纯文本（无效果）',
            'settings': {
                'watermark_text': '测试水印',
                'font_size': 48,
                'text_color': '#000000',
                'text_opacity': 80,
                'enable_shadow': False,
                'enable_stroke': False
            }
        },
        {
            'name': '阴影效果',
            'settings': {
                'watermark_text': '阴影水印',
                'font_size': 48,
                'text_color': '#FFFFFF',
                'text_opacity': 90,
                'enable_shadow': True,
                'shadow_color': '#000000',
                'shadow_offset_x': 3,
                'shadow_offset_y': 3,
                'shadow_blur': 2,
                'enable_stroke': False
            }
        },
        {
            'name': '描边效果',
            'settings': {
                'watermark_text': '描边水印',
                'font_size': 48,
                'text_color': '#FF0000',
                'text_opacity': 85,
                'enable_shadow': False,
                'enable_stroke': True,
                'stroke_color': '#FFFFFF',
                'stroke_width': 3
            }
        },
        {
            'name': '阴影+描边组合效果',
            'settings': {
                'watermark_text': '组合效果',
                'font_size': 52,
                'text_color': '#0066CC',
                'text_opacity': 90,
                'enable_shadow': True,
                'shadow_color': '#666666',
                'shadow_offset_x': 2,
                'shadow_offset_y': 2,
                'shadow_blur': 1,
                'enable_stroke': True,
                'stroke_color': '#FFFFFF',
                'stroke_width': 2
            }
        },
        {
            'name': '强阴影效果',
            'settings': {
                'watermark_text': '强阴影',
                'font_size': 44,
                'text_color': '#FFFF00',
                'text_opacity': 95,
                'enable_shadow': True,
                'shadow_color': '#000000',
                'shadow_offset_x': 5,
                'shadow_offset_y': 5,
                'shadow_blur': 4,
                'enable_stroke': False
            }
        }
    ]
    
    # 创建输出目录
    output_dir = "test_styles_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. 测试 {test_case['name']}:")
        
        try:
            # 应用设置
            watermark_manager.load_settings(test_case['settings'])
            
            # 应用水印
            result_image = watermark_manager.create_text_watermark(test_image)
            
            # 保存结果（可选）
            output_filename = f"{i:02d}_{test_case['name'].replace('+', '_').replace('（', '_').replace('）', '_')}.png"
            output_path = os.path.join(output_dir, output_filename)
            result_image.save(output_path, "PNG")
            
            print(f"   ✓ 样式效果已生成")
            print(f"   📁 保存到: {output_path}")
            
            # 显示设置信息
            settings = test_case['settings']
            if settings.get('enable_shadow'):
                print(f"   🌫️  阴影: 颜色{settings.get('shadow_color')} 偏移({settings.get('shadow_offset_x')},{settings.get('shadow_offset_y')}) 模糊{settings.get('shadow_blur')}")
            if settings.get('enable_stroke'):
                print(f"   ✏️  描边: 颜色{settings.get('stroke_color')} 宽度{settings.get('stroke_width')}")
                
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        print()
    
    print("=== 功能验证完成 ===")
    print("\n新功能说明:")
    print("📍 阴影效果:")
    print("  • 可设置阴影颜色、X/Y偏移量、模糊程度")
    print("  • 适合在浅色背景上增强深色文字的可读性")
    print("  • 模糊效果让阴影更自然")
    
    print("\n📍 描边效果:")
    print("  • 可设置描边颜色和宽度")
    print("  • 适合在复杂背景上突出文字")
    print("  • 圆形描边算法，效果更均匀")
    
    print("\n📍 组合使用:")
    print("  • 可以同时启用阴影和描边效果")
    print("  • 绘制顺序：阴影 → 描边 → 主文字")
    print("  • 大大增强文字在复杂背景下的可读性")
    
    print(f"\n💾 测试图片已保存到 {output_dir}/ 目录")
    print("🚀 在水印应用程序的'文本水印'页面中可以找到'文本样式效果'设置！")

if __name__ == "__main__":
    test_text_styles()
