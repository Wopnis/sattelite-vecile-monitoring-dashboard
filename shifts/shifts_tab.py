import os
import json
import uuid
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QMessageBox, QDialog,
    QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ShiftsTab(QWidget):
    def __init__(self, alarm_manager=None):
        super().__init__()
        self.alarm_manager = alarm_manager
        self.data_file = "shifts/shifts_data.json"
        self.shifts = self.load_shifts()
        self.active_shift = self.get_active_shift()
        self.current_shift_id = self.active_shift["id"] if self.active_shift else None

        layout = QVBoxLayout()

        self.status_label = QLabel()
        self.start_button = QPushButton("Начать смену")
        self.end_button = QPushButton("Завершить смену")
        self.end_button.setEnabled(bool(self.active_shift))

        self.start_button.clicked.connect(self.start_shift)
        self.end_button.clicked.connect(self.end_shift)

        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.end_button)

        layout.addWidget(QLabel("Комментарий:"))
        self.comment_input = QTextEdit()
        layout.addWidget(self.comment_input)

        layout.addWidget(QLabel("История смен:"))
        self.shift_list = QListWidget()
        self.shift_list.itemDoubleClicked.connect(self.show_shift_details)
        layout.addWidget(self.shift_list)

        self.setLayout(layout)
        self.refresh_ui()

    def load_shifts(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_shifts(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.shifts, f, indent=2, ensure_ascii=False)

    def get_active_shift(self):
        for shift in self.shifts:
            if not shift.get("ended_at"):
                return shift
        return None

    def start_shift(self):
        if self.active_shift:
            QMessageBox.warning(self, "Ошибка", "Смена уже начата.")
            return

        new_shift_id = str(uuid.uuid4())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_shift = {
            "id": new_shift_id,
            "started_at": now,
            "ended_at": None,
            "comment": ""
        }
        self.shifts.append(new_shift)
        self.active_shift = new_shift
        self.current_shift_id = new_shift_id
        # Перенос активных тревог в новую смену
        active_old = [
            alarm for alarm in self.alarm_manager.alarms
            if alarm.get("status") == "active"
        ]

        for alarm in active_old:
            copied = alarm.copy()
            copied["shift_id"] = new_shift_id
            self.alarm_manager.alarms.append(copied)

        self.alarm_manager.save_alarms()
        self.save_shifts()
        print(f"[SHIFT] Новая смена начата: {new_shift_id}")

        if self.on_shift_started:
            self.on_shift_started()  # ✅ уведомляем AlarmTab

        self.refresh_ui()


    def end_shift(self):
        if not self.active_shift:
            QMessageBox.warning(self, "Ошибка", "Смена не начата.")
            return

        comment = self.comment_input.toPlainText().strip()
        self.active_shift["ended_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.active_shift["comment"] = comment
        self.active_shift = None
        self.current_shift_id = None
        self.comment_input.clear()
        self.save_shifts()
        self.refresh_ui()

    def refresh_ui(self):
        if self.active_shift:
            self.status_label.setText(f"<b>Текущая смена начата:</b> {self.active_shift['started_at']}")
            self.end_button.setEnabled(True)
            self.start_button.setEnabled(False)
        else:
            self.status_label.setText("Нет активной смены.")
            self.start_button.setEnabled(True)
            self.end_button.setEnabled(False)

        self.shift_list.clear()
        for shift in reversed(self.shifts):
            text = f"{shift['started_at']} → {shift.get('ended_at', 'в процессе')}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, shift)
            self.shift_list.addItem(item)

    def show_shift_details(self, item):
        shift = item.data(Qt.UserRole)
        dialog = QDialog(self)
        dialog.setWindowTitle("Детали смены")

        layout = QVBoxLayout()
        text = QTextEdit()
        text.setReadOnly(True)
        text.setFont(QFont("Courier", 10))

        text.setText(
            f"ID смены: {shift.get('id')}\n"
            f"Начало: {shift.get('started_at')}\n"
            f"Окончание: {shift.get('ended_at', '-')}\n\n"
            f"Комментарий:\n{shift.get('comment', '')}"
        )
        layout.addWidget(text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()
