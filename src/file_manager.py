#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理模块
处理文件的导入、导出、批量处理等功能
"""

import os
import shutil
from typing import List, Optional, Tuple
from pathlib import Path


class FileManager:
    """文件管理器"""
    
    def __init__(self):
        self.supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        
    def get_supported_files(self, file_paths: List[str]) -> List[str]:
        """从文件路径列表中筛选出支持的图像文件"""
        supported_files = []
        
        for file_path in file_paths:
            if self.is_supported_image_file(file_path):
                supported_files.append(file_path)
        
        return supported_files
    
    def is_supported_image_file(self, file_path: str) -> bool:
        """检查文件是否为支持的图像格式"""
        if not os.path.isfile(file_path):
            return False
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_extensions
    
    def scan_directory_for_images(self, directory: str, recursive: bool = True) -> List[str]:
        """扫描目录中的图像文件"""
        image_files = []
        
        try:
            if recursive:
                # 递归扫描子目录
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.is_supported_image_file(file_path):
                            image_files.append(file_path)
            else:
                # 只扫描当前目录
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)
                    if self.is_supported_image_file(file_path):
                        image_files.append(file_path)
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return sorted(image_files)
    
    def generate_output_filename(self, original_path: str, naming_rule: str, 
                                prefix: str = "", suffix: str = "", 
                                output_format: str = "JPEG") -> str:
        """生成输出文件名"""
        original_dir = os.path.dirname(original_path)
        original_name = os.path.splitext(os.path.basename(original_path))[0]
        
        # 根据输出格式确定扩展名
        if output_format.upper() == "JPEG":
            ext = ".jpg"
        elif output_format.upper() == "PNG":
            ext = ".png"
        else:
            ext = ".jpg"  # 默认
        
        if naming_rule == "original":
            new_name = original_name + ext
        elif naming_rule == "prefix":
            new_name = prefix + original_name + ext
        elif naming_rule == "suffix":
            new_name = original_name + suffix + ext
        else:
            new_name = original_name + "_watermarked" + ext
        
        return new_name
    
    def generate_output_path(self, original_path: str, output_dir: str, 
                           naming_rule: str, prefix: str = "", suffix: str = "", 
                           output_format: str = "JPEG") -> str:
        """生成完整的输出路径"""
        filename = self.generate_output_filename(original_path, naming_rule, 
                                               prefix, suffix, output_format)
        return os.path.join(output_dir, filename)
    
    def is_safe_output_path(self, output_path: str, original_paths: List[str]) -> bool:
        """检查输出路径是否安全（不会覆盖原文件）"""
        output_path = os.path.abspath(output_path)
        
        for original_path in original_paths:
            original_path = os.path.abspath(original_path)
            if output_path == original_path:
                return False
            
            # 检查是否在原文件目录中
            original_dir = os.path.dirname(original_path)
            if output_path.startswith(original_dir + os.sep):
                # 如果在同一目录但文件名不同，则认为是安全的
                if os.path.basename(output_path) != os.path.basename(original_path):
                    continue
                return False
        
        return True
    
    def ensure_output_directory(self, output_dir: str) -> bool:
        """确保输出目录存在"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating output directory {output_dir}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'directory': os.path.dirname(file_path)
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return {'path': file_path, 'name': os.path.basename(file_path)}
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小为可读格式"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s}{size_names[i]}"
    
    def validate_output_settings(self, original_paths: List[str], output_dir: str, 
                                naming_rule: str, prefix: str = "", suffix: str = "",
                                output_format: str = "JPEG") -> Tuple[bool, str]:
        """验证输出设置"""
        if not output_dir:
            return False, "请选择输出目录"
        
        if not os.path.exists(output_dir):
            return False, "输出目录不存在"
        
        if not os.path.isdir(output_dir):
            return False, "输出路径不是目录"
        
        # 检查命名规则
        if naming_rule in ["prefix", "suffix"]:
            if naming_rule == "prefix" and not prefix.strip():
                return False, "请输入前缀"
            elif naming_rule == "suffix" and not suffix.strip():
                return False, "请输入后缀"
        
        # 检查是否会覆盖原文件
        for original_path in original_paths:
            output_path = self.generate_output_path(original_path, output_dir, 
                                                   naming_rule, prefix, suffix, output_format)
            if not self.is_safe_output_path(output_path, [original_path]):
                return False, f"输出文件可能覆盖原文件: {os.path.basename(output_path)}"
        
        # 检查文件名冲突
        output_files = set()
        for original_path in original_paths:
            output_filename = self.generate_output_filename(original_path, naming_rule,
                                                          prefix, suffix, output_format)
            if output_filename in output_files:
                return False, f"文件名冲突: {output_filename}"
            output_files.add(output_filename)
        
        return True, "设置有效"
    
    def backup_file(self, file_path: str) -> Optional[str]:
        """备份文件"""
        try:
            backup_path = file_path + ".bak"
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error backing up file {file_path}: {e}")
            return None
    
    def cleanup_temp_files(self, temp_files: List[str]):
        """清理临时文件"""
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error removing temp file {temp_file}: {e}")
    
    def get_unique_filename(self, base_path: str) -> str:
        """生成唯一的文件名（如果文件已存在则添加数字后缀）"""
        if not os.path.exists(base_path):
            return base_path
        
        directory = os.path.dirname(base_path)
        filename, ext = os.path.splitext(os.path.basename(base_path))
        
        counter = 1
        while True:
            new_filename = f"{filename}_{counter}{ext}"
            new_path = os.path.join(directory, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1
