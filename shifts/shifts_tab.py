# shifts/shifts_tab.py
import os
import json
import uuid
from datetime import datetime
import re

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QMessageBox, QMenu,
    QHBoxLayout, QLineEdit, QInputDialog, QShortcut  # noqa: F401
)
from PyQt5.QtGui import QFont, QKeySequence, QTextCursor, QTextCharFormat
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.Qt import QApplication

from utils.shift_report import generate_shift_report
from shifts.shift_details_dialog import show_shift_details_dialog


class ShiftsTab(QWidget):
    AUTO_SAVE_INTERVAL_MS = 30 * 1000  # 30 секунд

    KEYWORD_PATTERNS = [
        r"тревог", r"тревога", r"трев",
        r"демонт", r"демонтаж",
        r"выезд",
        r"рф", r"границ", r"граница",
        r"казахстан", r"грузия", r"азербайджан", r"турция",
        r"нет\s*связ",
        r"полиция",
        r"рг",
        r"изъят", r"изъятие",
        r"договор",
        r"наруш"
    ]

    def __init__(self, alarm_manager=None, on_shift_started=None):
        super().__init__()
        self.alarm_manager = alarm_manager
        self.on_shift_started = on_shift_started
        self.data_file = "shifts/shifts_data.json"
        self.shifts = self.load_shifts()
        self.active_shift = self.get_active_shift()
        self.current_shift_id = self.active_shift["id"] if self.active_shift else None

        self._editor_dirty = False
        self._last_saved_text = ""
        self._last_save_time = None

        layout = QVBoxLayout()

        self.status_label = QLabel()
        self.status_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.status_label)

        # кнопки управления сменой
        btns = QHBoxLayout()
        self.start_button = QPushButton("▶️ Начать смену")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_button.clicked.connect(self.start_shift)
        btns.addWidget(self.start_button)

        self.end_button = QPushButton("⏹️ Завершить смену")
        self.end_button.setStyleSheet("background-color: #e53935; color: white;")
        self.end_button.clicked.connect(self.end_shift)
        btns.addWidget(self.end_button)
        self.end_button.setEnabled(bool(self.active_shift))

        layout.addLayout(btns)

        # --- Журнал смены ---
        layout.addWidget(QLabel("🗒️ Журнал смены:"))
        self.journal_editor = QTextEdit()
        self.journal_editor.setFont(QFont("Arial", 11))
        self.journal_editor.setPlaceholderText("Ведите журнал смены. Автосохранение каждые 30 сек. Ctrl+S — сохранить вручную.")
        self.journal_editor.textChanged.connect(self.on_editor_text_changed)
        layout.addWidget(self.journal_editor)

        # статус сохранения (локальное уведомление)
        self.save_status = QLabel("")
        self.save_status.setStyleSheet("color: green; font-size: 10pt;")
        layout.addWidget(self.save_status)

        # таймер очистки статуса
        self._clear_status_timer = QTimer(self)
        self._clear_status_timer.setSingleShot(True)
        self._clear_status_timer.timeout.connect(lambda: self.save_status.setText(""))

        # --- История смен ---
        layout.addWidget(QLabel("📜 История смен:"))
        self.shift_list = QListWidget()
        self.shift_list.itemDoubleClicked.connect(self.show_shift_report)
        self.shift_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.shift_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.shift_list)

        self.setLayout(layout)
        self.refresh_ui()

        # быстрые клавиши
        self._save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self._save_shortcut.activated.connect(self.save_journal_text)

        QApplication.instance().installEventFilter(self)

        # автосохранение
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(self.AUTO_SAVE_INTERVAL_MS)
        self._autosave_timer.timeout.connect(self._autosave_if_needed)
        self._autosave_timer.start()

        # загрузить журнал текущей смены
        self.load_active_journal_text()

    # ------------------ Методы по сменам ------------------
    def load_shifts(self):
        """
        Загружает список смен из JSON и гарантирует наличие полей journal_text и comment.
        """
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                shifts = json.load(f)
            # гарантируем наличие journal_text и comment у каждой смены
            for s in shifts:
                if "journal_text" not in s:
                    s["journal_text"] = ""
                if "comment" not in s:
                    s["comment"] = ""
            return shifts
        except Exception:
            return []

    def save_shifts(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.shifts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Ошибка сохранения смен:", e)

    def get_active_shift(self):
        for s in self.shifts:
            if not s.get("ended_at"):
                return s
        return None

    def refresh_ui(self):
        if self.active_shift:
            self.status_label.setText(f"✅ Активная смена с {self.active_shift.get('started_at')}")
        else:
            self.status_label.setText("❌ Нет активной смены")
        self.shift_list.clear()
        for s in sorted(self.shifts, key=lambda x: x.get("started_at", ""), reverse=True):
            item_text = f"{s.get('started_at')} → {s.get('ended_at','в процессе')}"
            # если есть комментарий, пометим это в списке (необязательно, можно убрать)
            if s.get("comment"):
                item_text += "  ✎"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, s)
            self.shift_list.addItem(item)

    def start_shift(self):
        if self.active_shift:
            QMessageBox.warning(self, "Ошибка", "Смена уже идёт.")
            return
        new_shift = {
            "id": str(uuid.uuid4()),
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ended_at": None,
            "journal_text": "",
            "comment": ""
        }
        self.shifts.append(new_shift)
        self.active_shift = new_shift
        self.current_shift_id = new_shift["id"]
        self.save_shifts()
        self.refresh_ui()
        self.journal_editor.clear()
        if self.on_shift_started:
            self.on_shift_started()

    def end_shift(self):
        if not self.active_shift:
            return
        self.active_shift["ended_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_shifts()
        self.active_shift = None
        self.current_shift_id = None
        self.refresh_ui()
        self.journal_editor.clear()

    def show_shift_report(self, item):
        shift = item.data(Qt.UserRole)
        if not shift:
            return
        # generate_shift_report ожидает один аргумент (shift)
        generate_shift_report(shift)

    def show_context_menu(self, pos: QPoint):
        item = self.shift_list.itemAt(pos)
        if not item:
            return
        shift = item.data(Qt.UserRole)
        menu = QMenu(self)
        menu.addAction("💬 Оставить комментарий", lambda: self.add_comment(shift))
        menu.addAction("🔍 Посмотреть подробности", lambda: self.show_shift_details(shift))
        menu.exec_(self.shift_list.mapToGlobal(pos))

    def add_comment(self, shift):
        """
        Обновляем комментарий у смены: ищем её по id в self.shifts чтобы гарантированно обновить основную структуру.
        """
        comment_text, ok = QInputDialog.getMultiLineText(self, "Комментарий к смене", "Введите комментарий:", text=shift.get("comment", ""))
        if not ok:
            return

        # попытка найти реальную смену в self.shifts по id и обновить её
        found = False
        shift_id = shift.get("id")
        if shift_id:
            for s in self.shifts:
                if s.get("id") == shift_id:
                    s["comment"] = comment_text
                    found = True
                    break
        if not found:
            # fallback: обновляем объект, который передали
            shift["comment"] = comment_text

        self.save_shifts()
        self.refresh_ui()
        QMessageBox.information(self, "✅ Сохранено", "Комментарий сохранён.")

    def show_shift_details(self, shift):
        # берём свежую версию смены (на случай, если были изменения в self.shifts)
        fresh = next((s for s in self.shifts if s.get("id") == shift.get("id")), shift)
        show_shift_details_dialog(fresh, self.alarm_manager, self)

    # ------------------ Методы по журналу ------------------
    def load_active_journal_text(self):
        if not self.active_shift:
            self.journal_editor.clear()
            return
        text = self.active_shift.get("journal_text", "")
        self.journal_editor.setPlainText(text)

    def on_editor_text_changed(self):
        self._editor_dirty = True

    def save_journal_text(self):
        if not self.active_shift:
            return
        txt = self.journal_editor.toPlainText()
        # обновляем в self.shifts
        shift_id = self.active_shift.get("id") if self.active_shift else None
        if shift_id:
            for s in self.shifts:
                if s.get("id") == shift_id:
                    s["journal_text"] = txt
                    break
        else:
            # fallback
            self.active_shift["journal_text"] = txt

        self.save_shifts()
        self._editor_dirty = False
        self._last_saved_text = txt
        self._last_save_time = datetime.now()

        # показываем статус
        self.save_status.setText(f"✅ Сохранено: {self._last_save_time.strftime('%H:%M:%S')}")
        self._clear_status_timer.start(3000)  # очистка через 3 сек

        self.highlight_keywords()

    def _autosave_if_needed(self):
        if self._editor_dirty:
            self.save_journal_text()

    def highlight_keywords(self):
        doc = self.journal_editor.document()
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()

        plain = self.journal_editor.toPlainText()
        if not plain:
            return
        joined = "(" + "|".join(self.KEYWORD_PATTERNS) + ")"
        try:
            pattern = re.compile(joined, re.IGNORECASE | re.UNICODE)
        except re.error:
            return
        for match in pattern.finditer(plain):
            start, end = match.span()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            fmt = QTextCharFormat()
            fmt.setFontWeight(700)
            fmt.setBackground(Qt.yellow)
            cursor.mergeCharFormat(fmt)
            cursor.clearSelection()
