"""Install or uninstall the AGY-HUD plugin into ~/.gemini/config/plugins/agy-hud."""

import argparse
import os
import shutil


PLUGIN_NAME = "agy-hud"


def target_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".gemini", "config", "plugins", PLUGIN_NAME)


def source_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def install() -> None:
    src = source_dir()
    dst = target_dir()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("install_plugin.py", "__pycache__", "*.pyc"),
    )
    print(f"Installed {PLUGIN_NAME} plugin to: {dst}")


def uninstall() -> None:
    dst = target_dir()
    if os.path.exists(dst):
        shutil.rmtree(dst)
        print(f"Removed {PLUGIN_NAME} plugin from: {dst}")
    else:
        print(f"Plugin directory not found: {dst}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install/uninstall AGY-HUD plugin")
    parser.add_argument("--uninstall", action="store_true", help="Remove installed plugin")
    args = parser.parse_args()
    if args.uninstall:
        uninstall()
    else:
        install()


if __name__ == "__main__":
    main()
