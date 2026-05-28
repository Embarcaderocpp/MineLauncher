import customtkinter as ctk
from tkinter import messagebox
import threading
from .log_window import LogWindow
from ..core.manager import LauncherManager
from ..models import ModLoaderType
from ..utils import logger
from .progress_dialog import ProgressDialog   # ← важно!

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MinecraftLauncherGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Неофициальный Minecraft Launcher")
        self.geometry("1100x650")
        self.minsize(1100, 650)

        self.manager = LauncherManager()

        # Заголовок
        self.title_label = ctk.CTkLabel(self, text="Неофициальный Minecraft Launcher",
                                       font=ctk.CTkFont(size=32, weight="bold"))
        self.title_label.pack(pady=20)

        # Фрейм с инстансами
        self.instances_frame = ctk.CTkScrollableFrame(self, width=1050, height=420)
        self.instances_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Кнопки управления
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=15, padx=20, fill="x")

        self.btn_new = ctk.CTkButton(self.btn_frame, text="➕ Новый инстанс",
                                    command=self.show_create_dialog, width=220, height=45,
                                    font=ctk.CTkFont(size=16))
        self.btn_new.pack(side="left", padx=10)

        self.btn_logs = ctk.CTkButton(self.btn_frame, text="📜 Логи",
                                      command=self.show_log_window, width=140, height=45,
                                      font=ctk.CTkFont(size=16))
        self.btn_logs.pack(side="right", padx=10)

        self.btn_refresh = ctk.CTkButton(self.btn_frame, text="🔄 Обновить список",
                                        command=self.refresh_instances, width=220, height=45,
                                        font=ctk.CTkFont(size=16))
        self.btn_refresh.pack(side="left", padx=10)

        self.btn_settings = ctk.CTkButton(self.btn_frame, text="⚙ Настройки",
                                         command=self.show_settings, width=180, height=45,
                                         font=ctk.CTkFont(size=16))
        self.btn_settings.pack(side="right", padx=10)

        self.refresh_instances()

    # ==================== ОСНОВНЫЕ МЕТОДЫ ====================

    def refresh_instances(self):
        for widget in self.instances_frame.winfo_children():
            widget.destroy()

        instances = self.manager.list_instances()
        if not instances:
            ctk.CTkLabel(self.instances_frame,
                        text="Пока нет инстансов.\nНажми «Новый инстанс»",
                        font=ctk.CTkFont(size=18)).pack(pady=100)
            return

        for inst in instances:
            card = ctk.CTkFrame(self.instances_frame, height=100, corner_radius=12)
            card.pack(pady=8, padx=15, fill="x")

            name_label = ctk.CTkLabel(card, text=inst['name'],
                                     font=ctk.CTkFont(size=20, weight="bold"))
            name_label.pack(side="left", padx=20)

            info = f"{inst['version']} • {inst.get('modloader', 'vanilla').upper()}"
            info_label = ctk.CTkLabel(card, text=info, font=ctk.CTkFont(size=14))
            info_label.pack(side="left", padx=20)

            # Кнопка Play
            play_btn = ctk.CTkButton(card, text="▶ PLAY", width=130, height=50,
                                    font=ctk.CTkFont(size=18, weight="bold"),
                                    command=lambda n=inst['name']: self.launch_instance(n))
            play_btn.pack(side="right", padx=8)

            # Кнопка Удалить
            delete_btn = ctk.CTkButton(card, text="🗑", width=50, height=50,
                                      fg_color="#d32f2f", hover_color="#b71c1c",
                                      command=lambda n=inst['name']: self.delete_instance(n))
            delete_btn.pack(side="right", padx=8)

    def launch_instance(self, name: str):
        try:
            self.manager.launch(name)
            messagebox.showinfo("Запуск", f"✅ {name} запущен!")
        except Exception as e:
            logger.error(f"Ошибка запуска {name}: {e}")
            messagebox.showerror("Ошибка запуска", str(e))

    def delete_instance(self, name: str):
        if messagebox.askyesno("Подтверждение", f"Удалить инстанс '{name}' полностью?\n\nЭто действие нельзя отменить."):
            try:
                self.manager.delete_instance(name)
                messagebox.showinfo("Успех", f"Инстанс '{name}' удалён")
                self.refresh_instances()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    # ==================== НАСТРОЙКИ ====================

    def show_settings(self):
        current = self.manager.settings.last_instance
        try:
            instance = self.manager.get_instance_info(current)
        except (FileNotFoundError, ValueError, KeyError):
            instance = None

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Настройки — {current}")
        dialog.geometry("500x400")
        dialog.grab_set()
        dialog.transient(self)
        dialog.lift()

        ctk.CTkLabel(dialog, text="RAM (МБ)", font=ctk.CTkFont(size=16)).pack(pady=(20,5))
        ram_entry = ctk.CTkEntry(dialog, width=300)
        ram_entry.pack(pady=5)
        ram_entry.insert(0, str(instance.ram_mb) if instance else "4096")

        ctk.CTkLabel(dialog, text="JVM Args (через запятую)", font=ctk.CTkFont(size=16)).pack(pady=(15,5))
        jvm_entry = ctk.CTkEntry(dialog, width=300)
        jvm_entry.pack(pady=5)
        jvm_entry.insert(0, ",".join(instance.jvm_args) if instance and instance.jvm_args else "-XX:+UseG1GC")

        def save():
            try:
                ram = int(ram_entry.get())
                jvm = [x.strip() for x in jvm_entry.get().split(",") if x.strip()]
                self.manager.update_instance_settings(current, ram_mb=ram, jvm_args=jvm)
                messagebox.showinfo("Готово", "Настройки сохранены!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ctk.CTkButton(dialog, text="💾 Сохранить настройки", command=save, height=45).pack(pady=30)

    # ==================== СОЗДАНИЕ ИНСТАНСА С ПРОГРЕССОМ ====================

    def _install_with_progress(self, name: str, version: str, loader: ModLoaderType):
        """Установка с реальным динамическим прогрессом"""
        progress_win = ProgressDialog(self, title=f"Установка {name}")

        def update_log(msg: str):
            self.after(0, lambda: progress_win.log(msg))

        def update_progress(current: int, total: int):
            self.after(0, lambda: progress_win.update_progress(current, total))

        try:
            update_log(f"🚀 Начинаем установку {loader.value} {version}...")

            # Передаём callback прогресса в установщик
            self.manager.create_instance(
                name, version, modloader=loader,
                progress_callback=update_progress  # ← новый параметр
            )

            progress_win.finish(True, f"Инстанс '{name}' успешно создан!")
            self.after(0, self.refresh_instances)
        except Exception as e:
            progress_win.finish(False, str(e))

    def show_log_window(self):
        if not hasattr(self, 'log_window') or not self.log_window.winfo_exists():
            self.log_window = LogWindow(self)
        else:
            self.log_window.lift()

    def show_create_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Создать новый инстанс")
        dialog.geometry("420x380")
        dialog.grab_set()
        dialog.transient(self)
        dialog.lift()

        ctk.CTkLabel(dialog, text="Имя инстанса", font=ctk.CTkFont(size=14)).pack(pady=(20,5))
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack(pady=5)
        name_entry.insert(0, "my-world")

        ctk.CTkLabel(dialog, text="Версия Minecraft", font=ctk.CTkFont(size=14)).pack(pady=(15,5))
        version_entry = ctk.CTkEntry(dialog, width=300)
        version_entry.pack(pady=5)
        version_entry.insert(0, "1.21.5")

        loader_var = ctk.StringVar(value="vanilla")
        ctk.CTkLabel(dialog, text="Модлоадер", font=ctk.CTkFont(size=14)).pack(pady=(15,5))
        ctk.CTkOptionMenu(dialog, values=["vanilla", "fabric", "quilt", "forge", "neoforge"],
                         variable=loader_var, width=300).pack(pady=5)

        def create():
            name = name_entry.get().strip()
            version = version_entry.get().strip()
            loader = ModLoaderType(loader_var.get())

            if not name:
                messagebox.showwarning("Ошибка", "Имя инстанса обязательно!")
                return

            dialog.destroy()

            # Запуск в отдельном потоке
            thread = threading.Thread(
                target=self._install_with_progress,
                args=(name, version, loader),
                daemon=True
            )
            thread.start()

        ctk.CTkButton(dialog, text="Создать инстанс", command=create,
                     height=45, font=ctk.CTkFont(size=16)).pack(pady=30)


if __name__ == "__main__":
    app = MinecraftLauncherGUI()
    app.mainloop()
