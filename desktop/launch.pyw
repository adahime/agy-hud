"""Silent Windows launcher for the AGY-HUD floating pill."""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from desktop.cli import run_gui

if __name__ == "__main__":
    run_gui()
