"""
──────────────────────────────────────────────
Приложение мониторинга | Автор: Wopnis
(c) 2025 Все права защищены
──────────────────────────────────────────────
"""

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:  # noqa: E722
    pass

import sys
import json
import os
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QStatusBar, QMenuBar, QMenu, QAction
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt

from main_window import MainWindow

# 🔏 Цифровая подпись
__author_signature__ = "Wopnis-2025-UNIQUE-SIGNATURE-741"
__author_hash__ = hashlib.sha256("W-2025".encode()).hexdigest()

# 🌗 Путь до файла настроек темы
THEME_CONFIG_PATH = "config/theme.json"

def load_theme_preference():
    if os.path.exists(THEME_CONFIG_PATH):
        try:
            with open(THEME_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("theme", "light")
        except:  # noqa: E722
            pass
    return "light"

def save_theme_preference(theme_name):
    os.makedirs(os.path.dirname(THEME_CONFIG_PATH), exist_ok=True)
    with open(THEME_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"theme": theme_name}, f)

def apply_light_theme(app: QApplication):
    palette = QPalette()
    base_color = QColor("#f9f9f9")
    text_color = QColor("#2c2c2c")
    accent_color = QColor("#6c63ff")

    palette.setColor(QPalette.Window, base_color)
    palette.setColor(QPalette.WindowText, text_color)
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipText, text_color)
    palette.setColor(QPalette.Text, text_color)
    palette.setColor(QPalette.Button, QColor("#e0e0e0"))
    palette.setColor(QPalette.ButtonText, text_color)
    palette.setColor(QPalette.Highlight, accent_color)
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))

    app.setPalette(palette)

    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
        }
        QPushButton {
            background-color: #6c63ff;
            color: white;
            padding: 6px 12px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #5952d4;
        }
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 4px;
        }
        QListWidget {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 6px;
        }
        QTabBar::tab {
            background: #eaeaea;
            border: 1px solid #cccccc;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 6px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom: 1px solid white;
        }
        QToolTip {
            background-color: #fefefe;
            color: #333333;
            border: 1px solid #aaaaaa;
            padding: 4px;
            border-radius: 6px;
        }
    """)

def apply_dark_theme(app: QApplication):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#2b2b2b"))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor("#3c3f41"))
    palette.setColor(QPalette.AlternateBase, QColor("#2b2b2b"))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor("#3c3f41"))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.Highlight, QColor("#007acc"))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)

    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
            background-color: #2b2b2b;
            color: #534646;
        }

        QPushButton {
            background-color: #007acc;
            color: black;
            padding: 6px 12px;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #005999;
        }

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #444;
            color: #534646;
            border: 1px solid #888;
            border-radius: 6px;
            padding: 4px;
        }

        QListWidget {
            background-color: #3a3a3a;
            color: #534646;
            border: 1px solid #555;
            border-radius: 6px;
        }

        QTabBar::tab {
            background: #555;
            color: black;
            padding: 6px 12px;
            margin-right: 2px;
            border-radius: 4px;
        }

        QTabBar::tab:selected {
            background: #3c3f41;
            font-weight: bold;
        }

        QToolTip {
            background-color: #444444;
            color: black;
            border: 1px solid #888888;
            padding: 4px;
            border-radius: 6px;
        }
    """)


def toggle_theme(app: QApplication, window: MainWindow, menu_action: QAction):
    current_theme = load_theme_preference()
    new_theme = "dark" if current_theme == "light" else "light"
    save_theme_preference(new_theme)

    if new_theme == "dark":
        apply_dark_theme(app)
        menu_action.setText("Светлая тема")
    else:
        apply_light_theme(app)
        menu_action.setText("Тёмная тема")

    window.repaint()

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/monitoring.ico"))

    theme = load_theme_preference()
    if theme == "dark":
        apply_dark_theme(app)
    else:
        apply_light_theme(app)

    window = MainWindow()

    # 📟 Статус бар
    status_bar = QStatusBar()
    status_bar.showMessage("Автор: W | © 2025")
    window.setStatusBar(status_bar)

    # 🎛️ Меню для переключения темы
    menubar = QMenuBar(window)
    view_menu = QMenu("Вид", menubar)
    theme_action = QAction("Тёмная тема" if theme == "light" else "Светлая тема", window)
    theme_action.triggered.connect(lambda: toggle_theme(app, window, theme_action))
    view_menu.addAction(theme_action)
    menubar.addMenu(view_menu)
    window.setMenuBar(menubar)

    window.show()
    sys.exit(app.exec_())
