#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理模块
处理水印配置模板的保存、加载、管理功能
"""

import json
import os
import configparser
from typing import Dict, List, Optional
from datetime import datetime


class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        self.templates_dir = "templates"
        self.settings_file = os.path.join(self.templates_dir, "settings.ini")
        self.templates_file = os.path.join(self.templates_dir, "templates.json")
        
        # 确保模板目录存在
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # 初始化设置文件
        self.config = configparser.ConfigParser()
        self.load_app_settings()
        
        # 加载模板数据
        self.templates = self.load_templates()
    
    def load_app_settings(self):
        """加载应用设置"""
        if os.path.exists(self.settings_file):
            try:
                self.config.read(self.settings_file, encoding='utf-8')
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.config = configparser.ConfigParser()
    
    def save_app_settings(self):
        """保存应用设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_templates(self) -> Dict:
        """加载模板数据"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading templates: {e}")
        
        return {}
    
    def save_templates(self):
        """保存模板数据"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving templates: {e}")
    
    def save_template(self, name: str, watermark_settings: dict) -> bool:
        """保存水印设置为模板"""
        try:
            # 添加时间戳
            template_data = {
                'settings': watermark_settings.copy(),
                'created_time': datetime.now().isoformat(),
                'modified_time': datetime.now().isoformat()
            }
            
            # 如果模板已存在，更新修改时间
            if name in self.templates:
                template_data['created_time'] = self.templates[name].get('created_time', 
                                                                       datetime.now().isoformat())
            
            self.templates[name] = template_data
            self.save_templates()
            return True
            
        except Exception as e:
            print(f"Error saving template {name}: {e}")
            return False
    
    def load_template(self, name: str) -> Optional[dict]:
        """加载指定模板"""
        if name in self.templates:
            return self.templates[name]['settings'].copy()
        return None
    
    def delete_template(self, name: str) -> bool:
        """删除模板"""
        try:
            if name in self.templates:
                del self.templates[name]
                self.save_templates()
                return True
            return False
        except Exception as e:
            print(f"Error deleting template {name}: {e}")
            return False
    
    def get_template_list(self) -> List[str]:
        """获取模板名称列表"""
        return list(self.templates.keys())
    
    def get_template_info(self, name: str) -> Optional[dict]:
        """获取模板信息"""
        if name in self.templates:
            template = self.templates[name]
            return {
                'name': name,
                'created_time': template.get('created_time', ''),
                'modified_time': template.get('modified_time', ''),
                'settings_count': len(template.get('settings', {}))
            }
        return None
    
    def rename_template(self, old_name: str, new_name: str) -> bool:
        """重命名模板"""
        try:
            if old_name in self.templates and new_name not in self.templates:
                template_data = self.templates[old_name]
                template_data['modified_time'] = datetime.now().isoformat()
                self.templates[new_name] = template_data
                del self.templates[old_name]
                self.save_templates()
                return True
            return False
        except Exception as e:
            print(f"Error renaming template from {old_name} to {new_name}: {e}")
            return False
    
    def export_template(self, name: str, file_path: str) -> bool:
        """导出模板到文件"""
        try:
            if name in self.templates:
                template_data = {
                    'name': name,
                    'template': self.templates[name]
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, ensure_ascii=False, indent=2)
                return True
            return False
        except Exception as e:
            print(f"Error exporting template {name}: {e}")
            return False
    
    def import_template(self, file_path: str) -> Optional[str]:
        """从文件导入模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'name' in data and 'template' in data:
                name = data['name']
                template_data = data['template']
                
                # 如果模板名已存在，添加数字后缀
                original_name = name
                counter = 1
                while name in self.templates:
                    name = f"{original_name}_{counter}"
                    counter += 1
                
                # 更新时间戳
                template_data['modified_time'] = datetime.now().isoformat()
                if 'created_time' not in template_data:
                    template_data['created_time'] = datetime.now().isoformat()
                
                self.templates[name] = template_data
                self.save_templates()
                return name
            
            return None
            
        except Exception as e:
            print(f"Error importing template from {file_path}: {e}")
            return None
    
    def save_last_settings(self, watermark_manager):
        """保存最后使用的设置"""
        try:
            if 'LastSettings' not in self.config:
                self.config.add_section('LastSettings')
            
            settings = watermark_manager.get_settings()
            for key, value in settings.items():
                self.config.set('LastSettings', key, str(value))
            
            self.save_app_settings()
            
        except Exception as e:
            print(f"Error saving last settings: {e}")
    
    def load_last_settings(self, watermark_manager):
        """加载最后使用的设置"""
        try:
            if 'LastSettings' in self.config:
                settings = {}
                for key in self.config['LastSettings']:
                    value = self.config.get('LastSettings', key)
                    
                    # 类型转换
                    if key in ['font_size', 'text_opacity', 'image_scale', 'image_opacity', 
                             'custom_x', 'custom_y', 'rotation_angle']:
                        settings[key] = int(value)
                    elif key in ['font_bold', 'font_italic']:
                        settings[key] = value.lower() == 'true'
                    else:
                        settings[key] = value
                
                watermark_manager.load_settings(settings)
                
        except Exception as e:
            print(f"Error loading last settings: {e}")
    
    def get_default_template(self) -> dict:
        """获取默认模板设置"""
        return {
            'watermark_text': "水印文本",
            'font_family': "Arial", 
            'font_size': 36,
            'font_bold': False,
            'font_italic': False,
            'text_color': "#000000",
            'text_opacity': 80,
            'watermark_image_path': "",
            'image_scale': 50,
            'image_opacity': 80,
            'position': "center",
            'custom_x': 50,
            'custom_y': 50,
            'rotation_angle': 0,
            'watermark_type': "text"
        }
    
    def create_default_templates(self):
        """创建默认模板"""
        default_templates = {
            "默认文本水印": {
                'settings': {
                    'watermark_text': "版权所有",
                    'font_family': "Arial",
                    'font_size': 36,
                    'font_bold': False,
                    'font_italic': False,
                    'text_color': "#FFFFFF",
                    'text_opacity': 70,
                    'position': "bottom_right",
                    'watermark_type': "text"
                },
                'created_time': datetime.now().isoformat(),
                'modified_time': datetime.now().isoformat()
            },
            "透明文本水印": {
                'settings': {
                    'watermark_text': "WATERMARK",
                    'font_family': "Arial",
                    'font_size': 48,
                    'font_bold': True,
                    'font_italic': False,
                    'text_color': "#000000",
                    'text_opacity': 30,
                    'position': "center",
                    'rotation_angle': 45,
                    'watermark_type': "text"
                },
                'created_time': datetime.now().isoformat(),
                'modified_time': datetime.now().isoformat()
            }
        }
        
        # 只添加不存在的默认模板
        for name, template in default_templates.items():
            if name not in self.templates:
                self.templates[name] = template
        
        self.save_templates()
