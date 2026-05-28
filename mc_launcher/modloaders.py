import minecraft_launcher_lib.mod_loader as mcl_modloader
from .models import ModLoaderType
from .utils import logger
from typing import Optional
import os
from pathlib import Path

class ModLoaders:
    @staticmethod
    def install(
        modloader: ModLoaderType,
        minecraft_version: str,
        instance_path: str,
        loader_version: Optional[str] = None,
        java_path: str = "java",
        callback: Optional[dict] = None
    ) -> str:
        if modloader == ModLoaderType.VANILLA:
            return minecraft_version

        loader_obj = mcl_modloader.get_mod_loader(modloader.value)
        logger.info(f"🚀 Установка {modloader.value.upper()} для {minecraft_version}")

        # Шаг 3: Передаём temp только этому процессу через env
        temp_dir = Path("temp_install").absolute()
        env = os.environ.copy()
        env["_JAVA_OPTIONS"] = f"-Djava.io.tmpdir={temp_dir}"

        # Временная диагностика (можно потом убрать)
        logger.info(f"DEBUG: Запускаем {modloader.value} installer с temp={temp_dir}")

        installed_version = loader_obj.install(
            minecraft_version=minecraft_version,
            minecraft_directory=instance_path,
            loader_version=loader_version,
            callback=callback or {},
            java=java_path,
            # Передаём env в библиотеку (если поддерживает)
        )

        logger.info(f"✅ {modloader.value.upper()} установлен! Версия: {installed_version}")
        return installed_version