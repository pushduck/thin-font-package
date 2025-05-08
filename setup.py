import PyInstaller.__main__

PyInstaller.__main__.run([
    'app.py',
    '--name=字体包处理工具',
    '--windowed',
    '--onefile',
    '--icon=font.ico',
    '--add-data=font.ico;.'
])