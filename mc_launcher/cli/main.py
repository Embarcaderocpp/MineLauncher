import typer
from ..core.manager import LauncherManager
from ..models import ModLoaderType
from ..utils import logger

app = typer.Typer(help="Неофициальный Minecraft Launcher CLI")

manager = LauncherManager()

@app.command()
def create(
    name: str,
    version: str = typer.Option("1.21.5", "--version", "-v", help="Версия Minecraft"),
    nickname: str = typer.Option("CrackedPlayer", "--nickname", "-n", help="Никнейм"),
    loader: ModLoaderType = typer.Option(ModLoaderType.VANILLA, "--loader", "-l", help="Модлоадер"),
    loader_version: str = typer.Option(None, "--loader-version", help="Версия модлоадера (None = latest)"),
):
    """Создать новый инстанс"""
    manager.create_instance(name, version, nickname, loader, loader_version)
    typer.echo(f"✅ Инстанс '{name}' создан! (MC {version} + {loader.value})")

@app.command()
def launch(name: str = typer.Argument(None, help="Имя инстанса (по умолчанию последний)")):
    """Запустить инстанс"""
    manager.launch(name)
    typer.echo(f"▶️ Запускаем {name or manager.settings.last_instance}...")

@app.command()
def list():
    """Список всех инстансов"""
    instances = manager.list_instances()
    typer.echo(f"📋 Инстансов найдено: {len(instances)}")
    for i in instances:
        mod = i.get("modloader", "vanilla")
        typer.echo(f"  • {i['name']} | {i['version']} | {mod}")

@app.command()
def delete(name: str):
    """Удалить инстанс"""
    manager.delete_instance(name)
    typer.echo(f"🗑️ Инстанс '{name}' удалён")

@app.command()
def info(name: str = typer.Argument(None, help="Имя инстанса")):
    """Информация об инстансе"""
    if name is None:
        name = manager.settings.last_instance
    instance = manager.get_instance_info(name)
    typer.echo(f"📄 Инстанс: {instance.name}")
    typer.echo(f"   Версия: {instance.version}")
    typer.echo(f"   Модлоадер: {instance.modloader.value}")
    typer.echo(f"   Ник: {instance.nickname}")
    typer.echo(f"   RAM: {instance.ram_mb} MB")
    if instance.last_played:
        typer.echo(f"   Последний запуск: {instance.last_played}")

# ───── Новые команды Этапа 4 ─────

@app.command()
def list_versions():
    """Список доступных версий Minecraft"""
    typer.echo("🔍 Загружаем список версий Minecraft...")
    versions = manager.list_available_versions()
    typer.echo(f"📋 Доступно версий: {len(versions)}")
    for v in versions[:30]:  # показываем первые 30
        typer.echo(f"  • {v['id']} ({v['type']})")

@app.command()
def install_modloader(
    name: str,
    loader: ModLoaderType = typer.Option(..., "--loader", "-l", help="Модлоадер"),
    loader_version: str = typer.Option(None, "--loader-version", help="Версия модлоадера"),
):
    """Установить модлоадер в существующий инстанс"""
    manager.install_modloader_to_instance(name, loader, loader_version)
    typer.echo(f"✅ Модлоадер {loader.value} установлен в инстанс '{name}'")

if __name__ == "__main__":
    app()