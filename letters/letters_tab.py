# letters/letters_tab.py

import os
import json
from string import Template
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QListWidget, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
# from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication



class LettersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.templates_file = "templates/letters_templates.json"
        self.templates = self.load_templates()
        self.selected_template = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 🔹 Поля ввода
        form_layout = QVBoxLayout()
        self.vin_input = QLineEdit()
        self.contract_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.license_input = QLineEdit()
        self.lessee_input = QLineEdit()
        self.comment_input = QTextEdit()

        form_layout.addWidget(QLabel("VIN:"))
        form_layout.addWidget(self.vin_input)
        form_layout.addWidget(QLabel("Договор:"))
        form_layout.addWidget(self.contract_input)
        form_layout.addWidget(QLabel("Марка ТС:"))
        form_layout.addWidget(self.brand_input)
        form_layout.addWidget(QLabel("Госномер:"))
        form_layout.addWidget(self.license_input)
        form_layout.addWidget(QLabel("Лизингополучатель:"))
        form_layout.addWidget(self.lessee_input)
        form_layout.addWidget(QLabel("Комментарий:"))
        form_layout.addWidget(self.comment_input)

        layout.addLayout(form_layout)

        # 🔹 Список шаблонов
        layout.addWidget(QLabel("Шаблоны писем:"))
        self.template_list = QListWidget()
        self.template_list.addItems(self.templates.keys())
        self.template_list.itemClicked.connect(self.select_template)
        layout.addWidget(self.template_list)

        # 🔹 Кнопки
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Сформировать сообщение")
        self.copy_button = QPushButton("Копировать сообщение")
        self.copy_button.setEnabled(False)

        self.generate_button.clicked.connect(self.generate_message)
        self.copy_button.clicked.connect(self.copy_message)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.copy_button)
        layout.addLayout(button_layout)

        # 🔹 Вывод сообщения
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Courier", 10))
        layout.addWidget(QLabel("Результат:"))
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def load_templates(self):
        if os.path.exists(self.templates_file):
            with open(self.templates_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def select_template(self, item):
        self.selected_template = item.text()
        self.result_text.clear()
        self.copy_button.setEnabled(False)

    def generate_message(self):
        if not self.selected_template:
            QMessageBox.warning(self, "Нет шаблона", "Выберите шаблон сообщения.")
            return

        data = {
            "vin": self.vin_input.text().strip(),
            "contract": self.contract_input.text().strip(),
            "brand": self.brand_input.text().strip(),
            "license": self.license_input.text().strip(),
            "lessee": self.lessee_input.text().strip(),
            "comment": self.comment_input.toPlainText().strip()
        }

        # Проверка: все поля пустые
        if all(not val for val in data.values()):
            QMessageBox.warning(self, "Пусто", "Заполните хотя бы одно поле.")
            return

        template_text = self.templates.get(self.selected_template, "")
        message = Template(template_text).safe_substitute(data)

        if not message.strip():
            QMessageBox.warning(self, "Ошибка", "Результат пустой.")
            return

        self.result_text.setPlainText(message)
        self.copy_button.setEnabled(True)

    def copy_message(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_text.toPlainText())
        QMessageBox.information(self, "Готово", "Сообщение скопировано.")
