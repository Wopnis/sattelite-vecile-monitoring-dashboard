from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from alarms.alarm_entry_form import AlarmEntryForm
from alarms.alarm_list_view import AlarmListView


class AlarmTab(QWidget):
    def __init__(self, alarm_manager, blacklist_tab, shifts_tab):
        super().__init__()
        self.alarm_manager = alarm_manager
        self.blacklist_tab = blacklist_tab
        self.shifts_tab = shifts_tab
        self.shifts_tab.on_shift_started = self.on_shift_changed

        layout = QVBoxLayout()
        splitter = QSplitter()

        self.entry_form = AlarmEntryForm(
            alarm_manager,
            blacklist_tab,
            lambda: self.shifts_tab.current_shift_id
        )

        self.list_view = AlarmListView(
            alarm_manager,
            lambda: self.shifts_tab.current_shift_id,
            on_alarm_closed=self.on_alarm_closed,
            on_alarm_selected=self.populate_form_from_alarm
        )

        splitter.addWidget(self.entry_form)
        splitter.addWidget(self.list_view)
        splitter.setSizes([350, 450])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def on_alarm_closed(self):
        self.list_view.update_alarm_list()

    def populate_form_from_alarm(self, alarm):
        self.entry_form.brand_input.setText(alarm.get("brand", ""))
        self.entry_form.vin_input.setText(alarm.get("vin", ""))
        self.entry_form.license_input.setText(alarm.get("license", ""))
        self.entry_form.contract_input.setText(alarm.get("contract", ""))
        self.entry_form.lessee_input.setText(alarm.get("lessee", ""))
        self.entry_form.message_input.setText(alarm.get("message", ""))
        self.entry_form.comment_input.setText(alarm.get("comment", ""))
        self.entry_form.save_button.setEnabled(False)

    def on_shift_changed(self):
        print("[ALARM_TAB] Смена изменилась — обновляю список тревог")
        self.list_view.update_alarm_list()
