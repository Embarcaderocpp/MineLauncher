import sys
import typer
from mc_launcher.cli.main import app as cli_app

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from mc_launcher.gui.main import MinecraftLauncherGUI
        gui = MinecraftLauncherGUI()
        gui.mainloop()
    else:
        cli_app()