import minecraft_launcher_lib.command as mcl_command
import minecraft_launcher_lib.utils as mcl_utils
import subprocess
import sys
from ..utils import logger

class Runner:
    @staticmethod
    def get_launch_command(instance_path: str, version: str, nickname: str = "CrackedPlayer",
                          jvm_args: list = None, ram_mb: int = 2048):
        options = mcl_utils.generate_test_options()
        options["username"] = nickname
        if jvm_args:
            options["jvmArguments"] = jvm_args
        options["max_memory"] = ram_mb  # minecraft-launcher-lib сам добавит -Xmx

        command = mcl_command.get_minecraft_command(
            version=version,
            minecraft_directory=instance_path,
            options=options
        )
        return command

    @staticmethod
    def run(instance_path: str, version: str, nickname: str = "CrackedPlayer",
            java_path: str = "java", jvm_args: list = None, ram_mb: int = 2048):
        logger.info(f"▶️ Запуск {version} как {nickname} (RAM: {ram_mb}MB)")

        command = Runner.get_launch_command(instance_path, version, nickname, jvm_args, ram_mb)
        if java_path != "java" and java_path:
            command[0] = java_path

        logger.info(f"Команда: {' '.join(command[:6])} ...")

        try:
            popen_kwargs = {"shell": False}
            if sys.platform == "win32":
                popen_kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
            else:
                # На POSIX запускаем в новой сессии, чтобы процесс не умирал вместе с лаунчером
                popen_kwargs["start_new_session"] = True

            subprocess.Popen(command, **popen_kwargs)
            logger.info("✅ Minecraft запущен!")
        except Exception as e:
            logger.error(f"❌ Ошибка запуска: {e}")
