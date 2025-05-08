import os
import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QFileDialog, QComboBox, 
                            QTextEdit, QProgressBar, QMessageBox, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

class FontConverterThread(QThread):
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    completed = pyqtSignal(bool, str)

    """
    input_font_path: 字体源文件路径
    url_text: 常用字列表URL
    custom_text: 自定义字符
    output_format: 输出格式,默认不转换
    output_path: 输出路径,默认源文件同级目录
    """
    
    def __init__(self, input_font_path, url_text, custom_text, output_format, output_path):
        super().__init__()
        self.input_font_path = input_font_path
        self.url_text = url_text
        self.custom_text = custom_text
        self.output_format = output_format
        self.output_path = output_path
        
    def run(self):
        try:
            self.status_update.emit("加载字体文件...")
            self.progress_update.emit(10)
            
            font = TTFont(self.input_font_path)
            self.progress_update.emit(20)
            
            url_content = ""
            if self.url_text:
                self.status_update.emit("从URL下载字符...")
                try:
                    response = requests.get(self.url_text, timeout=10)
                    response.raise_for_status()
                    url_content = response.text
                    self.status_update.emit(f"从URL下载了 {len(url_content)} 个字符")
                except Exception as e:
                    self.status_update.emit(f"从URL下载失败: {str(e)}")
            self.progress_update.emit(40)
            
            final_text = url_content + self.custom_text
            if not final_text:
                self.status_update.emit("警告: 没有提供字符用于子集化")
                final_text = None
            else:
                self.status_update.emit(f"使用 {len(final_text)} 个字符进行子集化")
            
            self.progress_update.emit(50)
            options = Options()
            subsetter = Subsetter(options=options)
            
            if final_text:
                subsetter.populate(text=final_text)
                subsetter.subset(font)
            self.progress_update.emit(70)
        
            extension_map = {
                "TTF": ".ttf",
                "OTF": ".otf",
                "WOFF": ".woff"
                # "WOFF2": ".woff2"
            }

            if self.output_format != "":
                if not self.output_path.lower().endswith(extension_map[self.output_format].lower()):
                    file_base = os.path.splitext(self.output_path)[0]
                    self.output_path = file_base + extension_map[self.output_format]
            
                self.status_update.emit(f"转换为 {self.output_format} 格式...")
                if self.output_format == "WOFF2":
                    print("WOFF2 not supported")
                
            self.status_update.emit(f"保存字体到 {self.output_path}...")
            font.save(self.output_path)
            self.progress_update.emit(100)
            
            self.completed.emit(True, self.output_path)
            
        except Exception as e:
            self.status_update.emit(f"错误: {str(e)}")
            self.completed.emit(False, str(e))

class FontConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("字体包处理工具")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        input_group = QGroupBox("选择文件")
        input_layout = QHBoxLayout()
        self.input_font_label = QLabel("未选择")
        self.browse_button = QPushButton("选择文件")
        self.browse_button.clicked.connect(self.browse_font)
        input_layout.addWidget(QLabel("字体源文件:"))
        input_layout.addWidget(self.input_font_label, 1)
        input_layout.addWidget(self.browse_button)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        chars_group = QGroupBox("筛选字符")
        chars_layout = QVBoxLayout()
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("常用字列表(3500常用字):"))
        self.url_input = QLineEdit()
        default_url = "https://raw.githubusercontent.com/shinchanZ/-3500-/master/3500"
        self.url_input.setPlaceholderText(f"输入一个远程URL，例如{default_url}")
        self.url_input.setText(default_url)
        url_layout.addWidget(self.url_input)
        chars_layout.addLayout(url_layout)
        
        chars_layout.addWidget(QLabel("追加自定义字符:"))
        self.custom_chars = QTextEdit()
        example_chars = "犇骉淼焱"
        self.custom_chars.setPlaceholderText(f"添加你的自定义字符, 例如: {example_chars}")
        # self.custom_chars.setMaximumHeight(100)
        chars_layout.addWidget(self.custom_chars)
        chars_group.setLayout(chars_layout)
        main_layout.addWidget(chars_group)
        
        output_group = QGroupBox("输出选项")
        output_layout = QVBoxLayout()
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["不转换", "TTF", "OTF", "WOFF"])
        format_layout.addWidget(self.format_combo)
        output_layout.addLayout(format_layout)
        
        output_file_layout = QHBoxLayout()
        self.output_path_label = QLabel("未设置")
        self.output_browse_button = QPushButton("保存为...")
        self.output_browse_button.clicked.connect(self.browse_output)
        output_file_layout.addWidget(QLabel("输出文件:"))
        output_file_layout.addWidget(self.output_path_label, 1)
        output_file_layout.addWidget(self.output_browse_button)
        output_layout.addLayout(output_file_layout)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        status_group = QGroupBox("状态")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("准备就绪")
        self.progress_bar = QProgressBar()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        self.convert_button = QPushButton("开始处理")
        self.convert_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.convert_button.clicked.connect(self.start_conversion)
        main_layout.addWidget(self.convert_button)
    
        self.input_font_path = ""
        self.output_path = ""
        self.converter_thread = None
        
    def browse_font(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "选择字体文件", "", "字体文件 (*.ttf *.otf *.woff *.woff2)"
        )
        if file_path:
            self.input_font_path = file_path
            self.input_font_label.setText(os.path.basename(file_path))
            
            name_split = os.path.splitext(file_path)
            file_base = name_split[0]
            file_original_ext = name_split[1].split(".")[1]
            output_ext = self.format_combo.currentText().lower()
            if output_ext == "不转换":
                output_ext = file_original_ext
            if output_ext == "woff2":
                suggested_output = f"{file_base}-subset.woff2"
            else:
                suggested_output = f"{file_base}-subset.{output_ext}"
            self.output_path = suggested_output
            self.output_path_label.setText(os.path.basename(suggested_output))
    
    def browse_output(self):
        format_ext = self.format_combo.currentText().lower()
        file_filter = f"Font Files (*.{format_ext})"
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "保存字体文件", "", file_filter
        )
        if file_path:
            if not file_path.lower().endswith(f".{format_ext}"):
                file_path = f"{file_path}.{format_ext}"
            
            self.output_path = file_path
            self.output_path_label.setText(os.path.basename(file_path))
    
    def start_conversion(self):
        if not self.input_font_path:
            QMessageBox.warning(self, "提示", "请选择一个字体源文件。")
            return
            
        if not self.output_path:
            QMessageBox.warning(self, "提示", "请选择一个输出位置。")
            return
        
        self.progress_bar.setValue(0)
        self.status_label.setText("开始处理...")
        self.convert_button.setEnabled(False)
        
        url_text = self.url_input.text().strip()
        custom_text = self.custom_chars.toPlainText()
        user_output_format = self.format_combo.currentText()
        if user_output_format == "不转换":
            output_format = ""
        else:
            output_format = user_output_format

        self.converter_thread = FontConverterThread(
            self.input_font_path, 
            url_text, 
            custom_text,
            output_format,
            self.output_path
        )
    
        self.converter_thread.progress_update.connect(self.update_progress)
        self.converter_thread.status_update.connect(self.update_status)
        self.converter_thread.completed.connect(self.conversion_completed)
        
        self.converter_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def conversion_completed(self, success, message):
        self.convert_button.setEnabled(True)
        
        if success:
            QMessageBox.information(
                self, 
                "成功", 
                f"字体处理完成!\n输出保存到: {message}"
            )
        else:
            QMessageBox.critical(
                self,
                "错误",
                f"字体处理失败: {message}"
            )

def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('font.ico')))
    window = FontConverterApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()