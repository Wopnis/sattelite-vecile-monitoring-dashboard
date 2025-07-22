from PyQt5.QtWidgets import QMainWindow, QTabWidget, QDesktopWidget
from PyQt5.QtGui import QIcon

# Модули приложения
from alarms.alarm_manager import AlarmManager
from alarms.alarm_tab import AlarmTab
from alarms.alarm_search_tab import AlarmSearchTab
from messages.message_tab import MessageTab
from notes.notes_tab import NotesTab
from blacklist.blacklist_tab import BlacklistTab
from shifts.shifts_tab import ShiftsTab
from letters.letters_tab import LettersTab  # ✅ Новый модуль
from reminders.reminders_tab import RemindersTab  # ✅ Новая вкладка


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icons/monitoring.ico"))
        self.setWindowTitle("Дашборд оператора мониторинга")
        self.setWindowIcon(QIcon("icons/icon.png"))

        # ✅ Стартовый размер и минимальный размер
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        # ✅ Центровка окна
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # 💾 Менеджер тревог
        self.alarm_manager = AlarmManager()

        # 🧩 Центральные вкладки
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 🔧 Вкладки
        self.blacklist_tab = BlacklistTab()
        self.shifts_tab = ShiftsTab(self.alarm_manager)
        self.alarm_tab = AlarmTab(self.alarm_manager, self.blacklist_tab, self.shifts_tab)
        self.alarm_tab.entry_form.on_alarm_added = self.on_alarm_added

        self.message_tab = MessageTab(self.get_last_alarm)
        self.search_tab = AlarmSearchTab(self.alarm_manager)
        self.notes_tab = NotesTab()
        self.letters_tab = LettersTab()  # ✅ Новая вкладка "Письма"
        self.reminders_tab = RemindersTab()  # ✅ Вкладка напоминаний


        # 📑 Добавление вкладок
        self.tabs.addTab(self.alarm_tab, "Тревоги")
        self.tabs.addTab(self.message_tab, "Сообщения")
        self.tabs.addTab(self.search_tab, "Поиск")
        self.tabs.addTab(self.notes_tab, "Заметки")
        self.tabs.addTab(self.letters_tab, "Письма")  # ✅ Добавлена сюда
        self.tabs.addTab(self.reminders_tab, "Напоминания")  # ✅ Новая вкладка
        self.tabs.addTab(self.shifts_tab, "Смены")
        self.tabs.addTab(self.blacklist_tab, "Чёрный список")

        # ✅ Обновить тревоги текущей смены при запуске
        self.alarm_tab.list_view.update_alarm_list()

    def get_last_alarm(self):
        if self.alarm_manager.alarms:
            return self.alarm_manager.alarms[-1]
        return None

    def on_alarm_added(self):
        alarm = self.get_last_alarm()
        self.alarm_tab.list_view.update_alarm_list()
        if alarm:
            self.message_tab.update_alarm_info(alarm)
