"""Memo: a Windows auto clicker with no third-party runtime dependencies."""
import sys
import time
from dataclasses import dataclass


@dataclass
class ClickSchedule:
    interval: float
    limit: int = 0
    count: int = 0
    next_at: float = 0.0
    running: bool = False

    def start(self, now):
        self.count = 0
        self.next_at = now
        self.running = True

    def stop(self):
        self.running = False

    def tick(self, now, click):
        if not self.running or now < self.next_at:
            return False
        click()
        self.count += 1
        self.next_at = now + self.interval
        if self.limit and self.count >= self.limit:
            self.stop()
        return True


def main():
    if sys.platform != 'win32':
        print('Memo 自动连点器需要 Windows 10 或 Windows 11。')
        return 1

    import ctypes
    from ctypes import wintypes
    import tkinter as tk
    from tkinter import ttk, messagebox

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    # INPUT must include the largest union member and pointer-sized extra info.
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [('dx', wintypes.LONG), ('dy', wintypes.LONG),
                    ('mouseData', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
                    ('time', wintypes.DWORD), ('dwExtraInfo', ctypes.c_size_t)]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [('wVk', wintypes.WORD), ('wScan', wintypes.WORD),
                    ('dwFlags', wintypes.DWORD), ('time', wintypes.DWORD),
                    ('dwExtraInfo', ctypes.c_size_t)]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [('uMsg', wintypes.DWORD), ('wParamL', wintypes.WORD),
                    ('wParamH', wintypes.WORD)]

    class INPUTUNION(ctypes.Union):
        _fields_ = [('mi', MOUSEINPUT), ('ki', KEYBDINPUT), ('hi', HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ('data',)
        _fields_ = [('type', wintypes.DWORD), ('data', INPUTUNION)]

    user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    user32.SendInput.restype = wintypes.UINT
    user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
    user32.RegisterHotKey.restype = wintypes.BOOL
    user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND,
                                   wintypes.UINT, wintypes.UINT, wintypes.UINT]
    user32.PeekMessageW.restype = wintypes.BOOL

    root = tk.Tk()
    root.title('Memo 自动连点器')
    root.resizable(False, False)
    frame = ttk.Frame(root, padding=24)
    frame.grid()
    interval = tk.StringVar(value='100')
    limit = tk.StringVar(value='0')
    button = tk.StringVar(value='左键')
    status = tk.StringVar(value='已停止 · F6 开始/停止 · F8 紧急停止')
    counter = tk.StringVar(value='已点击：0 次')
    schedule = ClickSchedule(0.1)
    flags = (0x0002, 0x0004)

    ttk.Label(frame, text='Memo 自动连点器', font=('Microsoft YaHei UI', 16, 'bold')).grid(
        row=0, column=0, columnspan=2, pady=(0, 16))
    controls = []
    for row, (label, variable) in enumerate([
        ('点击间隔（毫秒，至少 10）', interval), ('点击次数（0 = 不限）', limit)
    ], 1):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky='w', pady=6)
        entry = ttk.Entry(frame, textvariable=variable, width=18)
        entry.grid(row=row, column=1, padx=(16, 0))
        controls.append(entry)
    ttk.Label(frame, text='鼠标按键').grid(row=3, column=0, sticky='w', pady=6)
    choice = ttk.Combobox(frame, textvariable=button, values=['左键', '右键'],
                          state='readonly', width=16)
    choice.grid(row=3, column=1, padx=(16, 0))
    ttk.Label(frame, text='点击鼠标当前所在位置。先将鼠标移到目标，再按 F6。',
              wraplength=380).grid(row=4, column=0, columnspan=2, pady=16)

    def update_state():
        for control in controls:
            control.configure(state='disabled' if schedule.running else 'normal')
        choice.configure(state='disabled' if schedule.running else 'readonly')
        start_button.configure(text='停止（F6）' if schedule.running else '开始（F6）')
        counter.set(f'已点击：{schedule.count} 次')

    def stop():
        schedule.stop()
        status.set('已停止 · F6 开始/停止 · F8 紧急停止')
        update_state()

    def toggle():
        nonlocal flags, schedule
        if schedule.running:
            stop()
            return
        try:
            milliseconds = int(interval.get())
            times = int(limit.get())
            if milliseconds < 10 or times < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror('设置无效', '间隔须为至少 10 的整数，次数须为非负整数。')
            return
        flags = (0x0002, 0x0004) if button.get() == '左键' else (0x0008, 0x0010)
        schedule = ClickSchedule(milliseconds / 1000, times)
        # Give users time to move the pointer when starting with the button.
        schedule.start(time.monotonic() + 1)
        status.set('运行中（1 秒后开始）· F8 紧急停止')
        update_state()

    def click():
        events = (INPUT * 2)()
        for event, flag in zip(events, flags):
            event.type = 0
            event.mi.dwFlags = flag
        if user32.SendInput(2, events, ctypes.sizeof(INPUT)) != 2:
            # Release the button as a precaution if only the down event succeeded.
            release = INPUT()
            release.mi.dwFlags = flags[1]
            user32.SendInput(1, ctypes.byref(release), ctypes.sizeof(INPUT))
            raise RuntimeError('Windows 拒绝了模拟点击。目标窗口可能以管理员权限运行。')

    start_button = ttk.Button(frame, text='开始（F6）', command=toggle)
    start_button.grid(row=5, column=0, sticky='ew', padx=(0, 8))
    ttk.Button(frame, text='停止（F8）', command=stop).grid(row=5, column=1, sticky='ew')
    ttk.Label(frame, textvariable=counter).grid(row=6, column=0, columnspan=2, pady=(16, 6))
    ttk.Label(frame, textvariable=status, wraplength=380).grid(row=7, column=0, columnspan=2)

    registered = []
    for identifier, key in [(1, 0x75), (2, 0x77)]:  # F6 / F8, MOD_NOREPEAT
        if not user32.RegisterHotKey(None, identifier, 0x4000, key):
            for previous in registered:
                user32.UnregisterHotKey(None, previous)
            messagebox.showerror('快捷键不可用', 'F6 或 F8 已被其他程序占用。请关闭冲突程序后重试。')
            root.destroy()
            return 1
        registered.append(identifier)

    def poll():
        msg = wintypes.MSG()
        while user32.PeekMessageW(ctypes.byref(msg), None, 0x0312, 0x0312, 1):
            if msg.wParam == 2:
                stop()
            elif msg.wParam == 1:
                toggle()
        try:
            if schedule.tick(time.monotonic(), click):
                update_state()
                if not schedule.running:
                    status.set('已完成指定次数 · F6 可再次开始')
        except RuntimeError as error:
            stop()
            messagebox.showerror('点击失败', str(error))
        root.after(5, poll)

    def close():
        schedule.stop()
        for identifier in registered:
            user32.UnregisterHotKey(None, identifier)
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', close)
    root.after(5, poll)
    try:
        root.mainloop()
    finally:
        for identifier in registered:
            user32.UnregisterHotKey(None, identifier)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
