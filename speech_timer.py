import os
import sys
import ctypes
import tkinter as tk
from tkinter import messagebox
import winsound


def resource_path(relative_path):
    """通常実行時・PyInstaller実行時のリソースパス"""
    base_path = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.abspath(__file__))
    )
    return os.path.join(base_path, relative_path)




class SpeechTimerApp:

    def __init__(self, root):
        self.root = root

        # --- タイトルとサイズ設定 ---
        APP_VERSION = "v2.0"
        self.root.title(f"スピーチタイマー   {APP_VERSION}")
        self.root.geometry("360x300")
        self.root.resizable(False, False)

        # --- リソースファイルパスの決定 ---

        self.ico_path = resource_path("bell.png")
        self.wav_path = resource_path("bell.wav")

        # --- アイコン設定 ---

        if os.path.exists(self.ico_path):
            try:
                self.icon_image = tk.PhotoImage(file=self.ico_path)
                self.root.iconphoto(True, self.icon_image)
            except Exception as e:
                print(f"iconbitmap error: {e}")

        # タイマー変数設定 (初期設定値: 3分 = 180秒)
        self.default_seconds = 180
        self.remaining_seconds = self.default_seconds
        self.is_running = False
        self.timer_id = None

        # --- 1. タイマー大文字入力・表示エリア ---
        self.time_entry = tk.Entry(
            self.root,
            font=("Helvetica", 64, "bold"),
            fg="#333333",
            disabledforeground="#333333",
            justify="center",
            bd=0,
            highlightthickness=0,
            width=6,
        )
        self.time_entry.pack(pady=(20, 10))
        self.set_entry_text(self.format_time(self.remaining_seconds))

        # --- 2. 操作ボタンエリア ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(
            btn_frame,
            text="スタート",
            font=("Helvetica", 12, "bold"),
            width=8,
            bg="#4CAF50",
            fg="white",
            command=self.start_timer,
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(
            btn_frame,
            text="一時停止",
            font=("Helvetica", 12),
            width=8,
            state=tk.DISABLED,
            command=self.stop_timer,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = tk.Button(
            btn_frame,
            text="リセット",
            font=("Helvetica", 12),
            width=8,
            command=self.reset_timer,
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # --- 3. 手動ベル鳴らしボタン（司会者用） ---
        test_frame = tk.Frame(self.root)
        test_frame.pack(pady=(15, 0))

        self.test_sound_btn = tk.Button(
            test_frame,
            text="🔔 手動ベル",
            font=("Helvetica", 10, "bold"),
            command=self.play_bell,
        )
        self.test_sound_btn.pack()

    def set_entry_text(self, text_str):
        """入力フォームのテキスト書き換え"""
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, text_str)

    def parse_entry_time(self):
        """入力テキスト（"03:00" や "180" など）を秒数に変換"""
        raw_text = self.time_entry.get().strip()
        if ":" in raw_text:
            parts = raw_text.split(":")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return int(parts[0]) * 60 + int(parts[1])
        elif raw_text.isdigit():
            return int(raw_text)
        return None

    def format_time(self, seconds):
        """秒数を MM:SS または -MM:SS 文字列に変換"""
        abs_seconds = abs(seconds)
        m, s = divmod(abs_seconds, 60)
        return f"{m:02d}:{s:02d}" if seconds >= 0 else f"-{m:02d}:{s:02d}"

    def update_colors(self):
        """残り時間に応じて文字色を変更"""
        if 0 < self.remaining_seconds <= 30:
            color = "#E65100"  # 警告（オレンジ）
        elif self.remaining_seconds <= 0:
            color = "#D32F2F"  # 超過（赤）
        else:
            color = "#333333"  # 通常（黒）

        self.time_entry.config(fg=color, disabledforeground=color)

    def update_timer(self):
        """1秒ごとに実行されるメインロジック"""
        if self.is_running:
            self.remaining_seconds -= 1

            self.time_entry.config(state=tk.NORMAL)
            self.set_entry_text(self.format_time(self.remaining_seconds))
            self.update_colors()
            self.time_entry.config(state=tk.DISABLED)

            if self.remaining_seconds == 0:
                self.play_bell()

            self.timer_id = self.root.after(1000, self.update_timer)

    def start_timer(self):
        """タイマー開始"""
        if not self.is_running:
            seconds = self.parse_entry_time()
            if seconds is None or seconds <= 0:
                messagebox.showerror(
                    "入力エラー",
                    "正しい時間を入力してください。\n例: 03:00 や 5:00",
                )
                return

            if not os.path.exists(self.wav_path):
                messagebox.showwarning(
                    "警告",
                    f"「bell.wav」が見つかりません。\n探索パス:\n{self.wav_path}",
                )
                return

            self.default_seconds = seconds
            self.remaining_seconds = seconds

            self.set_entry_text(self.format_time(self.remaining_seconds))
            self.update_colors()
            self.time_entry.config(state=tk.DISABLED)

            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            self.timer_id = self.root.after(1000, self.update_timer)

    def stop_timer(self):
        """一時停止"""
        if self.is_running:
            self.is_running = False
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def reset_timer(self):
        """リセット"""
        self.stop_timer()
        self.remaining_seconds = self.default_seconds

        self.time_entry.config(state=tk.NORMAL)
        self.update_colors()
        self.set_entry_text(self.format_time(self.remaining_seconds))

    def play_bell(self):
        """WAV音源を非同期再生"""
        if os.path.exists(self.wav_path):
            try:
                winsound.PlaySound(
                    self.wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC
                )
            except Exception as e:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                messagebox.showerror(
                    "再生エラー",
                    f"bell.wav の再生に失敗しました。\n詳細: {e}",
                )
        else:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            messagebox.showwarning(
                "ファイル未検出",
                f"音源が見つかりません:\n{self.wav_path}",
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechTimerApp(root)
    root.mainloop()