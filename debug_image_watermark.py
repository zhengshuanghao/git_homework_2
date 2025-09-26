#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试图片水印功能
创建一个简单的测试来验证UI中的图片水印是否工作
"""

from src.app import WatermarkApp
from src.watermark_manager import WatermarkManager
from PIL import Image, ImageDraw
import tkinter as tk
import os
import time

def create_simple_watermark():
    """创建简单的测试水印"""
    logo = Image.new('RGBA', (100, 50), color=(255, 0, 0, 150))
    draw = ImageDraw.Draw(logo)
    draw.text((20, 15), "LOGO", fill=(255, 255, 255, 255))
    
    watermark_path = "debug_watermark.png"
    logo.save(watermark_path)
    return watermark_path

def create_test_image():
    """创建测试图片"""
    img = Image.new('RGB', (300, 200), color=(100, 150, 200))
    draw = ImageDraw.Draw(img)
    draw.text((100, 80), "TEST IMAGE", fill=(255, 255, 255))
    
    test_path = "debug_test_image.jpg"
    img.save(test_path)
    return test_path

def test_ui_watermark_type_detection():
    """测试UI中的水印类型检测"""
    print("🧪 调试图片水印UI功能")
    print("="*50)
    
    # 创建测试文件
    watermark_path = create_simple_watermark()
    test_image_path = create_test_image()
    
    print(f"✓ 创建测试水印: {watermark_path}")
    print(f"✓ 创建测试图片: {test_image_path}")
    
    # 创建应用实例
    root = tk.Tk()
    app = WatermarkApp(root)
    
    print("✓ 应用程序已初始化")
    
    # 模拟用户操作
    print("\n📋 模拟用户操作:")
    
    # 1. 导入测试图片
    print("1. 导入测试图片...")
    app.selected_images = [test_image_path]
    app.current_image_index = 0
    app.load_current_image()
    print(f"   ✓ 导入成功，预览图片尺寸: {app.preview_image.size if app.preview_image else '无'}")
    
    # 2. 设置图片水印路径
    print("2. 设置图片水印...")
    app.watermark_image_path.set(watermark_path)
    print(f"   ✓ 设置水印路径: {app.watermark_image_path.get()}")
    
    # 3. 测试水印类型检测
    print("3. 测试水印类型检测...")
    watermark_type = app.get_current_watermark_type()
    print(f"   ✓ 检测到的水印类型: {watermark_type}")
    
    # 4. 手动触发预览更新
    print("4. 更新预览...")
    try:
        settings = app.get_current_watermark_settings()
        app.watermark_manager.load_settings(settings)
        
        if app.preview_image:
            watermarked = app.watermark_manager.apply_watermark(app.preview_image, watermark_type)
            output_path = "debug_watermark_result.png"
            watermarked.save(output_path)
            print(f"   ✓ 预览更新成功，结果保存到: {output_path}")
        else:
            print("   ❌ 没有预览图片")
            
    except Exception as e:
        print(f"   ❌ 预览更新失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 测试导出功能
    print("5. 测试导出功能...")
    try:
        # 设置输出目录
        app.output_dir.set("./")
        
        # 手动调用导出逻辑的核心部分
        settings = app.get_current_watermark_settings()
        app.watermark_manager.load_settings(settings)
        
        # 加载原始图片
        original_image = app.image_processor.load_image(test_image_path)
        if original_image:
            watermark_type = settings.get('watermark_type', 'text')
            watermarked = app.watermark_manager.apply_watermark(original_image, watermark_type)
            
            export_path = "debug_export_result.png"
            watermarked.save(export_path)
            print(f"   ✓ 导出成功: {export_path}")
        else:
            print("   ❌ 无法加载原始图片")
            
    except Exception as e:
        print(f"   ❌ 导出测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理
    root.destroy()
    
    # 清理临时文件
    for temp_file in [watermark_path, test_image_path]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("\n" + "="*50)
    print("📊 调试结果:")
    print(f"✓ 水印类型检测: {watermark_type}")
    print("✓ 检查生成的文件:")
    if os.path.exists("debug_watermark_result.png"):
        print("  - debug_watermark_result.png (预览结果)")
    if os.path.exists("debug_export_result.png"):
        print("  - debug_export_result.png (导出结果)")
    
    print("\n💡 解决方案:")
    print("1. 确保在图片水印页面选择了水印图片")
    print("2. 水印类型会根据当前页面和内容自动检测")
    print("3. 如果仍有问题，检查控制台的错误信息")

if __name__ == "__main__":
    test_ui_watermark_type_detection()
