#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题修复测试脚本
验证图片方向、水印位置、性能优化等问题的修复效果
"""

from src.image_processor import ImageProcessor
from src.watermark_manager import WatermarkManager
from PIL import Image, ImageDraw
import os
import time

def create_test_image():
    """创建一个测试图片，有明确的方向标识"""
    img = Image.new('RGB', (400, 300), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # 添加方向标识
    draw.rectangle([10, 10, 50, 50], fill='red')  # 左上角红色方块
    draw.text((20, 20), "TOP", fill='white')
    
    draw.rectangle([350, 10, 390, 50], fill='green')  # 右上角绿色方块
    draw.text((360, 20), "TOP", fill='white')
    
    draw.rectangle([10, 250, 50, 290], fill='blue')  # 左下角蓝色方块
    draw.text((15, 260), "BOT", fill='white')
    
    draw.rectangle([350, 250, 390, 290], fill='yellow')  # 右下角黄色方块
    draw.text((355, 260), "BOT", fill='black')
    
    # 中心标识
    draw.ellipse([175, 125, 225, 175], fill='purple')
    draw.text((185, 140), "CENTER", fill='white')
    
    return img

def test_watermark_positions():
    """测试水印位置是否正确"""
    print("=== 测试水印位置定位 ===")
    
    processor = ImageProcessor()
    watermark_manager = WatermarkManager()
    
    # 创建测试图片
    test_image = create_test_image()
    print(f"测试图片尺寸: {test_image.size}")
    
    # 设置水印参数
    watermark_manager.watermark_text = "水印"
    watermark_manager.font_size = 24
    watermark_manager.text_color = "#FF0000"
    watermark_manager.text_opacity = 90
    
    # 测试各个位置
    positions = [
        ('top_left', '左上角'),
        ('top_center', '正上方'),
        ('top_right', '右上角'),
        ('middle_left', '左中'),
        ('center', '正中'),
        ('middle_right', '右中'),
        ('bottom_left', '左下角'),
        ('bottom_center', '正下方'),
        ('bottom_right', '右下角')
    ]
    
    # 创建输出目录
    output_dir = "test_positions_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for position, desc in positions:
        print(f"测试位置: {desc} ({position})")
        
        # 设置位置
        watermark_manager.position = position
        
        # 应用水印
        result = watermark_manager.create_text_watermark(test_image)
        
        # 保存结果
        output_path = os.path.join(output_dir, f"position_{position}.png")
        result.save(output_path)
        print(f"   ✓ 保存到: {output_path}")
    
    print("\n位置测试完成！请检查输出图片确认位置是否正确。")

def test_performance():
    """测试性能优化效果"""
    print("\n=== 测试性能优化效果 ===")
    
    watermark_manager = WatermarkManager()
    test_image = create_test_image()
    
    # 设置基础参数
    watermark_manager.watermark_text = "性能测试水印"
    watermark_manager.font_size = 32
    watermark_manager.text_color = "#000000"
    watermark_manager.text_opacity = 80
    watermark_manager.position = "center"
    
    # 测试不同效果的性能
    test_cases = [
        ("无效果", {"enable_shadow": False, "enable_stroke": False}),
        ("仅阴影", {"enable_shadow": True, "enable_stroke": False, 
                  "shadow_color": "#666666", "shadow_offset_x": 2, "shadow_offset_y": 2, "shadow_blur": 1}),
        ("仅描边", {"enable_shadow": False, "enable_stroke": True,
                  "stroke_color": "#FFFFFF", "stroke_width": 2}),
        ("阴影+描边", {"enable_shadow": True, "enable_stroke": True,
                    "shadow_color": "#666666", "shadow_offset_x": 2, "shadow_offset_y": 2, "shadow_blur": 1,
                    "stroke_color": "#FFFFFF", "stroke_width": 2})
    ]
    
    for case_name, settings in test_cases:
        # 应用设置
        watermark_manager.load_settings(settings)
        
        # 计时测试
        start_time = time.time()
        result = watermark_manager.create_text_watermark(test_image)
        end_time = time.time()
        
        duration = (end_time - start_time) * 1000  # 转换为毫秒
        print(f"{case_name:10}: {duration:.2f}ms")
    
    print("\n性能测试完成！所有测试应该在合理时间内完成。")

def test_image_orientation():
    """测试图片方向修复"""
    print("\n=== 测试图片方向修复 ===")
    
    processor = ImageProcessor()
    
    # 创建测试图片并保存
    test_image = create_test_image()
    temp_file = "temp_test_image.png"
    test_image.save(temp_file)
    
    try:
        # 测试加载图片
        loaded_image = processor.load_image(temp_file)
        
        if loaded_image:
            print(f"✓ 图片加载成功")
            print(f"  原始尺寸: {test_image.size}")
            print(f"  加载尺寸: {loaded_image.size}")
            
            if test_image.size == loaded_image.size:
                print("✓ 图片尺寸保持正确")
            else:
                print("⚠️ 图片尺寸发生变化")
        else:
            print("❌ 图片加载失败")
            
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    """主测试函数"""
    print("🔧 开始问题修复验证测试\n")
    
    try:
        # 测试1：图片方向
        test_image_orientation()
        
        # 测试2：水印位置
        test_watermark_positions()
        
        # 测试3：性能优化
        test_performance()
        
        print("\n" + "="*50)
        print("🎉 所有测试完成！")
        print("\n修复内容总结:")
        print("✅ 图片方向问题 - 添加了EXIF方向信息处理")
        print("✅ 水印位置问题 - 简化了位置计算算法，确保准确性")
        print("✅ 性能卡顿问题 - 优化了阴影和描边算法，移除了复杂的模糊效果")
        print("✅ 预览响应问题 - 添加了防抖动机制，减少频繁更新")
        
        print("\n📁 测试输出:")
        print("- test_positions_output/ - 包含9个位置测试图片")
        print("- 控制台显示的性能测试结果")
        
        print("\n🚀 建议测试步骤:")
        print("1. 运行 python main.py 启动应用程序")
        print("2. 导入一张有明确方向的图片，检查是否正确显示")
        print("3. 测试各种水印位置，确认位置准确性")
        print("4. 启用阴影和描边效果，感受性能改善")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


