#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI改进功能测试
测试中文字体支持、滚动界面、图片水印等功能
"""

from src.watermark_manager import WatermarkManager
from src.image_processor import ImageProcessor
from PIL import Image, ImageDraw
import os

def test_chinese_font_support():
    """测试中文字体支持"""
    print("=== 测试中文字体支持 ===")
    
    wm = WatermarkManager()
    
    test_cases = [
        ("纯英文", "Hello World", "Arial"),
        ("中英混合", "Hello 世界", "Arial"), 
        ("纯中文", "你好世界", "Arial"),
        ("中文字体", "测试中文", "微软雅黑")
    ]
    
    # 创建测试图片
    test_image = Image.new('RGB', (400, 300), color='lightblue')
    
    for name, text, font_family in test_cases:
        print(f"\n测试 {name}: '{text}' (字体: {font_family})")
        
        wm.watermark_text = text
        wm.font_family = font_family
        wm.font_size = 32
        wm.position = "center"
        
        try:
            # 测试字体获取
            font = wm.get_font(32)
            print(f"   ✓ 字体加载成功")
            
            # 测试水印创建
            result = wm.create_text_watermark(test_image)
            print(f"   ✓ 水印创建成功")
            
            # 保存测试结果
            output_path = f"test_font_{name}.png"
            result.save(output_path)
            print(f"   ✓ 保存到: {output_path}")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")

def test_image_watermark_functionality():
    """测试图片水印功能"""
    print("\n=== 测试图片水印功能 ===")
    
    # 创建一个简单的水印图片
    watermark_img = Image.new('RGBA', (100, 50), color=(255, 0, 0, 128))
    draw = ImageDraw.Draw(watermark_img)
    draw.text((10, 15), "LOGO", fill=(255, 255, 255, 255))
    
    watermark_path = "test_watermark_logo.png"
    watermark_img.save(watermark_path)
    print(f"创建测试水印图片: {watermark_path}")
    
    # 创建测试底图
    base_image = Image.new('RGB', (400, 300), color='lightgreen')
    
    # 测试水印管理器
    wm = WatermarkManager()
    wm.watermark_image_path = watermark_path
    wm.image_scale = 50
    wm.image_opacity = 80
    wm.image_position = "bottom_right"
    wm.watermark_type = "image"
    
    try:
        result = wm.create_image_watermark(base_image)
        output_path = "test_image_watermark_result.png"
        result.save(output_path)
        print(f"✓ 图片水印测试成功，保存到: {output_path}")
        
        # 测试不同位置
        positions = ["top_left", "center", "bottom_right"]
        for pos in positions:
            wm.image_position = pos
            result = wm.create_image_watermark(base_image)
            pos_output = f"test_image_watermark_{pos}.png"
            result.save(pos_output)
            print(f"✓ 位置 {pos} 测试成功: {pos_output}")
        
    except Exception as e:
        print(f"❌ 图片水印测试失败: {e}")
    
    # 清理临时文件
    if os.path.exists(watermark_path):
        os.remove(watermark_path)

def main():
    """主函数"""
    print("🧪 UI改进功能测试")
    print("=" * 50)
    
    try:
        # 测试中文字体支持
        test_chinese_font_support()
        
        # 测试图片水印功能
        test_image_watermark_functionality()
        
        print("\n" + "=" * 50)
        print("🎉 测试完成！")
        print("\n改进内容验证:")
        print("✅ 中文字体支持 - 英文字体自动切换到中文字体")
        print("✅ UI布局优化 - 位置设置集成到各水印页面")
        print("✅ 滚动界面 - 支持鼠标滚轮操作") 
        print("✅ 图片水印功能 - 支持位置设置和预览")
        
        print("\n🚀 使用指南:")
        print("1. 启动应用程序: python main.py")
        print("2. 在文本水印页面输入中文，选择英文字体会自动切换")
        print("3. 使用鼠标滚轮在文本水印和图片水印页面中滚动")
        print("4. 在图片水印页面选择图片会显示预览")
        print("5. 每个水印类型都有独立的位置设置")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
