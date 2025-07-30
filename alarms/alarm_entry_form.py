from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit,
    QTextEdit, QPushButton, QMessageBox, QHBoxLayout
)
# from PyQt5.QtGui import QIcon
from datetime import datetime


class AlarmEntryForm(QWidget):
    def __init__(self, alarm_manager, blacklist_tab, get_shift_id):
        super().__init__()
        self.alarm_manager = alarm_manager
        self.blacklist_tab = blacklist_tab
        self.get_shift_id = get_shift_id
        self.on_alarm_added = None

        layout = QFormLayout()
        
        # Стилизация формы
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                color: #333;
                font-weight: bold;
            }
            QPushButton {
                border-radius: 4px;
                padding: 6px 12px;
            }
        """)

        self.setStyleSheet("""
            QWidget {
                background-color: #F9FAFC;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #D0D0D0;
                padding: 4px;
                background-color: #FFFFFF;
            }
            QPushButton {
                padding: 6px 12px;
                font-weight: bold;
            }
        """)

        self.brand_input = QLineEdit()
        self.vin_input = QLineEdit()
        self.license_input = QLineEdit()
        self.contract_input = QLineEdit()
        self.lessee_input = QLineEdit()
        self.message_input = QTextEdit()
        self.comment_input = QTextEdit()

        layout.addRow("🚗 Марка ТС*:", self.brand_input)
        layout.addRow("🔑 VIN*:", self.vin_input)
        layout.addRow("🚘 Госномер:", self.license_input)
        layout.addRow("📄 Договор*:", self.contract_input)
        layout.addRow("👤 Лизингополучатель:", self.lessee_input)
        layout.addRow("📢 Сообщение*:", self.message_input)
        layout.addRow("📝 Комментарий:", self.comment_input)

        # Кнопки
        self.save_button = QPushButton("💾 Сохранить тревогу")
        self.save_button.clicked.connect(self.save_alarm)

        self.clear_button = QPushButton("🧹 Очистить форму")
        self.clear_button.clicked.connect(self.clear_form)
        
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #eeeeee;
            }
        """)

        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #FF7043;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)


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

        if not all([brand, vin, contract, message]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля (*).")
            return

        if self.blacklist_tab and self.blacklist_tab.is_blacklisted(vin, contract):
            warning_box = QMessageBox(self)
            warning_box.setWindowTitle("⚠️ Внимание")
            warning_box.setText("VIN или договор присутствуют в чёрном списке!")
            warning_box.setIcon(QMessageBox.Warning)
            warning_box.setStyleSheet("""
                QMessageBox {
                    background-color: #FFEBEE;
                    color: #C62828;
                }
                QPushButton {
                    background-color: #C62828;
                    color: white;
                }
            """)


            warning_box.exec_()

        for alarm in self.alarm_manager.alarms:
            if (
                alarm.get("vin") == vin and
                alarm.get("contract") == contract and
                alarm.get("status") == "active"
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
