import os
import json
import uuid
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from utils.shift_report import generate_shift_report


class ShiftsTab(QWidget):
    def __init__(self, alarm_manager=None, on_shift_started=None):
        super().__init__()
        self.alarm_manager = alarm_manager
        self.on_shift_started = on_shift_started
        self.data_file = "shifts/shifts_data.json"
        self.shifts = self.load_shifts()
        self.active_shift = self.get_active_shift()
        self.current_shift_id = self.active_shift["id"] if self.active_shift else None

        layout = QVBoxLayout()
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-size: 13px;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
            QPushButton {
                padding: 8px 12px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)

        self.status_label = QLabel()
        self.status_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.status_label)

        # 🔹 Кнопка начала смены
        self.start_button = QPushButton("▶️ Начать смену")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_button.clicked.connect(self.start_shift)
        layout.addWidget(self.start_button)

        # 🔹 Кнопка завершения смены
        self.end_button = QPushButton("⏹️ Завершить смену")
        self.end_button.setStyleSheet("background-color: #e53935; color: white;")
        self.end_button.clicked.connect(self.end_shift)
        layout.addWidget(self.end_button)
        self.end_button.setEnabled(bool(self.active_shift))

        # 🔹 Комментарий к смене
        layout.addWidget(QLabel("📝 Комментарий:"))
        self.comment_input = QTextEdit()
        self.comment_input.setFont(QFont("Arial", 10))
        layout.addWidget(self.comment_input)

        # 🔹 История смен
        layout.addWidget(QLabel("📜 История смен:"))
        self.shift_list = QListWidget()
        self.shift_list.itemDoubleClicked.connect(self.show_shift_report)
        layout.addWidget(self.shift_list)

        self.setLayout(layout)
        self.refresh_ui()

    def load_shifts(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    return [entry for entry in data if isinstance(entry, dict)]
                except json.JSONDecodeError:
                    return []
        return []

    def save_shifts(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.shifts, f, indent=2, ensure_ascii=False)

    def get_active_shift(self):
        for shift in self.shifts:
            if isinstance(shift, dict) and not shift.get("ended_at"):
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

        # 💾 Присваиваем ID текущим активным тревогам
        if self.alarm_manager:
            active_alarms = [
                alarm for alarm in self.alarm_manager.alarms
                if alarm.get("status") == "active"
            ]
            for alarm in active_alarms:
                copied = alarm.copy()
                copied["shift_id"] = new_shift_id
                self.alarm_manager.alarms.append(copied)
            self.alarm_manager.save_alarms()

        self.save_shifts()
        print(f"[SHIFT] Новая смена начата: {new_shift_id}")

        if self.on_shift_started:
            self.on_shift_started()

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
            self.status_label.setText(
                f"<b>🟢 Текущая смена начата:</b> {self.active_shift['started_at']}"
            )
            self.start_button.setEnabled(False)
            self.end_button.setEnabled(True)
        else:
            self.status_label.setText("⚪ Нет активной смены.")
            self.start_button.setEnabled(True)
            self.end_button.setEnabled(False)

        self.shift_list.clear()
        for shift in reversed(self.shifts):
            if isinstance(shift, dict):
                text = f"{shift['started_at']} → {shift.get('ended_at', 'в процессе')}"
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, shift)
                self.shift_list.addItem(item)

    def show_shift_report(self, item):
        shift = item.data(Qt.UserRole)
        shift_id = shift.get("id")
        report = generate_shift_report(shift_id)

        comment = shift.get("comment", "").strip()
        comment_text = f"\n📝 Комментарий к смене:\n{comment}" if comment else "\n📝 Комментарий: (отсутствует)"

        full_report = f"{report}\n{comment_text}"

        QMessageBox.information(self, "📋 Отчёт по смене", full_report)
