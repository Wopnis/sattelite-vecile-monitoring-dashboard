# shifts/shift_details_dialog.py
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QMenu, QAction, QInputDialog, QMessageBox,  # noqa: F401
    QPushButton, QHBoxLayout, QLineEdit, QFileDialog, QApplication, QToolTip
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QTextDocument
from PyQt5.QtPrintSupport import QPrinter


class ShiftDetailsDialog(QDialog):
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

    def __init__(self, shift: dict, alarm_manager, parent=None):
        super().__init__(parent)
        self.shift = shift or {}
        self.alarm_manager = alarm_manager
        self.setWindowTitle("📊 Подробности смены")
        self.resize(800, 600)

        layout = QVBoxLayout()

        # заголовок
        layout.addWidget(QLabel(f"<b>Смена:</b> {self.shift.get('started_at')} → {self.shift.get('ended_at', 'в процессе')}"))

        # комментарий к смене (read-only)
        layout.addWidget(QLabel("💬 Комментарий к смене:"))
        self.comment_box = QTextEdit()
        self.comment_box.setReadOnly(True)
        self.comment_box.setFont(QFont("Segoe UI", 10))
        self.comment_box.setFixedHeight(80)
        self.comment_box.setPlainText(self.shift.get("comment", ""))
        layout.addWidget(self.comment_box)

        # тревоги
        layout.addWidget(QLabel("📋 Тревоги в смене:"))
        self.alarm_list = QListWidget()
        self.alarm_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.alarm_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.alarm_list)

        # журнал
        layout.addWidget(QLabel("🗒️ Журнал смены:"))

        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по журналу (Enter)")
        self.search_input.returnPressed.connect(self.search_in_journal)
        controls.addWidget(self.search_input)

        self.search_btn = QPushButton("Найти")
        self.search_btn.clicked.connect(self.search_in_journal)
        controls.addWidget(self.search_btn)

        self.copy_btn = QPushButton("📋 Копировать")
        self.copy_btn.clicked.connect(self.copy_journal_text)
        controls.addWidget(self.copy_btn)

        self.export_txt_btn = QPushButton("Экспорт TXT")
        self.export_txt_btn.clicked.connect(self.export_txt)
        controls.addWidget(self.export_txt_btn)

        self.export_pdf_btn = QPushButton("Экспорт PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        controls.addWidget(self.export_pdf_btn)

        layout.addLayout(controls)

        self.journal_box = QTextEdit()
        self.journal_box.setReadOnly(True)
        self.journal_box.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.journal_box)

        self.setLayout(layout)

        self.populate_alarm_list()
        self.load_journal_text()

    # ---------------- тревоги ----------------
    def populate_alarm_list(self):
        self.alarm_list.clear()
        shift_id = self.shift.get("id")
        if not self.alarm_manager:
            return
        alarms = [a for a in self.alarm_manager.alarms if a.get("shift_id") == shift_id]
        for alarm in alarms:
            item = QListWidgetItem(f"{alarm.get('vin','')} | {alarm.get('contract','')} | {alarm.get('message','')}")
            item.setData(Qt.UserRole, alarm)
            self.alarm_list.addItem(item)

    def show_context_menu(self, pos: QPoint):
        item = self.alarm_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        menu.addAction("💬 Оставить комментарий", lambda: self.add_comment(item))
        menu.addAction("🔍 Посмотреть подробности", lambda: self.show_alarm_details(item))
        menu.exec_(self.alarm_list.mapToGlobal(pos))

    def add_comment(self, item: QListWidgetItem):
        alarm = item.data(Qt.UserRole)
        existing_comment = alarm.get("comment", "")
        comment, ok = QInputDialog.getMultiLineText(self, "Комментарий", "Введите комментарий:", text=existing_comment)
        if ok:
            alarm["comment"] = comment
            if hasattr(self.alarm_manager, "save_alarms"):
                try:
                    self.alarm_manager.save_alarms()
                except Exception:
                    pass
            QMessageBox.information(self, "✅ Сохранено", "Комментарий сохранён.")

    def show_alarm_details(self, item: QListWidgetItem):
        alarm = item.data(Qt.UserRole)
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
        lines = []
        for key in ["vin", "contract", "brand", "lessee", "license", "message", "status", "timestamp", "closed_at", "comment", "shift_id"]:
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
        dlg_layout = QVBoxLayout()
        dlg_layout.addWidget(detail_box)
        dialog.setLayout(dlg_layout)
        dialog.resize(600, 450)
        dialog.exec_()

    # ---------------- журнал ----------------
    def load_journal_text(self):
        txt = self.shift.get("journal_text", "")
        self.journal_box.setPlainText(txt)
        self.highlight_journal_keywords()
        # обновим комментарий (если что-то изменилось извне)
        self.comment_box.setPlainText(self.shift.get("comment", ""))

    def search_in_journal(self):
        query = self.search_input.text().strip().lower()
        if not query:
            return
        text = self.journal_box.toPlainText().lower()
        idx = text.find(query)
        if idx == -1:
            QMessageBox.information(self, "Поиск", "Совпадений не найдено.")
            return
        cursor = self.journal_box.textCursor()
        cursor.setPosition(idx)
        cursor.setPosition(idx + len(query), QTextCursor.KeepAnchor)
        self.journal_box.setTextCursor(cursor)
        self.journal_box.setFocus()

    def copy_journal_text(self):
        text = self.journal_box.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            # показываем локальный тултип рядом с виджетом (не системный долгоживущий)
            QToolTip.showText(self.journal_box.mapToGlobal(self.journal_box.rect().topRight()), "📋 Скопировано", self.journal_box)

    def export_txt(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Сохранить журнал как TXT", "", "Текстовый файл (*.txt)")
        if not fname:
            return
        if not fname.lower().endswith(".txt"):
            fname += ".txt"
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(self.journal_box.toPlainText())
            QMessageBox.information(self, "Экспорт", "Экспорт в TXT выполнен.")
        except Exception as ex:
            QMessageBox.warning(self, "Ошибка", str(ex))

    def export_pdf(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Сохранить журнал как PDF", "", "PDF файл (*.pdf)")
        if not fname:
            return
        if not fname.lower().endswith(".pdf"):
            fname += ".pdf"
        try:
            doc = QTextDocument()
            # используем HTML для сохранения переносов/форматирования
            html = "<pre style='font-family:monospace; white-space:pre-wrap'>{}</pre>".format(
                self.journal_box.toPlainText()
            )
            doc.setHtml(html)
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fname)
            doc.print_(printer)
            QMessageBox.information(self, "Экспорт", "Экспорт в PDF выполнен.")
        except Exception as ex:
            QMessageBox.warning(self, "Ошибка", str(ex))

    def highlight_journal_keywords(self):
        doc = self.journal_box.document()
        cursor = QTextCursor(doc)

        # сброс форматирования
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()

        plain = self.journal_box.toPlainText()
        if not plain:
            return
        try:
            pattern = re.compile("(" + "|".join(self.KEYWORD_PATTERNS) + ")", re.IGNORECASE | re.UNICODE)
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


def show_shift_details_dialog(shift: dict, alarm_manager, parent=None):
    dlg = ShiftDetailsDialog(shift, alarm_manager, parent)
    dlg.exec_()
