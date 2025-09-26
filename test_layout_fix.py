#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布局显示修复测试
测试滚动界面是否能正确显示所有内容
"""

import tkinter as tk
from tkinter import ttk

def create_test_scrollable_window():
    """创建测试滚动窗口"""
    root = tk.Tk()
    root.title("滚动界面布局测试")
    root.geometry("600x500")
    
    # 创建Notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 测试页面1 - 类似文本水印页面
    test_frame1 = ttk.Frame(notebook)
    notebook.add(test_frame1, text="测试页面1")
    
    # 创建滚动视图
    canvas = tk.Canvas(test_frame1, highlightthickness=0)
    v_scrollbar = ttk.Scrollbar(test_frame1, orient="vertical", command=canvas.yview)
    h_scrollbar = ttk.Scrollbar(test_frame1, orient="horizontal", command=canvas.xview)
    scrollable_frame = ttk.Frame(canvas)
    
    # 绑定滚动事件
    def _bound_to_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Shift-MouseWheel>", _on_h_mousewheel)
        
    def _unbound_to_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Shift-MouseWheel>")
        
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def _on_h_mousewheel(event):
        canvas.xview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind('<Enter>', _bound_to_mousewheel)
    canvas.bind('<Leave>', _unbound_to_mousewheel)
    
    # 动态调整canvas窗口大小
    def _configure_scrollable_frame(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas_width = canvas.winfo_width()
        frame_width = scrollable_frame.winfo_reqwidth()
        if frame_width < canvas_width:
            canvas.itemconfig("scrollable_window", width=canvas_width)
    
    def _configure_canvas(event):
        canvas_width = canvas.winfo_width()
        canvas.itemconfig("scrollable_window", width=canvas_width)
    
    scrollable_frame.bind("<Configure>", _configure_scrollable_frame)
    canvas.bind('<Configure>', _configure_canvas)
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="scrollable_window")
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # 添加大量测试内容
    for i in range(20):
        group = ttk.LabelFrame(scrollable_frame, text=f"测试组 {i+1}", padding=5)
        group.pack(fill=tk.X, pady=(0, 10))
        
        # 每组内添加多个控件
        for j in range(3):
            row_frame = ttk.Frame(group)
            row_frame.pack(fill=tk.X, pady=(0, 5))
            
            ttk.Label(row_frame, text=f"选项 {i+1}-{j+1}:").pack(side=tk.LEFT)
            ttk.Entry(row_frame, width=15).pack(side=tk.LEFT, padx=(5, 0))
            ttk.Scale(row_frame, from_=0, to=100, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            ttk.Label(row_frame, text="100%").pack(side=tk.LEFT, padx=(5, 0))
    
    # 布局滚动组件 - 使用grid布局
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    # 配置网格权重
    test_frame1.grid_rowconfigure(0, weight=1)
    test_frame1.grid_columnconfigure(0, weight=1)
    
    # 状态标签
    status_label = ttk.Label(root, text="✅ 布局修复完成 - 使用鼠标滚轮测试垂直滚动，Shift+滚轮测试水平滚动")
    status_label.pack(side=tk.BOTTOM, pady=(5, 0))
    
    return root

def main():
    """主函数"""
    print("🧪 滚动界面布局修复测试")
    print("=" * 50)
    print("测试内容:")
    print("1. 垂直滚动 - 使用鼠标滚轮")
    print("2. 水平滚动 - Shift + 鼠标滚轮") 
    print("3. 内容完整显示 - 右侧不会被截断")
    print("4. 动态宽度调整 - 窗口大小改变时自动适应")
    print()
    print("🔍 预期效果:")
    print("- 所有控件都能完整显示")
    print("- 滚动条出现在正确位置")
    print("- 右侧内容不会被截断")
    print("- 滚动操作流畅无卡顿")
    print()
    
    try:
        root = create_test_scrollable_window()
        print("✅ 测试窗口已启动")
        print("📝 请验证:")
        print("  1. 右侧内容是否完整显示")
        print("  2. 滚动条是否正常工作")
        print("  3. 窗口缩放时是否适应良好")
        print()
        print("按 Ctrl+C 退出测试")
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n🛑 测试已中断")
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
