import tkinter as tk
from ttkbootstrap import Style
from tkinter import messagebox
from ttkbootstrap.widgets import Entry, Button, Label
from PIL import Image, ImageTk
import requests
import io
import pyperclip
import re
import threading

class DriveImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Drive URL 変換ツール")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # Bootstrapスタイル適用
        style = Style("cyborg")  # dark系なら "cyborg", "darkly", 明るいのがいいなら "flatly" など

        # ---------- メインフレーム ----------
        self.main_frame = tk.Frame(root, bg=style.colors.bg)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ---------- 入力欄 ----------
        self.input_url = tk.StringVar()
        self.output_url = tk.StringVar()

        self.input_entry = Entry(self.main_frame, textvariable=self.input_url, width=50)
        self.input_entry.grid(row=0, column=0, padx=10, pady=10)

        paste_btn = Button(self.main_frame, text="paste", bootstyle="info", command=self.paste_url)
        paste_btn.grid(row=0, column=1, padx=5)

        # ---------- 出力欄 ----------
        self.output_entry = Entry(self.main_frame, textvariable=self.output_url, width=50)
        self.output_entry.grid(row=1, column=0, padx=10, pady=10)

        copy_btn = Button(self.main_frame, text="copy", bootstyle="info", command=self.copy_url)
        copy_btn.grid(row=1, column=1, padx=5)

        # ---------- プレビュー切り替え ----------
        self.preview_btn = Button(self.main_frame, text="プレビューを表示", bootstyle="secondary", command=self.toggle_preview)
        self.preview_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # ---------- プレビュー枠 ----------
        self.preview_frame = tk.Frame(self.main_frame, bg=style.colors.secondary, width=500, height=300)
        self.preview_frame.grid(row=3, column=0, columnspan=2)
        self.preview_frame.grid_propagate(False)

        self.preview_label = Label(self.preview_frame, text="画像プレビュー", anchor="center", foreground="white")
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        self.preview_visible = False
        self.tk_image = None  # 保持用

    def paste_url(self):
        url = pyperclip.paste()
        self.input_url.set(url)
        file_id = self.extract_id(url)
        if file_id:
            direct_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            self.output_url.set(direct_url)

    def copy_url(self):
        pyperclip.copy(self.output_url.get())
        messagebox.showinfo("コピー完了", "画像URLをコピーしました")

    def extract_id(self, url):
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
        return match.group(1) if match else None

    def toggle_preview(self):
        if self.preview_visible:
            self.preview_frame.grid_remove()
            self.preview_btn.config(text="プレビューを表示")
            self.preview_visible = False
        else:
            self.preview_label.config(text="読み込み中...", image="", compound="none")
            self.preview_frame.grid()
            self.preview_btn.config(text="プレビューを非表示")
            self.preview_visible = True
            threading.Thread(target=self.load_image, daemon=True).start()

    def load_image(self):
        url = self.output_url.get()
        if not url:
            messagebox.showwarning("警告", "画像URLが空です")
            return
        try:
            response = requests.get(url, timeout=10)
            image = Image.open(io.BytesIO(response.content))
            image.thumbnail((500, 300))
            self.tk_image = ImageTk.PhotoImage(image)
            self.preview_label.config(image=self.tk_image, text="", compound="none")
        except Exception as e:
            self.preview_label.config(text="画像の読み込みに失敗しました")

# 実行
if __name__ == "__main__":
    root = tk.Tk()
    app = DriveImageApp(root)
    root.mainloop()
