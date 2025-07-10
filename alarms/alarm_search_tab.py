from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QDialog, QTextEdit, QDialogButtonBox
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


class AlarmSearchTab(QWidget):
    def __init__(self, alarm_manager):
        super().__init__()
        self.alarm_manager = alarm_manager

        layout = QVBoxLayout()

        # 🔹 Форма поиска
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

        # 🔹 Результаты поиска
        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.highlight_item)
        self.result_list.itemPressed.connect(self.handle_right_click)
        self.result_list.itemDoubleClicked.connect(self.show_details_dialog)  # ✅ Двойной клик
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
        for i, alarm in enumerate(self.alarm_manager.alarms):
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
                results.append((i, alarm))

        self.result_list.clear()
        if not results:
            QMessageBox.information(self, "Результаты", "Ничего не найдено.")
            return

        for index, alarm in results:
            item_text = f"{alarm.get('vin')} | {alarm.get('contract')} | {alarm.get('brand')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, alarm)
            item.setToolTip(
                f"Марка: {alarm.get('brand')}\n"
                f"VIN: {alarm.get('vin')}\n"
                f"Договор: {alarm.get('contract')}\n"
                f"Сообщение: {alarm.get('message')}\n"
                f"Комментарий: {alarm.get('comment')}"
            )
            item.setForeground(Qt.red)
            item.setBackground(Qt.yellow)
            self.result_list.addItem(item)

    def clear_search(self):
        self.vin_input.clear()
        self.contract_input.clear()
        self.keyword_input.clear()
        self.result_list.clear()
        self.vin_input.setFocus()

    def highlight_item(self, item):
        item.setBackground(QColor("#eef"))

    def handle_right_click(self, item):
        if QApplication.mouseButtons() == Qt.RightButton:
            self.show_details_dialog(item)

    def show_details_dialog(self, item):
        alarm = item.data(Qt.UserRole)
        dialog = QDialog(self)
        dialog.setWindowTitle("Детали тревоги")
        layout = QVBoxLayout()

        text_box = QTextEdit()
        text_box.setReadOnly(True)
        text_box.setFont(QFont("Courier", 10))
        text_box.setText(
            f"Марка: {alarm.get('brand')}\n"
            f"VIN: {alarm.get('vin')}\n"
            f"Госномер: {alarm.get('license')}\n"
            f"Договор: {alarm.get('contract')}\n"
            f"Лизингополучатель: {alarm.get('lessee')}\n"
            f"Сообщение: {alarm.get('message')}\n"
            f"Комментарий: {alarm.get('comment')}\n"
            f"Добавлено: {alarm.get('timestamp')}\n"
            f"Закрыто: {alarm.get('closed_at', '-')}"
        )
        layout.addWidget(text_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()
