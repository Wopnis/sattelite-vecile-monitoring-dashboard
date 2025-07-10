"""
──────────────────────────────────────────────
Приложение мониторинга | Автор: Wopnis
(c) 2025 Все права защищены
──────────────────────────────────────────────
"""

import sys
import hashlib
from PyQt5.QtWidgets import QApplication, QStatusBar
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtGui import QIcon
# from PyQt5.QtWidgets import QApplication

from main_window import MainWindow

# 🔏 Цифровая подпись (не мешает работе, но легко доказать авторство)
__author_signature__ = "Wopnis-2025-UNIQUE-SIGNATURE-741"
__author_hash__ = hashlib.sha256("W-2025".encode()).hexdigest()

def apply_bento_theme(app: QApplication):
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
            font-size: 13px;
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/monitoring.ico")) 

    apply_bento_theme(app)

    window = MainWindow()

    # 🖋️ Строка авторства внизу окна
    status_bar = QStatusBar()
    status_bar.showMessage("Автор: W | © 2025")
    window.setStatusBar(status_bar)

    window.show()
    sys.exit(app.exec_())
