#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片方向问题专项测试
用于诊断和验证EXIF方向处理是否正确
"""

from src.image_processor import ImageProcessor
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_images_with_orientation():
    """创建带有不同EXIF方向信息的测试图片"""
    print("=== 创建方向测试图片 ===")
    
    # 创建基础测试图片（竖向，300x400）
    base_image = Image.new('RGB', (300, 400), color='lightblue')
    draw = ImageDraw.Draw(base_image)
    
    # 添加方向标识
    # 顶部标识
    draw.rectangle([50, 20, 250, 80], fill='red')
    draw.text((120, 40), "TOP", fill='white', font=None)
    
    # 底部标识  
    draw.rectangle([50, 320, 250, 380], fill='blue')
    draw.text((110, 340), "BOTTOM", fill='white', font=None)
    
    # 左侧标识
    draw.rectangle([20, 150, 80, 250], fill='green')
    draw.text((35, 190), "LEFT", fill='white', font=None)
    
    # 右侧标识
    draw.rectangle([220, 150, 280, 250], fill='yellow')
    draw.text((230, 190), "RIGHT", fill='black', font=None)
    
    # 中心圆形
    draw.ellipse([125, 175, 175, 225], fill='purple')
    draw.text((135, 190), "CENTER", fill='white', font=None)
    
    # 保存原始图片（无旋转）
    test_dir = "orientation_test"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    original_path = os.path.join(test_dir, "original_portrait.png")
    base_image.save(original_path)
    print(f"原始竖向图片: {original_path} (尺寸: {base_image.size})")
    
    # 创建旋转版本用于测试
    rotated_90 = base_image.rotate(90, expand=True)  # 逆时针90度
    rotated_path = os.path.join(test_dir, "rotated_90_ccw.png")
    rotated_90.save(rotated_path)
    print(f"旋转90度图片: {rotated_path} (尺寸: {rotated_90.size})")
    
    return original_path, rotated_path

def test_exif_processing():
    """测试EXIF方向处理功能"""
    print("\n=== 测试EXIF方向处理 ===")
    
    processor = ImageProcessor()
    
    # 创建测试图片
    original_path, rotated_path = create_test_images_with_orientation()
    
    # 测试原始图片
    print(f"\n测试1: 加载原始图片")
    original_image = Image.open(original_path)
    print(f"原始尺寸: {original_image.size}")
    
    fixed_image = processor.fix_image_orientation(original_image)
    print(f"处理后尺寸: {fixed_image.size}")
    
    if original_image.size == fixed_image.size:
        print("✅ 原始图片方向保持正确")
    else:
        print(f"⚠️ 图片尺寸发生了变化")
    
    # 测试旋转图片
    print(f"\n测试2: 加载旋转图片")
    rotated_image = Image.open(rotated_path)
    print(f"旋转图片尺寸: {rotated_image.size}")
    
    fixed_rotated = processor.fix_image_orientation(rotated_image)
    print(f"处理后尺寸: {fixed_rotated.size}")
    
    # 使用完整的load_image方法测试
    print(f"\n测试3: 使用ImageProcessor.load_image()方法")
    processed_original = processor.load_image(original_path)
    processed_rotated = processor.load_image(rotated_path)
    
    if processed_original:
        print(f"原始图片加载结果: {processed_original.size}")
    if processed_rotated:
        print(f"旋转图片加载结果: {processed_rotated.size}")
    
    return processed_original, processed_rotated

def diagnose_user_image():
    """为用户提供图片诊断功能"""
    print("\n=== 用户图片诊断功能 ===")
    print("请按以下步骤测试您的图片：")
    print("1. 将您有问题的图片复制到当前目录")
    print("2. 重命名为 'user_test_image.jpg'")
    print("3. 重新运行此脚本")
    
    user_image_path = "user_test_image.jpg"
    if os.path.exists(user_image_path):
        print(f"找到用户测试图片: {user_image_path}")
        
        processor = ImageProcessor()
        
        # 直接用PIL打开
        pil_image = Image.open(user_image_path)
        print(f"PIL直接打开尺寸: {pil_image.size}")
        
        # 检查EXIF信息
        try:
            if hasattr(pil_image, '_getexif') and pil_image._getexif():
                exif = pil_image._getexif()
                orientation = exif.get(0x0112, 1)
                print(f"EXIF方向值: {orientation}")
                
                orientation_meanings = {
                    1: "正常方向",
                    2: "水平翻转", 
                    3: "旋转180度",
                    4: "垂直翻转",
                    5: "水平翻转+逆时针90度",
                    6: "顺时针90度",
                    7: "水平翻转+顺时针90度", 
                    8: "逆时针90度"
                }
                print(f"方向含义: {orientation_meanings.get(orientation, '未知')}")
            else:
                print("图片没有EXIF方向信息")
        except Exception as e:
            print(f"读取EXIF信息失败: {e}")
        
        # 使用我们的处理器加载
        processed_image = processor.load_image(user_image_path)
        if processed_image:
            print(f"处理器处理后尺寸: {processed_image.size}")
            
            # 保存处理后的结果供对比
            output_path = "user_image_processed.png"
            processed_image.save(output_path)
            print(f"处理后图片已保存到: {output_path}")
            
            if pil_image.size != processed_image.size:
                print("🔄 图片方向已被修正")
            else:
                print("📐 图片方向未改变")
        else:
            print("❌ 处理器无法加载图片")
    else:
        print(f"未找到用户测试图片 {user_image_path}")
        print("请放置您的测试图片并重新运行")

def main():
    """主函数"""
    print("🔍 图片方向问题专项诊断工具")
    print("="*50)
    
    try:
        # 基础测试
        test_exif_processing()
        
        # 用户图片诊断
        diagnose_user_image()
        
        print("\n" + "="*50)
        print("📋 诊断完成！")
        print("\n如果问题仍然存在，请：")
        print("1. 检查控制台输出的调试信息")
        print("2. 对比原始图片和处理后图片的方向")
        print("3. 将问题图片放到当前目录作为 'user_test_image.jpg' 进行专项测试")
        
        print("\n🔧 修复建议：")
        print("- 如果图片没有EXIF信息但仍然显示错误，可能是显示器或查看软件的问题")
        print("- 如果EXIF处理失败，请确保PIL版本足够新")
        print("- 某些相机或软件生成的EXIF信息可能不标准")
        
    except Exception as e:
        print(f"❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
