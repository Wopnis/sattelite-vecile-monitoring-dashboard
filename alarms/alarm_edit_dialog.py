from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QPushButton, QMessageBox
)

class AlarmEditDialog(QDialog):
    def __init__(self, alarm, on_save):
        super().__init__()
        self.setWindowTitle("Редактировать тревогу")
        self.alarm = alarm.copy()
        self.on_save = on_save

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.brand_input = QLineEdit(self.alarm.get("brand", ""))
        self.vin_input = QLineEdit(self.alarm.get("vin", ""))
        self.license_input = QLineEdit(self.alarm.get("license", ""))
        self.contract_input = QLineEdit(self.alarm.get("contract", ""))
        self.lessee_input = QLineEdit(self.alarm.get("lessee", ""))
        self.message_input = QTextEdit(self.alarm.get("message", ""))
        self.comment_input = QTextEdit(self.alarm.get("comment", ""))

        form_layout.addRow("Марка:", self.brand_input)
        form_layout.addRow("VIN:", self.vin_input)
        form_layout.addRow("Гос. номер:", self.license_input)
        form_layout.addRow("Договор:", self.contract_input)
        form_layout.addRow("Лизингополучатель:", self.lessee_input)
        form_layout.addRow("Содержание сигнала:", self.message_input)
        form_layout.addRow("Комментарий:", self.comment_input)

        layout.addLayout(form_layout)

        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save(self):
        if not self.brand_input.text() or not self.vin_input.text() or not self.contract_input.text():
            QMessageBox.warning(self, "Ошибка", "Поля Марка, VIN и Договор обязательны.")
            return

        updated_alarm = {
            "brand": self.brand_input.text(),
            "vin": self.vin_input.text(),
            "license": self.license_input.text(),
            "contract": self.contract_input.text(),
            "lessee": self.lessee_input.text(),
            "message": self.message_input.toPlainText(),
            "comment": self.comment_input.toPlainText()
        }

        self.on_save(updated_alarm)
        self.accept()
