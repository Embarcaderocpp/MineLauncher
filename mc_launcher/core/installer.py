from pathlib import Path
from typing import Optional
import minecraft_launcher_lib.install as mcl_install
import os
import shutil
from tqdm import tqdm
from ..utils import logger
from ..modloaders import ModLoaders
from ..models import ModLoaderType

class Installer:
    @staticmethod
    def _setup_custom_temp():
        """Чистый temp + проверка прав"""
        temp_dir = Path("temp_install").absolute()
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Проверка доступности
        test_file = temp_dir / "write_test.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError as e:
            logger.error(f"❌ Нет прав на запись в temp_install: {e}")
            raise

        os.environ["TMP"] = str(temp_dir)
        os.environ["TEMP"] = str(temp_dir)
        os.environ["TMPDIR"] = str(temp_dir)

        logger.info(f"🔧 Чистый temp создан: {temp_dir}")
        return temp_dir

    @staticmethod
    def install_vanilla(version: str, instance_path: str, progress_callback=None):
        Installer._setup_custom_temp()
        instance_path = str(Path(instance_path).absolute())

        logger.info(f"🚀 Установка Vanilla {version}")

        pbar = tqdm(total=0, desc=f"Vanilla {version}", unit="файл", ncols=80)

        def set_status(text: str):
            logger.info(f"Статус: {text}")
            pbar.set_description(text)

        def set_max(max_val: int):
            pbar.total = max_val
            pbar.refresh()
            if progress_callback:
                progress_callback(0, max_val)

        def set_progress(current: int):
            pbar.n = current
            pbar.refresh()
            if progress_callback and pbar.total > 0:
                progress_callback(current, pbar.total)

        callback = {"setStatus": set_status, "setMax": set_max, "setProgress": set_progress}

        mcl_install.install_minecraft_version(
            version=version,
            minecraft_directory=instance_path,
            callback=callback
        )
        pbar.close()
        logger.info(f"✅ Vanilla {version} готов!")

    @staticmethod
    def install_modloader(
        modloader: ModLoaderType,
        minecraft_version: str,
        instance_path: str,
        loader_version: Optional[str] = None,
        java_path: str = "java",
        progress_callback=None   # ← добавлено
    ) -> str:
        Installer._setup_custom_temp()

        instance_path = str(Path(instance_path).absolute())

        vanilla_path = Path(instance_path) / "versions" / minecraft_version
        if not vanilla_path.exists():
            Installer.install_vanilla(minecraft_version, instance_path, progress_callback)

        pbar = tqdm(total=0, desc=f"{modloader.value.upper()}", unit="шаг", ncols=80)

        def set_status(text: str):
            logger.info(f"Статус: {text}")
            pbar.set_description(text)

        def set_max(max_val: int):
            pbar.total = max_val
            pbar.refresh()
            if progress_callback:
                progress_callback(0, max_val)

        def set_progress(current: int):
            pbar.n = current
            pbar.refresh()
            if progress_callback and pbar.total > 0:
                progress_callback(current, pbar.total)

        callback = {"setStatus": set_status, "setMax": set_max, "setProgress": set_progress}

        try:
            installed_version = ModLoaders.install(
                modloader=modloader,
                minecraft_version=minecraft_version,
                instance_path=instance_path,
                loader_version=loader_version,
                java_path=java_path,
                callback=callback
            )
            pbar.close()
            return installed_version
        except Exception as e:
            pbar.close()
            logger.error(f"❌ Ошибка установки {modloader.value}: {e}")
            raise
