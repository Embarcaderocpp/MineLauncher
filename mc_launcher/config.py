from pydantic_settings import BaseSettings, SettingsConfigDict
import tomli
import tomli_w
from pathlib import Path
import shutil
import subprocess
import glob
from .utils import logger

class Settings(BaseSettings):
    minecraft_dir: str = "instances"
    java_path: str = "java"
    last_instance: str = "default"
    theme: str = "dark"

    model_config = SettingsConfigDict(
        env_prefix="MC_",
        extra="ignore"
    )

    @staticmethod
    def _find_java() -> str:
        """Улучшенный поиск + всегда возвращаем java.exe"""
        # 1. PATH
        java = shutil.which("java") or shutil.which("java.exe")
        if java and Settings._check_java_version(java):
            logger.info(f"✅ Java найдена в PATH: {java}")
            return java

        # 2. Windows
        if Path("C:/").exists():
            windows_patterns = [
                r"C:\Program Files\Eclipse Adoptium\jdk-21*\bin\java.exe",
                r"C:\Program Files\Eclipse Adoptium\jdk-21*\bin\javaw.exe",
                r"C:\Program Files\Java\jdk-21*\bin\java.exe",
                r"C:\Program Files (x86)\Common Files\Oracle\Java\javapath\java.exe",
            ]
            for pattern in windows_patterns:
                for path in glob.glob(pattern):
                    if Path(path).is_file() and Settings._check_java_version(path):
                        logger.info(f"✅ Java найдена: {path}")
                        return path

        # 3. Linux + macOS
        common = [
            "/usr/bin/java",
            "/usr/lib/jvm/java-21-openjdk/bin/java",
            "/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home/bin/java",
        ]
        for p in common:
            if Path(p).exists() and Settings._check_java_version(p):
                return p

        logger.error("❌ Java 21+ не найдена!")
        return "java"

    @staticmethod
    def _check_java_version(java_path: str) -> bool:
        try:
            result = subprocess.run([java_path, "-version"], capture_output=True, text=True, timeout=5)
            return "21." in result.stderr or "21." in result.stdout
        except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired):
            return False

    @classmethod
    def load(cls) -> "Settings":
        if Path("config.toml").exists():
            with open("config.toml", "rb") as f:
                data = tomli.load(f)
            merged = {}
            merged.update(data.get("minecraft", {}))
            merged.update(data.get("settings", {}))
            settings = cls.model_validate(merged)
        else:
            settings = cls()

        # Финальная проверка — если путь заканчивается на bin, добавляем java.exe
        jp = Path(settings.java_path)
        if jp.is_dir() or str(jp).endswith("bin"):
            exe = jp / "java.exe" if (jp / "java.exe").exists() else jp / "javaw.exe"
            if exe.exists():
                settings.java_path = str(exe)
                logger.info(f"🔧 Исправлен путь к Java: {settings.java_path}")

        if settings.java_path in ("java", "java.exe") or not Path(settings.java_path).exists():
            settings.java_path = Settings._find_java()
            settings.save()

        logger.info(f"🔧 Используем Java: {settings.java_path}")
        return settings

    def save(self):
        data = {
            "minecraft": {
                "minecraft_dir": self.minecraft_dir,
                "java_path": self.java_path,
                "last_instance": self.last_instance,
            },
            "settings": {"theme": self.theme}
        }
        with open("config.toml", "wb") as f:
            tomli_w.dump(data, f)