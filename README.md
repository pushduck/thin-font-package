# 字体转换器和子集生成器

一个用于字体子集生成和格式转换的 GUI 应用程序。

## 功能

- **字体子集生成**：通过仅包含所需字符来减小字体文件大小
- **格式转换**：在字体格式之间转换（OTF, TTF, WOFF, WOFF2）
- **字符导入**：从 URL 加载字符或直接输入
- **简易 GUI 界面**：易于使用的图形界面

## 安装

### 选项 1：使用预构建的可执行文件（Windows）

1. 下载最新版本
2. 解压文件
3. 运行 `FontConverter.exe`

### 选项 2：从源码安装

1. 克隆此仓库
2. 安装依赖项：
```
pip install -r requirements.txt
```
3. 运行应用程序：
```
python font_converter_gui.py
```

## 构建可执行文件

要自己构建可执行文件：

1. 安装依赖项：
```
pip install -r requirements.txt
```

2. 运行安装脚本：
```
python setup.py build
```

3. 可执行文件将在 `build` 目录中创建

## 使用说明

1. **选择输入字体**：点击“浏览...”选择你的源字体文件
2. **选择要包含的字符**：
- 输入 URL 下载字符（可选）
- 在文本框中输入自定义字符（可选）
3. **设置输出选项**：
- 选择输出格式（TTF, OTF, WOFF, WOFF2）
- 选择保存输出文件的位置
4. **点击“转换”**来处理字体

## 要求

- Python 3.6+
- PyQt5
- fontTools
- requests
- brotli（用于 WOFF2 支持）

## 许可证

MIT 许可证