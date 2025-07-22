import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QDateTimeEdit, QDialog,
    QTextEdit, QDialogButtonBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtMultimedia import QSound

from utils.telegram_utils import send_telegram_message


class RemindersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.data_file = "reminders/reminders_data.json"
        self.reminders = self.load_reminders()
        self.sound = None  # 🔉 Хранение текущего звука

        layout = QVBoxLayout()

        # 🔹 Форма добавления
        self.text_input = QLineEdit()
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setDateTime(QDateTime.currentDateTime())
        self.enabled_checkbox = QCheckBox("Активно")
        self.enabled_checkbox.setChecked(True)
        self.telegram_checkbox = QCheckBox("Оповещение в Telegram")
        self.telegram_checkbox.setChecked(True)

        add_button = QPushButton("Добавить напоминание")
        add_button.clicked.connect(self.add_reminder)

        layout.addWidget(QLabel("Текст напоминания:"))
        layout.addWidget(self.text_input)
        layout.addWidget(QLabel("Дата и время:"))
        layout.addWidget(self.datetime_input)
        layout.addWidget(self.enabled_checkbox)
        layout.addWidget(self.telegram_checkbox)
        layout.addWidget(add_button)

        # 🔹 Список напоминаний
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.view_reminder)
        layout.addWidget(self.list_widget)

        # 🔹 Удаление
        del_button = QPushButton("Удалить выбранное")
        del_button.clicked.connect(self.delete_reminder)
        layout.addWidget(del_button)

        self.setLayout(layout)
        self.refresh_list()

        # 🔔 Таймер на проверку напоминаний
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(10_000)  # каждые 10 секунд

    def load_reminders(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_reminders(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.reminders, f, indent=2, ensure_ascii=False)

    def add_reminder(self):
        text = self.text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Текст не может быть пустым.")
            return
        timestamp = self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.reminders.append({
            "text": text,
            "time": timestamp,
            "notified": False,
            "enabled": self.enabled_checkbox.isChecked(),
            "telegram": self.telegram_checkbox.isChecked()
        })
        self.text_input.clear()
        self.save_reminders()
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for r in sorted(self.reminders, key=lambda x: x["time"]):
            status = "⏰" if r.get("enabled") else "❌"
            if r.get("notified"):
                status = "✅"
            tg_mark = "📲 " if r.get("telegram") else ""
            item = QListWidgetItem(f"{status} {tg_mark}{r['time']} — {r['text']}")
            item.setData(Qt.UserRole, r)
            self.list_widget.addItem(item)

    def delete_reminder(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        reminder = item.data(Qt.UserRole)
        confirm = QMessageBox.question(self, "Удалить?", f"Удалить: {reminder['text']}?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.reminders.remove(reminder)
            self.save_reminders()
            self.refresh_list()

    def view_reminder(self, item):
        reminder = item.data(Qt.UserRole)
        dialog = QDialog(self)
        dialog.setWindowTitle("Напоминание")
        layout = QVBoxLayout()
        msg = QTextEdit()
        msg.setReadOnly(True)
        msg.setText(f"🕒 Время: {reminder['time']}\n\n{reminder['text']}")
        layout.addWidget(msg)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.resize(400, 200)
        dialog.exec_()

    def check_reminders(self):
        now = datetime.now()
        updated = False
        for reminder in self.reminders:
            if not reminder.get("enabled") or reminder.get("notified"):
                continue
            remind_time = datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M:%S")
            if now >= remind_time:
                reminder["notified"] = True
                updated = True
                self.trigger_reminder(reminder)
        if updated:
            self.save_reminders()
            self.refresh_list()

    def trigger_reminder(self, reminder):
        # 🔊 Зацикленный звук
        self.sound = QSound("reminders/notify_reminder.wav")
        self.sound.setLoops(QSound.Infinite)
        self.sound.play()

        # 💬 Всплывающее окно
        dialog = QMessageBox(self)
        dialog.setWindowTitle("🔔 Напоминание")
        dialog.setText(reminder["text"])
        dialog.setIcon(QMessageBox.Information)
        dialog.exec_()

        # ⏹️ Остановить звук
        if self.sound:
            self.sound.stop()

        # ✉️ Telegram
        if reminder.get("telegram"):
            send_telegram_message(f"🔔 Напоминание: {reminder['text']}")
