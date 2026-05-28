import customtkinter as ctk
import logging
from ..utils import logger

class LogWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Логи лаунчера")
        self.geometry("900x600")
        self.transient(parent)
        self.lift()

        # Заголовок
        ctk.CTkLabel(self, text="📜 Python",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Поле с логами
        self.log_text = ctk.CTkTextbox(self, width=880, height=520)
        self.log_text.pack(pady=10, padx=10)
        self.log_text.configure(state="disabled")

        # Кнопка очистки
        ctk.CTkButton(self, text="Очистить логи", width=150,
                     command=self.clear_logs).pack(pady=5)

        # Подключаем handler для живых логов
        self.handler = GuiLogHandler(self)
        logger.addHandler(self.handler)

    def log(self, message: str):
        """Добавляем строку в окно"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def destroy(self):
        # Убираем handler при закрытии окна
        if self.handler in logger.handlers:
            logger.removeHandler(self.handler)
        super().destroy()


class GuiLogHandler(logging.Handler):
    """Handler, который отправляет логи в GUI-окно"""
    def __init__(self, log_window):
        super().__init__()
        self.log_window = log_window
        self.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    def emit(self, record):
        msg = self.format(record)
        # Выполняем в главном потоке tkinter
        self.log_window.after(0, self.log_window.log, msg)