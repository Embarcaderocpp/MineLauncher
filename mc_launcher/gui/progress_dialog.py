import customtkinter as ctk
from tkinter import messagebox

class ProgressDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Установка инстанса"):
        super().__init__(parent)
        self.title(title)
        self.geometry("640x480")
        self.grab_set()
        self.transient(parent)
        self.lift()

        # Заголовок
        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=15)

        # Прогресс-бар
        self.progress = ctk.CTkProgressBar(self, width=580, height=20)
        self.progress.pack(pady=10, padx=30)
        self.progress.set(0)

        # Текст процента
        self.percent_label = ctk.CTkLabel(self, text="0%", font=ctk.CTkFont(size=16))
        self.percent_label.pack(pady=(0, 10))

        # Лог
        self.log_text = ctk.CTkTextbox(self, width=600, height=260)
        self.log_text.pack(pady=10, padx=20)
        self.log_text.insert("0.0", "🚀 Начало установки...\n")
        self.log_text.configure(state="disabled")

    def update_progress(self, current: int, total: int):
        """Обновление прогресс-бара и процентов"""
        if total > 0:
            percent = current / total
            self.progress.set(percent)
            self.percent_label.configure(text=f"{int(percent * 100)}%")
        else:
            self.progress.set(0.5)  # анимация, если total неизвестен

    def log(self, message: str):
        """Добавление строки в лог"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def finish(self, success: bool, message: str):
        """Завершение окна"""
        self.log("✅ " + message if success else "❌ " + message)
        if success:
            messagebox.showinfo("Готово", message)
        else:
            messagebox.showerror("Ошибка", message)
        self.destroy()