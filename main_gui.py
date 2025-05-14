import customtkinter as ctk
from tkinter import messagebox 
from tkinter import filedialog

import os

from main import run_generate_exo

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class LRC2EXOApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # タイトル設定
        self.title("LRC2EXO-Python")

        # GUI要素の設定
        self.font = ("メイリオ", 12)
        self.create_widgets()
        self.eval('tk::PlaceWindow . center')
        self.resizable(False, False)
        

    def create_widgets(self):
        # 入力歌詞ファイル
        self.label_lyrics = ctk.CTkLabel(self, text="入力歌詞ファイル", font=self.font)
        self.label_lyrics.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.entry_lyrics = ctk.CTkEntry(self, width=300, font=self.font)
        self.entry_lyrics.grid(row=0, column=1, padx=10, pady=10)
        
        self.button_lyrics = ctk.CTkButton(self, text="...", command=self.select_lyrics_file, width=50, font=self.font)
        self.button_lyrics.grid(row=0, column=2, padx=10, pady=10)
        
        # 設定ファイル
        self.label_settings = ctk.CTkLabel(self, text="設定ファイル", font=self.font)
        self.label_settings.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        self.entry_settings = ctk.CTkEntry(self, width=300, font=self.font)
        self.entry_settings.grid(row=1, column=1, padx=10, pady=10)
        
        self.button_settings = ctk.CTkButton(self, text="...", command=self.select_settings_file, width=50, font=self.font)
        self.button_settings.grid(row=1, column=2, padx=10, pady=10)
        
        # EXO出力先
        self.label_output = ctk.CTkLabel(self, text="EXO出力先", font=self.font)
        self.label_output.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        self.entry_output = ctk.CTkEntry(self, width=300, font=self.font)
        self.entry_output.grid(row=2, column=1, padx=10, pady=10)
        
        self.button_output = ctk.CTkButton(self, text="...", command=self.select_output_file, width=50, font=self.font)
        self.button_output.grid(row=2, column=2, padx=10, pady=10)

        # 処理開始ボタン
        self.button_process = ctk.CTkButton(self, text="処理開始", command=self.start_processing, width=200, font=self.font)
        self.button_process.grid(row=3, column=1, padx=10, pady=20)

    # ファイル選択ダイアログを開き、選択したファイルパスをエントリーに表示
    def select_lyrics_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("タイムタグ付き歌詞ファイル", "*.lrc;*.kra")])
        if file_path:
            self.entry_lyrics.delete(0, ctk.END)
            self.entry_lyrics.insert(0, file_path)

    def select_settings_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("設定ファイル", "*.json")])
        if file_path:
            self.entry_settings.delete(0, ctk.END)
            self.entry_settings.insert(0, file_path)

    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("EXOファイル", "*.exo")])
        if file_path:
            file_path = file_path if file_path.endswith(".exo") else f"{file_path}.exo"
            self.entry_output.delete(0, ctk.END)
            self.entry_output.insert(0, file_path)

    # 処理開始ボタンを押したときの処理
    def start_processing(self):
        lyrics_path = self.entry_lyrics.get()
        settings_path = self.entry_settings.get()
        output_path = self.entry_output.get()
        
        if all([lyrics_path, settings_path, output_path]):
            if messagebox.askyesno("確認", "処理を開始してもよろしいですか？"):
                try:
                    run_generate_exo(
                        input_lrc_path=lyrics_path,
                        settings_path=settings_path,
                        exo_output_path=output_path
                    )
                    messagebox.showinfo("情報", f"生成が完了しました")
                
                except Exception as e:
                    messagebox.showerror("エラー", f"エラーが発生しました：{e}")
        
        else:
            messagebox.showwarning("警告", "すべてのファイルパスを指定してください")


if __name__ == "__main__":
    app = LRC2EXOApp()
    app.mainloop()
