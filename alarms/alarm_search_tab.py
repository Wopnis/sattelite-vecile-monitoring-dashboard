from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QDialog, QTextEdit, QDialogButtonBox, QApplication
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt


class AlarmSearchTab(QWidget):
    def __init__(self, alarm_manager):
        super().__init__()
        self.alarm_manager = alarm_manager

        layout = QVBoxLayout()

        # 🔹 Поиск по тревогам
        form_layout = QHBoxLayout()
        self.vin_input = QLineEdit()
        self.contract_input = QLineEdit()
        self.keyword_input = QLineEdit()

        self.vin_input.returnPressed.connect(self.perform_search)
        self.contract_input.returnPressed.connect(self.perform_search)
        self.keyword_input.returnPressed.connect(self.perform_search)

        form_layout.addWidget(QLabel("VIN:"))
        form_layout.addWidget(self.vin_input)
        form_layout.addWidget(QLabel("Договор:"))
        form_layout.addWidget(self.contract_input)
        form_layout.addWidget(QLabel("Ключевое слово:"))
        form_layout.addWidget(self.keyword_input)

        self.search_button = QPushButton("Искать")
        self.search_button.setDefault(True)
        self.search_button.clicked.connect(self.perform_search)
        form_layout.addWidget(self.search_button)

        self.clear_button = QPushButton("Очистить поиск")
        self.clear_button.clicked.connect(self.clear_search)
        form_layout.addWidget(self.clear_button)

        layout.addLayout(form_layout)

        # 🔍 Глобальный поиск
        global_layout = QHBoxLayout()
        global_layout.addWidget(QLabel("🔎 Глобальный поиск:"))
        self.global_input = QLineEdit()
        global_layout.addWidget(self.global_input)

        self.global_search_button = QPushButton("Найти везде")
        self.global_search_button.clicked.connect(self.perform_global_search)
        global_layout.addWidget(self.global_search_button)

        layout.addLayout(global_layout)

        # 🔹 Результаты
        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.highlight_item)
        self.result_list.itemPressed.connect(self.handle_right_click)
        self.result_list.itemDoubleClicked.connect(self.show_details_dialog)
        layout.addWidget(self.result_list)

        self.setLayout(layout)

    def perform_search(self):
        vin = self.vin_input.text().strip().lower()
        contract = self.contract_input.text().strip().lower()
        keyword = self.keyword_input.text().strip().lower()

        if not vin and not contract and not keyword:
            QMessageBox.warning(self, "Пустой запрос", "Введите VIN, договор или ключевое слово для поиска.")
            return

        results = []
        for alarm in self.alarm_manager.alarms:
            match = True
            if vin and vin not in alarm.get("vin", "").lower():
                match = False
            if contract and contract not in alarm.get("contract", "").lower():
                match = False
            if keyword:
                combined = " ".join([
                    alarm.get("message", ""), alarm.get("comment", ""),
                    alarm.get("brand", ""), alarm.get("license", ""), alarm.get("lessee", "")
                ]).lower()
                if keyword not in combined:
                    match = False
            if match:
                results.append(alarm)

        self.result_list.clear()
        if not results:
            QMessageBox.information(self, "Результаты", "Ничего не найдено.")
            return

        for alarm in results:
            timestamp = alarm.get("timestamp", "-")
            closed = alarm.get("closed_at", "-")
            item_text = f"[Тревога] {timestamp} | {alarm.get('vin')} | {alarm.get('contract')} | {alarm.get('message')}"
            tooltip = (
                f"Марка: {alarm.get('brand')}\n"
                f"VIN: {alarm.get('vin')}\n"
                f"Договор: {alarm.get('contract')}\n"
                f"Открыта: {timestamp}\n"
                f"Закрыта: {closed}"
            )
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, alarm)
            item.setToolTip(tooltip)
            item.setForeground(Qt.red)
            item.setBackground(Qt.yellow)
            self.result_list.addItem(item)

    def clear_search(self):
        self.vin_input.clear()
        self.contract_input.clear()
        self.keyword_input.clear()
        self.global_input.clear()
        self.result_list.clear()
        self.vin_input.setFocus()

    def highlight_item(self, item):
        item.setBackground(QColor("#eef"))

    def handle_right_click(self, item):
        if QApplication.mouseButtons() == Qt.RightButton:
            self.show_details_dialog(item)

    def show_details_dialog(self, item):
        data = item.data(Qt.UserRole)
        if not data:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Детали")
        layout = QVBoxLayout()

        text_box = QTextEdit()
        text_box.setReadOnly(True)
        text_box.setFont(QFont("Courier", 10))

        if "message" in data:  # Это тревога
            text_box.setText(
                f"Марка: {data.get('brand')}\n"
                f"VIN: {data.get('vin')}\n"
                f"Госномер: {data.get('license')}\n"
                f"Договор: {data.get('contract')}\n"
                f"Лизингополучатель: {data.get('lessee')}\n"
                f"Сообщение: {data.get('message')}\n"
                f"Комментарий: {data.get('comment')}\n"
                f"Открыта: {data.get('timestamp', '-')}\n"
                f"Закрыта: {data.get('closed_at', '-')}"
            )
        elif "title" in data and "content" in data:  # Это заметка
            text_box.setText(f"Заметка:\n\n{data.get('title')}\n\n{data.get('content')}")
        elif "reason" in data:  # Это чёрный список
            text_box.setText(
                f"🚫 Чёрный список\n\n"
                f"VIN: {data.get('vin')}\n"
                f"Договор: {data.get('contract')}\n"
                f"Причина: {data.get('reason')}"
            )
        else:
            text_box.setText(str(data))

        layout.addWidget(text_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()

    def perform_global_search(self):
        from utils.global_search import global_search

        keyword = self.global_input.text().strip()
        self.result_list.clear()

        if not keyword:
            QMessageBox.warning(self, "Пусто", "Введите слово для глобального поиска.")
            return

        results = global_search(keyword)
        if not results:
            QMessageBox.information(self, "Поиск", "Ничего не найдено.")
            return

        for res in results:
            item = QListWidgetItem(res["text"])
            item.setData(Qt.UserRole, res.get("data"))
            item.setToolTip(res.get("tooltip", ""))
            item.setForeground(Qt.black)
            item.setBackground(Qt.lightGray)
            self.result_list.addItem(item)
