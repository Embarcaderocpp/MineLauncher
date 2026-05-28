from pathlib import Path
from datetime import datetime
from ..config import Settings
from ..models import Instance, ModLoaderType
from .installer import Installer
from .runner import Runner
import json
from ..utils import logger

class LauncherManager:
    def __init__(self):
        self.settings = Settings.load()
        self.instances_dir = Path(self.settings.minecraft_dir)
        self.instances_dir.mkdir(parents=True, exist_ok=True)

    def get_instance_path(self, name: str) -> Path:
        path = self.instances_dir / name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_instance(
            self,
            name: str,
            version: str,
            nickname: str = "CrackedPlayer",
            modloader: ModLoaderType = ModLoaderType.VANILLA,
            loader_version: str = None,
            progress_callback=None  # ← добавлено
    ) -> Instance:
        """Создаёт новый инстанс"""
        instance_path = self.get_instance_path(name)

        instance = Instance(
            name=name,
            version=version,
            modloader=modloader,
            modloader_version=loader_version,
            nickname=nickname,
            jvm_args=[],
            ram_mb=4096
        )

        json_path = instance_path / "instance.json"
        json_path.write_text(instance.model_dump_json(indent=2), encoding="utf-8")

        # Установка с поддержкой прогресса
        if modloader == ModLoaderType.VANILLA:
            Installer.install_vanilla(version, str(instance_path), progress_callback=progress_callback)
        else:
            installed_version = Installer.install_modloader(
                modloader=modloader,
                minecraft_version=version,
                instance_path=str(instance_path),
                loader_version=loader_version,
                java_path=self.settings.java_path,
                progress_callback=progress_callback  # ← передаём
            )
            instance.version = installed_version
            json_path.write_text(instance.model_dump_json(indent=2), encoding="utf-8")

        self.settings.last_instance = name
        self.settings.save()
        return instance

    def launch(self, name: str = None):
        """Запускает инстанс (по умолчанию — последний)"""
        if name is None:
            name = self.settings.last_instance

        instance_path = self.get_instance_path(name)
        json_path = instance_path / "instance.json"

        if not json_path.exists():
            raise FileNotFoundError(f"Инстанс '{name}' не найден!")

        instance = Instance.model_validate_json(json_path.read_text(encoding="utf-8"))

        Runner.run(
            instance_path=str(instance_path),
            version=instance.version,
            nickname=instance.nickname,
            java_path=self.settings.java_path,
            jvm_args=instance.jvm_args,
            ram_mb=instance.ram_mb
        )

        instance.last_played = datetime.now()
        json_path.write_text(instance.model_dump_json(indent=2), encoding="utf-8")

        self.settings.last_instance = name
        self.settings.save()

    def list_instances(self):
        """Возвращает список всех инстансов"""
        instances = []
        for folder in self.instances_dir.iterdir():
            if folder.is_dir() and (folder / "instance.json").exists():
                try:
                    data = json.loads((folder / "instance.json").read_text(encoding="utf-8"))
                    instances.append(data)
                except (json.JSONDecodeError, OSError, KeyError, TypeError):
                    pass  # пропускаем повреждённые инстансы
        return instances

    def delete_instance(self, name: str):
        """Удаляет инстанс"""
        path = self.get_instance_path(name)
        if path.exists():
            import shutil
            shutil.rmtree(path)
            logger.info(f"🗑️ Инстанс '{name}' полностью удалён")
            if self.settings.last_instance == name:
                self.settings.last_instance = "default"
                self.settings.save()

    def get_instance_info(self, name: str):
        """Информация об инстансе"""
        json_path = self.get_instance_path(name) / "instance.json"
        if not json_path.exists():
            raise FileNotFoundError(f"Инстанс '{name}' не найден!")
        return Instance.model_validate_json(json_path.read_text(encoding="utf-8"))

    def list_available_versions(self):
        """Список всех доступных версий Minecraft"""
        from minecraft_launcher_lib.utils import get_version_list
        return get_version_list()

    def install_modloader_to_instance(
        self,
        name: str,
        modloader: ModLoaderType,
        loader_version: str = None
    ):
        """Устанавливает модлоадер в уже существующий инстанс"""
        instance_path = self.get_instance_path(name)
        json_path = instance_path / "instance.json"

        if not json_path.exists():
            raise FileNotFoundError(f"Инстанс '{name}' не найден!")

        instance = Instance.model_validate_json(json_path.read_text(encoding="utf-8"))

        installed_version = Installer.install_modloader(
            modloader=modloader,
            minecraft_version=instance.version,
            instance_path=str(instance_path),
            loader_version=loader_version,
            java_path=self.settings.java_path
        )

        instance.modloader = modloader
        instance.modloader_version = loader_version
        instance.version = installed_version
        json_path.write_text(instance.model_dump_json(indent=2), encoding="utf-8")

        logger.info(f"✅ Модлоадер {modloader.value} установлен в '{name}'")

    def update_instance_settings(self, name: str, ram_mb: int = None, jvm_args: list = None):
        """Обновляет настройки инстанса (RAM + JVM)"""
        json_path = self.get_instance_path(name) / "instance.json"
        if not json_path.exists():
            return
        instance = Instance.model_validate_json(json_path.read_text(encoding="utf-8"))
        if ram_mb:
            instance.ram_mb = ram_mb
        if jvm_args is not None:
            instance.jvm_args = jvm_args
        json_path.write_text(instance.model_dump_json(indent=2), encoding="utf-8")
        logger.info(f"✅ Настройки инстанса '{name}' обновлены")
