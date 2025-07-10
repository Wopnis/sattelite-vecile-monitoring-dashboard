from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit,
    QTextEdit, QPushButton, QMessageBox, QHBoxLayout
)
from datetime import datetime


class AlarmEntryForm(QWidget):
    def __init__(self, alarm_manager, blacklist_tab, get_shift_id):
        super().__init__()
        self.alarm_manager = alarm_manager
        self.blacklist_tab = blacklist_tab
        self.get_shift_id = get_shift_id
        self.on_alarm_added = None

        layout = QFormLayout()

        self.brand_input = QLineEdit()
        self.vin_input = QLineEdit()
        self.license_input = QLineEdit()
        self.contract_input = QLineEdit()
        self.lessee_input = QLineEdit()
        self.message_input = QTextEdit()
        self.comment_input = QTextEdit()

        layout.addRow("Марка ТС*:", self.brand_input)
        layout.addRow("VIN*:", self.vin_input)
        layout.addRow("Госномер:", self.license_input)
        layout.addRow("Договор*:", self.contract_input)
        layout.addRow("Лизингополучатель:", self.lessee_input)
        layout.addRow("Сообщение*:", self.message_input)
        layout.addRow("Комментарий:", self.comment_input)

        # Кнопки
        self.save_button = QPushButton("Сохранить тревогу")
        self.save_button.clicked.connect(self.save_alarm)

        self.clear_button = QPushButton("Очистить форму")
        self.clear_button.clicked.connect(self.clear_form)

        button_row = QHBoxLayout()
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.clear_button)
        layout.addRow(button_row)

        self.setLayout(layout)

    def save_alarm(self):
        brand = self.brand_input.text().strip()
        vin = self.vin_input.text().strip()
        license_plate = self.license_input.text().strip()
        contract = self.contract_input.text().strip()
        lessee = self.lessee_input.text().strip()
        message = self.message_input.toPlainText().strip()
        comment = self.comment_input.toPlainText().strip()

        # Проверка обязательных полей
        if not all([brand, vin, contract, message]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля (*).")
            return

        # ✅ Проверка чёрного списка
        if self.blacklist_tab and self.blacklist_tab.is_blacklisted(vin, contract):
            QMessageBox.warning(self, "Внимание", "VIN или договор присутствуют в чёрном списке!")
            return

        # Проверка на дубликат активной тревоги
        for alarm in self.alarm_manager.alarms:
            if (
                alarm.get("vin") == vin
                and alarm.get("contract") == contract
                and alarm.get("status") == "active"
            ):
                QMessageBox.warning(self, "Дубликат", "Активная тревога с таким VIN и договором уже существует.")
                return

        shift_id = self.get_shift_id()
        if not shift_id:
            QMessageBox.warning(self, "Нет активной смены", "Перед созданием тревоги начните смену.")
            return

        alarm_data = {
            "brand": brand,
            "vin": vin,
            "license": license_plate,
            "contract": contract,
            "lessee": lessee,
            "message": message,
            "comment": comment,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active",
        }

        self.alarm_manager.add_alarm(alarm_data, shift_id)

        if self.on_alarm_added:
            self.on_alarm_added()

        self.save_button.setEnabled(False)

    def clear_form(self):
        print("[FORM] Очистка формы пользователя")
        self.brand_input.clear()
        self.vin_input.clear()
        self.license_input.clear()
        self.contract_input.clear()
        self.lessee_input.clear()
        self.message_input.clear()
        self.comment_input.clear()
        self.save_button.setEnabled(True)

        if self.on_alarm_added:
            self.on_alarm_added()
