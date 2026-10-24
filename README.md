# Memo 自动连点器

Windows 10 / 11 桌面自动连点器。使用 Python 自带的 Tkinter 界面和 Windows SendInput，无需第三方运行依赖。

## 第一次运行（Windows）

1. 从 https://www.python.org/downloads/windows/ 安装 Python 3.10 或更新版本，保留安装选项中的 Tcl/Tk 和 Python Launcher。
2. 在 GitHub 仓库页面点击 **Code → Download ZIP**，下载后解压。也可以把本项目文件从 Codespace 下载到 Windows 电脑。
3. 双击 `start.bat`，打开窗口。如果显示找不到 `py`，重新安装 Python 并启用 Python Launcher。
4. 设置间隔、次数和左键/右键。次数为 `0` 表示持续点击。
5. 将鼠标移到目标位置，按 **F6** 开始；启动后有 1 秒准备时间。再次按 **F6** 暂停，按 **F8** 紧急停止。关闭窗口也会停止。

点击位置始终跟随鼠标当前所在位置。最小间隔是 10 毫秒；实际速度受 Windows 调度和目标程序影响，并非精确定时。快捷键在其他窗口获得焦点时仍有效；若已被其他程序占用，应用会提示并退出。

先在空白文档或其他无重要操作的区域试用。目标程序如果以管理员权限运行，Windows 可能拒绝点击。锁屏、受保护的桌面和部分游戏可能不接受模拟输入。

## 开发与验证

```sh
python -m unittest discover -s tests -v
```

Codespace / Linux 可以编辑代码并运行调度逻辑测试；实际窗口、全局快捷键和鼠标点击需要在 Windows 桌面验证。

Windows 手动验收：在画图的空白画布上设置 500 毫秒、3 次，鼠标移到画布后按 F6，确认完成后计数为 3；设为不限次数，再验证 F6、F8 和关闭窗口都能停止。分别检查左右键，并检查间隔小于 10、负次数及非数字输入均会被拒绝。

可选：在 Windows 上生成独立 EXE（需要联网安装打包工具）：

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install pyinstaller
.venv\Scripts\python -m PyInstaller --onefile --windowed --name Memo clicker.py
```

生成文件为 `dist\Memo.exe`。须在 Windows 上打包，不能在 Linux Codespace 中直接生成 Windows EXE。
