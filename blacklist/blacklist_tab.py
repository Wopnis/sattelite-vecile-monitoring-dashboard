import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QDialog, QFormLayout, QDialogButtonBox, QLabel
)
from PyQt5.QtCore import Qt


class BlacklistTab(QWidget):
    def __init__(self):
        super().__init__()
        self.data_file = "data/blacklist.json"
        self.records = self.load_blacklist()

        main_layout = QVBoxLayout()

        # 📥 Область добавления записи
        main_layout.addWidget(QLabel("<b>Добавить запись в чёрный список</b>"))

        self.vin_input = QLineEdit()
        self.vin_input.setPlaceholderText("VIN")
        self.contract_input = QLineEdit()
        self.contract_input.setPlaceholderText("Договор")
        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Причина добавления в чёрный список")
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_record)

        main_layout.addWidget(self.vin_input)
        main_layout.addWidget(self.contract_input)
        main_layout.addWidget(self.reason_input)
        main_layout.addWidget(self.add_button)

        # 🔍 Поиск
        main_layout.addWidget(QLabel("<b>Поиск в чёрном списке</b>"))
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите ключевое слово, VIN или договор")
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.select_record)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.edit_record)
        main_layout.addWidget(self.list_widget)

        self.setLayout(main_layout)

    def load_blacklist(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:  # noqa: E722
                return []
        return []

    def save_blacklist(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2, ensure_ascii=False)

    def add_record(self):
        vin = self.vin_input.text().strip()
        contract = self.contract_input.text().strip()
        reason = self.reason_input.toPlainText().strip()

        if not vin and not contract:
            QMessageBox.warning(self, "Ошибка", "Укажите VIN или договор.")
            return

        self.records.append({
            "vin": vin,
            "contract": contract,
            "reason": reason
        })
        self.save_blacklist()
        self.vin_input.clear()
        self.contract_input.clear()
        self.reason_input.clear()
        QMessageBox.information(self, "Добавлено", "Запись добавлена в чёрный список.")

    def perform_search(self):
        query = self.search_input.text().strip().lower()
        self.list_widget.clear()
        if not query:
            return
        for record in self.records:
            if (
                query in record.get("vin", "").lower()
                or query in record.get("contract", "").lower()
                or query in record.get("reason", "").lower()
            ):
                item_text = f"{record.get('vin', '')} | {record.get('contract', '')} | {record.get('reason', '')}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, record)
                self.list_widget.addItem(item)

    def select_record(self, item):
        record = item.data(Qt.UserRole)
        QMessageBox.information(
            self, "Запись",
            f"VIN: {record.get('vin','')}\nДоговор: {record.get('contract','')}\nПричина: {record.get('reason','')}"
        )

    def edit_record(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        record = item.data(Qt.UserRole)

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование записи")

        layout = QFormLayout()

        vin_input = QLineEdit(record.get("vin", ""))
        contract_input = QLineEdit(record.get("contract", ""))
        reason_input = QTextEdit(record.get("reason", ""))

        layout.addRow("VIN:", vin_input)
        layout.addRow("Договор:", contract_input)
        layout.addRow("Причина:", reason_input)

        # Кнопки
        buttons = QDialogButtonBox()
        save_button = buttons.addButton("Сохранить", QDialogButtonBox.AcceptRole)
        cancel_button = buttons.addButton("Отмена", QDialogButtonBox.RejectRole)
        delete_button = buttons.addButton("Удалить запись", QDialogButtonBox.DestructiveRole)

        # Стили
        save_button.setStyleSheet("background-color: #90EE90; color: black; font-weight: bold;")
        cancel_button.setStyleSheet("background-color: #87CEFA; color: black; font-weight: bold;")
        delete_button.setStyleSheet("background-color: #FF6347; color: white; font-weight: bold;")

        layout.addRow(buttons)

        def save_changes():
            confirm = QMessageBox.question(
                self, "Подтверждение", "Сохранить изменения?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                updated_record = {
                    "vin": vin_input.text().strip(),
                    "contract": contract_input.text().strip(),
                    "reason": reason_input.toPlainText().strip()
                }
                for idx, r in enumerate(self.records):
                    if r == record:
                        self.records[idx] = updated_record
                        break
                self.save_blacklist()
                self.perform_search()
                dialog.accept()

        def delete_record():
            confirm1 = QMessageBox.question(
                self, "Удаление", "Вы точно хотите удалить запись?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm1 == QMessageBox.Yes:
                confirm2 = QMessageBox.question(
                    self, "Подтверждение удаления", "Это действие необратимо. Удалить?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm2 == QMessageBox.Yes:
                    self.records = [r for r in self.records if r != record]
                    self.save_blacklist()
                    self.perform_search()
                    dialog.accept()

        save_button.clicked.connect(save_changes)
        cancel_button.clicked.connect(dialog.reject)
        delete_button.clicked.connect(delete_record)

        dialog.setLayout(layout)
        dialog.exec_()

    def is_blacklisted(self, vin: str, contract: str) -> bool:
        vin = vin.strip().lower()
        contract = contract.strip().lower()
        for record in self.records:
            rec_vin = record.get("vin", "").lower()
            rec_contract = record.get("contract", "").lower()
            if vin and vin == rec_vin:
                return True
            if contract and contract == rec_contract:
                return True
        return False
