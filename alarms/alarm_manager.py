import json
import os

class AlarmManager:
    def __init__(self, filename="data/alarms.json"):
        self.filename = filename
        self.alarms = self.load_alarms()

    def load_alarms(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    return []
        return []

    def save_alarms(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.alarms, f, indent=2, ensure_ascii=False)

    def add_alarm(self, alarm_data, shift_id):
        alarm_data["shift_id"] = shift_id
        self.alarms.append(alarm_data)
        self.save_alarms()

    def get_alarms_for_shift(self, shift_id):
        return [a for a in self.alarms if a.get("shift_id") == shift_id]

    def get_active_alarms_for_shift(self, shift_id):
        return [a for a in self.alarms if a.get("shift_id") == shift_id and a.get("status") == "active"]
