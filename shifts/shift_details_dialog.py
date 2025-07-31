# import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QMenu, QAction, QInputDialog, QMessageBox, QApplication  # noqa: F401
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont


class ShiftDetailsDialog(QDialog):
    def __init__(self, shift: dict, alarm_manager, parent=None):
        super().__init__(parent)
        self.shift = shift
        self.alarm_manager = alarm_manager
        self.setWindowTitle("📊 Подробности смены")

        self.setMinimumSize(700, 500)

        layout = QVBoxLayout()

        # Заголовок
        layout.addWidget(QLabel(f"<b>Смена:</b> {shift.get('started_at')} → {shift.get('ended_at', 'в процессе')}"))

        # Список тревог
        self.alarm_list = QListWidget()
        self.alarm_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.alarm_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(QLabel("📋 Тревоги в смене:"))
        layout.addWidget(self.alarm_list)

        self.populate_alarm_list()

        self.setLayout(layout)

    def populate_alarm_list(self):
        self.alarm_list.clear()
        shift_id = self.shift.get("id")
        alarms = [a for a in self.alarm_manager.alarms if a.get("shift_id") == shift_id]
        for alarm in alarms:
            item = QListWidgetItem(f"{alarm.get('vin', '')} | {alarm.get('contract', '')} | {alarm.get('message', '')}")
            item.setData(Qt.UserRole, alarm)
            self.alarm_list.addItem(item)

    def show_context_menu(self, pos: QPoint):
        item = self.alarm_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        comment_action = QAction("💬 Оставить комментарий", self)
        comment_action.triggered.connect(lambda: self.add_comment(item))
        menu.addAction(comment_action)

        details_action = QAction("🔍 Посмотреть подробности", self)
        details_action.triggered.connect(lambda: self.show_alarm_details(item))
        menu.addAction(details_action)

        menu.exec_(self.alarm_list.mapToGlobal(pos))

    def add_comment(self, item: QListWidgetItem):
        alarm = item.data(Qt.UserRole)
        existing_comment = alarm.get("comment", "")
        comment, ok = QInputDialog.getMultiLineText(
            self,
            "Комментарий",
            "Введите комментарий:",
            text=existing_comment
        )
        if ok:
            alarm["comment"] = comment
            self.alarm_manager.save_alarms()
            QMessageBox.information(self, "✅ Сохранено", "Комментарий сохранён.")

    def show_alarm_details(self, item: QListWidgetItem):
        alarm = item.data(Qt.UserRole)

        # Расшифровка полей
        field_labels = {
            "vin": "🚗 VIN-код",
            "contract": "📄 Договор",
            "brand": "🏷️ Марка",
            "lessee": "👤 Лизингополучатель",
            "license": "📛 Госномер",
            "message": "📢 Тревога",
            "status": "⚠️ Статус",
            "timestamp": "🕒 Время активации",
            "closed_at": "🛑 Время закрытия",
            "comment": "💬 Комментарий",
            "shift_id": "🧾 ID смены",
        }

        # Формируем читабельный текст
        lines = []
        for key in [
            "vin", "contract", "brand", "lessee", "license",
            "message", "status", "timestamp", "closed_at", "comment", "shift_id"
        ]:
            label = field_labels.get(key, key)
            value = alarm.get(key, "—")
            lines.append(f"<b>{label}:</b> {value}")

        html = "<br><br>".join(lines)

        detail_box = QTextEdit()
        detail_box.setReadOnly(True)
        detail_box.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        detail_box.setHtml(html)
        detail_box.setFont(QFont("Segoe UI", 10))

        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 Подробности тревоги")
        layout = QVBoxLayout()
        layout.addWidget(detail_box)
        dialog.setLayout(layout)
        dialog.resize(600, 450)
        dialog.exec_()



def show_shift_details_dialog(shift: dict, alarm_manager, parent=None):
    dialog = ShiftDetailsDialog(shift, alarm_manager, parent)
    dialog.exec_()
