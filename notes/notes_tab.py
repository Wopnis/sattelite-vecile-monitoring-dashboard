import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QInputDialog, QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from datetime import datetime
from PyQt5.QtWidgets import QApplication


class NotesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.notes_file = "notes/notes_data.json"
        self.notes = self.load_notes()

        layout = QVBoxLayout()

        # 🔹 Форма добавления
        self.title_input = QLineEdit()
        self.content_input = QTextEdit()
        add_button = QPushButton("Добавить заметку")
        add_button.clicked.connect(self.add_note)

        layout.addWidget(QLabel("Заголовок:"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Содержание:"))
        layout.addWidget(self.content_input)
        layout.addWidget(add_button)

        # 🔹 Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по заголовку или содержанию...")
        self.search_input.returnPressed.connect(self.search_notes)
        search_button = QPushButton("Искать")
        search_button.clicked.connect(self.search_notes)
        clear_button = QPushButton("Очистить")
        clear_button.clicked.connect(self.clear_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)
        layout.addLayout(search_layout)

        # 🔹 Список заметок
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.show_note_view)
        self.list_widget.itemPressed.connect(self.handle_right_click)
        layout.addWidget(self.list_widget)

        # 🔹 Удаление
        delete_button = QPushButton("Удалить выбранную заметку")
        delete_button.clicked.connect(self.delete_note)
        layout.addWidget(delete_button)

        self.setLayout(layout)
        self.refresh_list()

    def load_notes(self):
        if os.path.exists(self.notes_file):
            with open(self.notes_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_notes(self):
        os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
        with open(self.notes_file, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)

    def add_note(self):
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        if not title or not content:
            QMessageBox.warning(self, "Ошибка", "Заполните заголовок и содержание.")
            return
        note = {
            "title": title,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.notes.append(note)
        self.save_notes()
        self.title_input.clear()
        self.content_input.clear()
        self.refresh_list()

    def search_notes(self):
        keyword = self.search_input.text().strip().lower()
        self.list_widget.clear()
        for note in self.notes:
            if keyword in note["title"].lower() or keyword in note["content"].lower():
                item = QListWidgetItem(f"{note['title']} ({note['created_at']})")
                item.setData(Qt.UserRole, note)
                self.list_widget.addItem(item)

    def clear_search(self):
        self.search_input.clear()
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for note in self.notes:
            item = QListWidgetItem(f"{note['title']} ({note['created_at']})")
            item.setData(Qt.UserRole, note)
            self.list_widget.addItem(item)

    def show_note_view(self, item):
        note = item.data(Qt.UserRole)
        dialog = QDialog(self)
        dialog.setWindowTitle(note["title"])
        layout = QVBoxLayout()
        text_box = QTextEdit()
        text_box.setReadOnly(True)
        text_box.setFont(QFont("Courier", 10))
        text_box.setText(note["content"])
        layout.addWidget(text_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()

    def handle_right_click(self, item):
        if QApplication.mouseButtons() == Qt.RightButton:
            self.edit_note(item)

    def edit_note(self, item):
        note = item.data(Qt.UserRole)
        title, ok1 = QInputDialog.getText(self, "Редактировать заголовок", "Заголовок:", text=note["title"])
        if not ok1 or not title.strip():
            return
        content, ok2 = QInputDialog.getMultiLineText(self, "Редактировать содержание", "Содержание:", note["content"])
        if not ok2 or not content.strip():
            return
        note["title"] = title.strip()
        note["content"] = content.strip()
        self.save_notes()
        self.refresh_list()

    def delete_note(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        note = item.data(Qt.UserRole)
        confirm = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Удалить заметку '{note['title']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            confirm2 = QMessageBox.question(
                self, "Подтверждение",
                "Вы точно уверены?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm2 == QMessageBox.Yes:
                self.notes.remove(note)
                self.save_notes()
                self.refresh_list()
