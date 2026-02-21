"""
Root entry point for the LCCA application.
Run: python main.py
"""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from gui.main import Manager
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    m = Manager()
    m.spawn()
    sys.exit(app.exec())
