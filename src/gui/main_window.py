"""
主GUI窗口
视频翻译器的主用户界面
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from ttkthemes import ThemedTk
from ..core.video_processor import VideoProcessor
from ..core.subtitle_extractor import SubtitleExtractor
from ..core.translator import TranslationManager, TranslationProvider
from ..core.subtitle_writer import SubtitleWriter
from ..utils.config import get_config
from ..utils.logger import get_logger, init_logger
from ..utils.helpers import (
    is_video_file,
    get_video_files_in_directory,
    format_file_size,
    format_duration,
    get_system_info
)

logger = get_logger(__name__)


class ProgressDialog:
    """进度对话框"""

    def __init__(self, parent, title="处理中..."):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="正在初始化...")
        self.status_label.pack(pady=(0, 10))

        # 进度条
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode="determinate",
            length=300
        )
        self.progress_bar.pack(pady=(0, 10))

        # 详细信息
        self.detail_label = ttk.Label(main_frame, text="", font=("Arial", 8))
        self.detail_label.pack(pady=(0, 10))

        # 取消按钮
        self.cancel_button = ttk.Button(
            main_frame,
            text="取消",
            command=self.cancel
        )
        self.cancel_button.pack()

        self.cancelled = False

    def update_progress(self, current: int, total: int, status: str = "", detail: str = ""):
        """更新进度"""
        if self.cancelled:
            return

        progress = (current / total * 100) if total > 0 else 0
        self.progress_bar['value'] = progress

        if status:
            self.status_label.config(text=status)
        if detail:
            self.detail_label.config(text=detail)

        self.dialog.update_idletasks()

    def cancel(self):
        """取消操作"""
        self.cancelled = True
        self.dialog.destroy()

    def close(self):
        """关闭对话框"""
        self.dialog.destroy()


class VideoTranslatorGUI:
    """视频翻译器主界面"""

    def __init__(self):
        self.config = get_config()
        self.video_processor = VideoProcessor()
        self.subtitle_extractor = SubtitleExtractor()
        self.translation_manager = TranslationManager()
        self.subtitle_writer = SubtitleWriter()

        # 数据存储
        self.selected_files: List[Path] = []
        self.current_video_info = None
        self.translation_thread = None

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主窗口
        self.root = ThemedTk(theme=self.config.get('ui.theme', 'arc'))
        self.root.title("视频翻译器 - Video Translator")
        self.root.geometry(self.config.get('ui.window_size', '1200x800'))

        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap('assets/icon.ico')
            pass
        except:
            pass

        # 创建主菜单
        self.create_menu()

        # 创建主界面
        self.create_main_interface()

        # 绑定事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开视频文件", command=self.select_video_files)
        file_menu.add_command(label="打开文件夹", command=self.select_directory)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="设置", command=self.show_settings)
        tools_menu.add_command(label="清除日志", command=self.clear_logs)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_main_interface(self):
        """创建主界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建左右分割
        paned_window = ttk.PanedWindow(main_frame, orient="horizontal")
        paned_window.pack(fill="both", expand=True)

        # 左侧面板
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=2)

        # 右侧面板
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)

        # 创建左侧界面
        self.create_left_panel(left_frame)

        # 创建右侧界面
        self.create_right_panel(right_frame)

    def create_left_panel(self, parent):
        """创建左侧面板"""
        # 文件选择区域
        file_frame = ttk.LabelFrame(parent, text="文件选择", padding="10")
        file_frame.pack(fill="x", pady=(0, 10))

        # 按钮行
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            button_frame,
            text="选择视频文件",
            command=self.select_video_files
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            button_frame,
            text="选择文件夹",
            command=self.select_directory
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            button_frame,
            text="清除列表",
            command=self.clear_file_list
        ).pack(side="left")

        # 文件列表
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill="both", expand=True)

        # 创建Treeview
        columns = ("文件名", "格式", "大小", "状态")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=8)

        # 设置列
        self.file_tree.heading("#0", text="路径")
        self.file_tree.column("#0", width=200)

        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=80)

        # 滚动条
        scrollbar_y = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient="horizontal", command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # 布局
        self.file_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # 绑定选择事件
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)

        # 翻译设置区域
        settings_frame = ttk.LabelFrame(parent, text="翻译设置", padding="10")
        settings_frame.pack(fill="x", pady=(0, 10))

        # 第一行：AI提供商和模型
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill="x", pady=(0, 5))

        ttk.Label(row1, text="AI提供商:").pack(side="left")
        self.provider_var = tk.StringVar(value=self.config.get('translation.provider', 'openai'))
        provider_combo = ttk.Combobox(row1, textvariable=self.provider_var, state="readonly", width=15)
        provider_combo['values'] = [p.value for p in self.translation_manager.get_available_providers()]
        provider_combo.pack(side="left", padx=(5, 10))

        ttk.Label(row1, text="模型:").pack(side="left")
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(row1, textvariable=self.model_var, state="readonly", width=20)
        self.model_combo.pack(side="left", padx=(5, 0))

        # 第二行：目标语言和输出格式
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill="x", pady=(0, 5))

        ttk.Label(row2, text="目标语言:").pack(side="left")
        self.target_lang_var = tk.StringVar(value=self.config.get('translation.target_language', 'zh-CN'))
        lang_combo = ttk.Combobox(row2, textvariable=self.target_lang_var, state="readonly", width=15)

        # 设置语言选项
        languages = self.config.get_supported_languages()
        lang_combo['values'] = [f"{code} - {name}" for code, name in languages.items()]
        lang_combo.pack(side="left", padx=(5, 10))

        ttk.Label(row2, text="输出格式:").pack(side="left")
        self.output_format_var = tk.StringVar(value='srt')
        format_combo = ttk.Combobox(row2, textvariable=self.output_format_var, state="readonly", width=10)
        format_combo['values'] = ['srt', 'vtt', 'ass']
        format_combo.pack(side="left", padx=(5, 0))

        # 第三行：字幕选项
        row3 = ttk.Frame(settings_frame)
        row3.pack(fill="x", pady=(0, 5))

        self.bilingual_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row3, text="双语字幕", variable=self.bilingual_var).pack(side="left")

        self.extract_all_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row3, text="提取所有字幕轨道", variable=self.extract_all_var).pack(side="left", padx=(20, 0))

        # 绑定提供商变化事件
        provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)

        # 控制按钮区域
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x")

        self.start_button = ttk.Button(
            control_frame,
            text="开始翻译",
            command=self.start_translation,
            style="Accent.TButton"
        )
        self.start_button.pack(side="left", padx=(0, 10))

        self.stop_button = ttk.Button(
            control_frame,
            text="停止",
            command=self.stop_translation,
            state="disabled"
        )
        self.stop_button.pack(side="left")

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame,
            variable=self.progress_var,
            mode="determinate",
            length=200
        )
        self.progress_bar.pack(side="right")

        self.progress_label = ttk.Label(control_frame, text="就绪")
        self.progress_label.pack(side="right", padx=(0, 10))

    def create_right_panel(self, parent):
        """创建右侧面板"""
        # 创建笔记本控件
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)

        # 视频信息标签页
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="视频信息")

        # 创建视频信息显示
        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            wrap=tk.WORD,
            height=15,
            state="disabled"
        )
        self.info_text.pack(fill="both", expand=True, padx=5, pady=5)

        # 日志标签页
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="运行日志")

        # 创建日志显示
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=15,
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # 设置日志处理器
        self.setup_log_handler()

    def setup_log_handler(self):
        """设置日志处理器"""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.text_widget.config(state="normal")
                    self.text_widget.insert(tk.END, msg + "\n")
                    self.text_widget.see(tk.END)
                    self.text_widget.config(state="disabled")
                except:
                    pass

        # 添加GUI日志处理器
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        ))

        root_logger = logging.getLogger()
        root_logger.addHandler(gui_handler)

    def load_settings(self):
        """加载设置"""
        # 更新模型选择
        self.on_provider_change()

    def on_provider_change(self, event=None):
        """提供商变化事件"""
        provider = self.provider_var.get()
        providers_info = self.config.get_translation_providers()

        if provider in providers_info:
            models = providers_info[provider].get('models', [])
            self.model_combo['values'] = models
            if models:
                self.model_var.set(models[0])

    def select_video_files(self):
        """选择视频文件"""
        initial_dir = self.config.get_last_used_dir()

        filetypes = [
            ("视频文件", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v"),
            ("所有文件", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title="选择视频文件",
            initialdir=initial_dir,
            filetypes=filetypes
        )

        if files:
            # 更新最后使用的目录
            self.config.update_last_used_dir(str(Path(files[0]).parent))

            # 添加文件到列表
            for file_path in files:
                path = Path(file_path)
                if is_video_file(path) and path not in self.selected_files:
                    self.selected_files.append(path)

            self.update_file_list()

    def select_directory(self):
        """选择目录"""
        initial_dir = self.config.get_last_used_dir()

        directory = filedialog.askdirectory(
            title="选择包含视频文件的文件夹",
            initialdir=initial_dir
        )

        if directory:
            self.config.update_last_used_dir(directory)

            # 获取目录中的视频文件
            video_files = get_video_files_in_directory(directory, recursive=True)

            for file_path in video_files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)

            self.update_file_list()

            messagebox.showinfo(
                "信息",
                f"找到 {len(video_files)} 个视频文件"
            )

    def clear_file_list(self):
        """清除文件列表"""
        self.selected_files.clear()
        self.update_file_list()
        self.clear_video_info()

    def update_file_list(self):
        """更新文件列表显示"""
        # 清除现有项目
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # 添加文件
        for file_path in self.selected_files:
            file_size = format_file_size(file_path.stat().st_size)

            self.file_tree.insert(
                "", "end",
                text=str(file_path),
                values=(
                    file_path.name,
                    file_path.suffix.upper()[1:],
                    file_size,
                    "就绪"
                )
            )

    def on_file_select(self, event):
        """文件选择事件"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            file_path = Path(self.file_tree.item(item, "text"))
            self.load_video_info(file_path)

    def load_video_info(self, file_path: Path):
        """加载视频信息"""
        def load_info():
            try:
                video_info = self.video_processor.get_video_info(file_path)
                self.current_video_info = video_info

                # 在主线程更新UI
                self.root.after(0, lambda: self.display_video_info(video_info))

            except Exception as e:
                error_msg = f"加载视频信息失败: {e}"
                self.root.after(0, lambda: self.display_error(error_msg))

        # 在后台线程加载
        threading.Thread(target=load_info, daemon=True).start()

        # 显示加载中状态
        self.display_loading_info()

    def display_loading_info(self):
        """显示加载中信息"""
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "正在加载视频信息...\n")
        self.info_text.config(state="disabled")

    def display_video_info(self, video_info):
        """显示视频信息"""
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)

        info_text = f"""文件信息:
文件路径: {video_info.file_path}
文件大小: {format_file_size(video_info.file_size)}
格式: {video_info.format_name}
时长: {format_duration(video_info.duration)}

视频信息:
分辨率: {video_info.width} x {video_info.height}
编码: {video_info.video_codec}
帧率: {video_info.fps:.2f} fps
比特率: {video_info.bitrate} bps

音频信息:
编码: {video_info.audio_codec}
音频流数量: {len(video_info.audio_streams)}

字幕信息:
字幕轨道数量: {len(video_info.subtitle_streams)}
"""

        if video_info.subtitle_streams:
            info_text += "\n字幕轨道详情:\n"
            for i, subtitle in enumerate(video_info.subtitle_streams):
                info_text += f"  轨道 {i+1}: {subtitle.title} ({subtitle.language}, {subtitle.codec})\n"
        else:
            info_text += "\n未检测到字幕轨道\n"

        self.info_text.insert(tk.END, info_text)
        self.info_text.config(state="disabled")

    def display_error(self, error_msg: str):
        """显示错误信息"""
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"错误: {error_msg}\n")
        self.info_text.config(state="disabled")

    def clear_video_info(self):
        """清除视频信息"""
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state="disabled")
        self.current_video_info = None

    def start_translation(self):
        """开始翻译"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择视频文件")
            return

        if self.translation_thread and self.translation_thread.is_alive():
            messagebox.showwarning("警告", "翻译正在进行中")
            return

        # 获取设置
        provider_str = self.provider_var.get()
        target_lang = self.target_lang_var.get().split(' - ')[0]  # 提取语言代码
        output_format = self.output_format_var.get()
        bilingual = self.bilingual_var.get()
        extract_all = self.extract_all_var.get()

        # 验证API密钥
        if not self.config.validate_api_config(provider_str):
            messagebox.showerror(
                "错误",
                f"请检查 {provider_str} 的API配置"
            )
            return

        # 更新UI状态
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_label.config(text="正在翻译...")

        # 启动翻译线程
        self.translation_thread = threading.Thread(
            target=self.translation_worker,
            args=(provider_str, target_lang, output_format, bilingual, extract_all),
            daemon=True
        )
        self.translation_thread.start()

    def translation_worker(self, provider_str: str, target_lang: str,
                          output_format: str, bilingual: bool, extract_all: bool):
        """翻译工作线程"""
        try:
            total_files = len(self.selected_files)

            for i, file_path in enumerate(self.selected_files):
                if hasattr(self, '_stop_translation') and self._stop_translation:
                    break

                # 更新进度
                progress = (i / total_files) * 100
                self.root.after(0, lambda p=progress: self.update_progress(p, f"处理文件 {i+1}/{total_files}"))

                # 处理单个文件
                self.process_single_file(file_path, provider_str, target_lang, output_format, bilingual, extract_all)

            # 完成
            self.root.after(0, lambda: self.translation_completed())

        except Exception as e:
            error_msg = f"翻译过程中发生错误: {e}"
            logger.error(error_msg)
            self.root.after(0, lambda: self.translation_error(error_msg))

    def process_single_file(self, file_path: Path, provider_str: str, target_lang: str,
                           output_format: str, bilingual: bool, extract_all: bool):
        """处理单个文件"""
        try:
            logger.info(f"开始处理文件: {file_path.name}")

            # 获取视频信息
            video_info = self.video_processor.get_video_info(file_path)

            if not video_info.subtitle_streams:
                logger.warning(f"文件 {file_path.name} 没有字幕轨道")
                return

            # 提取字幕
            if extract_all:
                # 提取所有字幕轨道
                extracted_subtitles = self.video_processor.extract_all_subtitles(
                    file_path, output_format='srt'
                )
            else:
                # 提取第一个字幕轨道
                subtitle_path = self.video_processor.extract_subtitle(
                    file_path, subtitle_index=video_info.subtitle_streams[0].index
                )
                extracted_subtitles = {0: subtitle_path} if subtitle_path else {}

            # 翻译每个字幕文件
            for subtitle_index, subtitle_path in extracted_subtitles.items():
                if subtitle_path and subtitle_path.exists():
                    self.translate_subtitle_file(
                        subtitle_path, file_path, provider_str, target_lang,
                        output_format, bilingual
                    )

        except Exception as e:
            logger.error(f"处理文件 {file_path.name} 失败: {e}")

    def translate_subtitle_file(self, subtitle_path: Path, video_path: Path,
                               provider_str: str, target_lang: str,
                               output_format: str, bilingual: bool):
        """翻译字幕文件"""
        try:
            # 加载字幕
            subtitle_file = self.subtitle_extractor.load_subtitle_file(subtitle_path)

            # 创建异步事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # 执行翻译
                provider = TranslationProvider(provider_str)
                translated_file = loop.run_until_complete(
                    self.translation_manager.translate_subtitle_file(
                        subtitle_file,
                        target_lang,
                        provider,
                        progress_callback=self.translation_progress_callback
                    )
                )

                # 保存翻译结果
                output_filename = self.subtitle_writer.get_output_filename(
                    video_path.name, target_lang, output_format, bilingual
                )
                output_path = video_path.parent / output_filename

                self.subtitle_writer.write_subtitle_file(
                    translated_file,
                    output_path,
                    output_format,
                    bilingual
                )

                logger.info(f"翻译完成: {output_path}")

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"翻译字幕文件失败: {e}")

    def translation_progress_callback(self, current: int, total: int, progress: float):
        """翻译进度回调"""
        detail = f"翻译进度: {current}/{total} ({progress:.1f}%)"
        self.root.after(0, lambda: self.update_progress(progress, detail))

    def stop_translation(self):
        """停止翻译"""
        self._stop_translation = True
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_label.config(text="已取消")
        logger.info("翻译已取消")

    def translation_completed(self):
        """翻译完成"""
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set(100)
        self.progress_label.config(text="翻译完成")

        messagebox.showinfo("完成", "所有文件翻译完成！")
        logger.info("翻译任务完成")

    def translation_error(self, error_msg: str):
        """翻译错误"""
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_label.config(text="发生错误")

        messagebox.showerror("错误", error_msg)

    def update_progress(self, progress: float, detail: str = ""):
        """更新进度"""
        self.progress_var.set(progress)
        if detail:
            self.progress_label.config(text=detail)

    def show_settings(self):
        """显示设置对话框"""
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()

        # 居中显示
        settings_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))

        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 翻译设置标签页
        trans_frame = ttk.Frame(notebook)
        notebook.add(trans_frame, text="翻译设置")

        # API密钥设置
        api_frame = ttk.LabelFrame(trans_frame, text="API密钥配置", padding="10")
        api_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(api_frame, text="请在.env文件中配置API密钥").pack(anchor="w")

        # 输出设置
        output_frame = ttk.LabelFrame(trans_frame, text="输出设置", padding="10")
        output_frame.pack(fill="x", pady=(0, 10))

        # 输出目录
        ttk.Label(output_frame, text="默认输出目录:").pack(anchor="w")
        output_dir_var = tk.StringVar(value=self.config.get('output.default_dir', './output'))
        ttk.Entry(output_frame, textvariable=output_dir_var, width=50).pack(fill="x", pady=(5, 10))

        # 文件名模板
        ttk.Label(output_frame, text="文件名模板:").pack(anchor="w")
        template_var = tk.StringVar(value=self.config.get('output.filename_template', '{original_name}_{lang}_{format}'))
        ttk.Entry(output_frame, textvariable=template_var, width=50).pack(fill="x", pady=5)

        # 界面设置标签页
        ui_frame = ttk.Frame(notebook)
        notebook.add(ui_frame, text="界面设置")

        # 主题选择
        theme_frame = ttk.LabelFrame(ui_frame, text="主题设置", padding="10")
        theme_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(theme_frame, text="主题:").pack(anchor="w")
        theme_var = tk.StringVar(value=self.config.get('ui.theme', 'arc'))
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, state="readonly")

        # 获取可用主题
        try:
            from ttkthemes import themed_tk
            available_themes = themed_tk.ThemedTk().get_themes()
            theme_combo['values'] = sorted(available_themes)
        except:
            theme_combo['values'] = ['arc', 'equilux', 'adapta']

        theme_combo.pack(fill="x", pady=5)

        # 语言设置
        ttk.Label(theme_frame, text="界面语言:").pack(anchor="w", pady=(10, 0))
        lang_var = tk.StringVar(value=self.config.get('ui.language', 'zh_CN'))
        lang_combo = ttk.Combobox(lang_var, textvariable=lang_var, state="readonly")
        lang_combo['values'] = ['zh_CN', 'en_US']
        lang_combo.pack(fill="x", pady=5)

        # 按钮区域
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill="x", padx=10, pady=10)

        def save_settings():
            """保存设置"""
            self.config.set('output.default_dir', output_dir_var.get())
            self.config.set('output.filename_template', template_var.get())
            self.config.set('ui.theme', theme_var.get())
            self.config.set('ui.language', lang_var.get())

            messagebox.showinfo("设置", "设置已保存，重启应用后生效")
            settings_window.destroy()

        def reset_settings():
            """重置设置"""
            if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
                self.config.reset_to_defaults()
                messagebox.showinfo("设置", "设置已重置")
                settings_window.destroy()

        ttk.Button(button_frame, text="保存", command=save_settings).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="重置", command=reset_settings).pack(side="right")
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side="right", padx=(0, 5))

    def clear_logs(self):
        """清除日志"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        logger.info("日志已清除")

    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()

        # 居中显示
        about_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 150,
            self.root.winfo_rooty() + 150
        ))

        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill="both", expand=True)

        # 应用信息
        info_text = """视频翻译器 (Video Translator)
版本: 1.0.0

一个功能强大的视频字幕提取和翻译工具，
支持批量处理视频文件，利用AI平台进行高质量翻译。

主要功能:
• 支持多种视频格式
• 智能字幕提取
• AI翻译集成
• 多种输出格式
• 批量处理

支持的AI平台:
• OpenAI GPT
• Anthropic Claude
• Google Translate
• Azure Translator

开发者: Video Translator Team
许可证: MIT License
"""

        info_label = ttk.Label(main_frame, text=info_text, justify="left")
        info_label.pack(pady=(0, 20))

        # 系统信息
        system_info = get_system_info()
        sys_text = f"""系统信息:
操作系统: {system_info.get('platform', 'Unknown')}
Python版本: {system_info.get('python_version', 'Unknown')}
CPU核心数: {system_info.get('cpu_count', 'Unknown')}
内存: {format_file_size(system_info.get('memory_total', 0))}
"""

        sys_label = ttk.Label(main_frame, text=sys_text, justify="left", font=("Arial", 8))
        sys_label.pack(pady=(0, 20))

        ttk.Button(main_frame, text="确定", command=about_window.destroy).pack()

    def on_closing(self):
        """关闭应用"""
        # 如果翻译正在进行，询问是否确定关闭
        if self.translation_thread and self.translation_thread.is_alive():
            if messagebox.askyesno("确认", "翻译正在进行中，确定要退出吗？"):
                self._stop_translation = True
                self.root.quit()
        else:
            self.root.quit()

    def run(self):
        """运行应用"""
        try:
            logger.info("视频翻译器启动")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"应用运行错误: {e}")
            messagebox.showerror("错误", f"应用运行出错: {e}")
        finally:
            logger.info("视频翻译器关闭")


def main():
    """主函数"""
    try:
        # 初始化日志系统
        config = get_config()
        init_logger(config.get('logging', {}))

        # 创建并运行应用
        app = VideoTranslatorGUI()
        app.run()

    except Exception as e:
        print(f"启动失败: {e}")
        messagebox.showerror("启动错误", f"应用启动失败: {e}")


if __name__ == "__main__":
    main()
