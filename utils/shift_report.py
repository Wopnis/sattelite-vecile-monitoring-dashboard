# utils/shift_report.py

from alarms.alarm_manager import AlarmManager

def generate_shift_report(shift_id: str) -> str:
    """
    Возвращает текстовый отчёт по тревогам в указанной смене.
    """
    alarm_manager = AlarmManager()
    closed = 0
    open_ = 0
    total = 0

    for alarm in alarm_manager.alarms:
        if alarm.get("shift_id") == shift_id:
            total += 1
            if alarm.get("status") == "closed":
                closed += 1
            else:
                open_ += 1

    return (
        f"📊 Отчёт по смене\n\n"
        f"🆔 ID смены: {shift_id}\n\n"
        f"Всего тревог: {total}\n"
        f"🔴 Закрытых тревог: {closed}\n"
        f"🟡 Открытых тревог: {open_}"
    )
