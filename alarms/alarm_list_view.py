from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QCheckBox, QPushButton, QDialog, QLineEdit, QTextEdit,
    QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from datetime import datetime


class AlarmListView(QWidget):
    def __init__(self, alarm_manager, get_shift_id, on_alarm_closed=None, on_alarm_selected=None):
        super().__init__()
        self.alarm_manager = alarm_manager
        self.get_shift_id = get_shift_id
        self.on_alarm_closed = on_alarm_closed
        self.on_alarm_selected = on_alarm_selected

        layout = QVBoxLayout()

        self.active_only_checkbox = QCheckBox("Показать только активные тревоги")
        self.active_only_checkbox.setChecked(False)
        self.active_only_checkbox.stateChanged.connect(self.update_alarm_list)
        layout.addWidget(self.active_only_checkbox)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.handle_double_click)
        self.list_widget.itemPressed.connect(self.handle_right_click)
        layout.addWidget(self.list_widget)

        self.close_button = QPushButton("Закрыть выбранную тревогу")
        self.close_button.clicked.connect(self.close_selected_alarm)
        layout.addWidget(self.close_button)

        self.setLayout(layout)
        self.update_alarm_list()

    def update_alarm_list(self):
        self.list_widget.clear()
        shift_id = self.get_shift_id()
        if not shift_id:
            return

        show_only_active = self.active_only_checkbox.isChecked()

        filtered_alarms = [
            alarm for alarm in self.alarm_manager.alarms
            if alarm.get("shift_id") == shift_id and
            (not show_only_active or alarm.get("status") == "active")
        ]

        for alarm in filtered_alarms:
            vin = alarm.get("vin", "")
            contract = alarm.get("contract", "")
            brand = alarm.get("brand", "")
            message = alarm.get("message", "")
            opened = alarm.get("timestamp", "")
            closed = alarm.get("closed_at", "—") if alarm.get("status") == "closed" else "—"

            item_text = (
                f"{vin} | {contract} | {brand} | {message} | "
                f"Открыта: {opened} | Закрыта: {closed}"
            )
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, alarm)

            # Подсветка по статусу
            if alarm.get("status") == "active":
                item.setForeground(QColor("red"))
            else:
                item.setForeground(QColor("gray"))

            self.list_widget.addItem(item)


    def handle_double_click(self, item):
        alarm = item.data(Qt.UserRole)
        if self.on_alarm_selected:
            self.on_alarm_selected(alarm)

    def handle_right_click(self, item):
        if QApplication.mouseButtons() == Qt.RightButton:
            alarm = item.data(Qt.UserRole)
            if alarm.get("status") == "closed":
                QMessageBox.information(self, "Тревога закрыта", "Эту тревогу редактировать нельзя.")
                return
            self.open_edit_dialog(alarm)

    def open_edit_dialog(self, alarm):
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование тревоги")

        form = QFormLayout()
        brand_input = QLineEdit(alarm.get("brand", ""))
        vin_input = QLineEdit(alarm.get("vin", ""))
        license_input = QLineEdit(alarm.get("license", ""))
        contract_input = QLineEdit(alarm.get("contract", ""))
        lessee_input = QLineEdit(alarm.get("lessee", ""))
        message_input = QTextEdit(alarm.get("message", ""))
        comment_input = QTextEdit(alarm.get("comment", ""))

        form.addRow("Марка ТС:", brand_input)
        form.addRow("VIN:", vin_input)
        form.addRow("Госномер:", license_input)
        form.addRow("Договор:", contract_input)
        form.addRow("Лизингополучатель:", lessee_input)
        form.addRow("Сообщение:", message_input)
        form.addRow("Комментарий:", comment_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        dialog.setLayout(form)

        if dialog.exec_() == QDialog.Accepted:
            for original in self.alarm_manager.alarms:
                if (
                    original.get("vin") == alarm.get("vin") and
                    original.get("contract") == alarm.get("contract") and
                    original.get("timestamp") == alarm.get("timestamp")
                ):
                    original["brand"] = brand_input.text().strip()
                    original["vin"] = vin_input.text().strip()
                    original["license"] = license_input.text().strip()
                    original["contract"] = contract_input.text().strip()
                    original["lessee"] = lessee_input.text().strip()
                    original["message"] = message_input.toPlainText().strip()
                    original["comment"] = comment_input.toPlainText().strip()
            self.alarm_manager.save_alarms()
            self.update_alarm_list()

    def close_selected_alarm(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.information(self, "Закрытие тревоги", "Выберите тревогу в списке.")
            return

        alarm = item.data(Qt.UserRole)
        if alarm.get("status") == "closed":
            QMessageBox.information(self, "Уже закрыта", "Эта тревога уже закрыта.")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы точно хотите закрыть эту тревогу?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            closed = False
            for original in self.alarm_manager.alarms:
                if (
                    original.get("vin") == alarm.get("vin") and
                    original.get("contract") == alarm.get("contract") and
                    original.get("timestamp") == alarm.get("timestamp")
                ):
                    if original["status"] != "closed":
                        original["status"] = "closed"
                        original["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        closed = True

            if closed:
                self.alarm_manager.save_alarms()
                self.update_alarm_list()
                if self.on_alarm_closed:
                    self.on_alarm_closed()
