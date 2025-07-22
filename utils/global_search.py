import json
import os

def global_search(keyword):
    keyword = keyword.lower()
    results = []

    # 🔍 Тревоги
    if os.path.exists("data/alarms.json"):
        with open("data/alarms.json", "r", encoding="utf-8") as f:
            alarms = json.load(f)
            for alarm in alarms:
                combined = " ".join([
                    alarm.get("vin", ""), alarm.get("contract", ""),
                    alarm.get("brand", ""), alarm.get("license", ""),
                    alarm.get("message", ""), alarm.get("comment", ""),
                    alarm.get("lessee", "")
                ]).lower()
                if keyword in combined:
                    timestamp = alarm.get("timestamp", "-")
                    closed_at = alarm.get("closed_at")
                    tooltip_parts = [
                        f"Марка: {alarm.get('brand', '')}",
                        f"Лизингополучатель: {alarm.get('lessee', '')}",
                        f"Открыта: {timestamp}"
                    ]
                    if closed_at:
                        tooltip_parts.append(f"Закрыта: {closed_at}")

                    results.append({
                        "source": "alarm",
                        "text": f"[Тревога] {timestamp} | {alarm.get('vin')} | {alarm.get('contract')} | {alarm.get('message')}",
                        "tooltip": " | ".join(tooltip_parts),
                        "data": alarm
                    })

    # 🔍 Заметки
    if os.path.exists("notes/notes_data.json"):
        with open("notes/notes_data.json", "r", encoding="utf-8") as f:
            notes = json.load(f)
            for note in notes:
                combined = f"{note.get('title', '')} {note.get('content', '')}".lower()
                if keyword in combined:
                    results.append({
                        "source": "note",
                        "text": f"[Заметка] {note.get('title')} | {note.get('content')[:40]}",
                        "tooltip": note.get("content"),
                        "data": note
                    })

    # 🔍 Чёрный список
    if os.path.exists("blacklist/blacklist_data.json"):
        with open("blacklist/blacklist_data.json", "r", encoding="utf-8") as f:
            entries = json.load(f)
            for entry in entries:
                combined = f"{entry.get('vin', '')} {entry.get('contract', '')} {entry.get('reason', '')}".lower()
                if keyword in combined:
                    results.append({
                        "source": "blacklist",
                        "text": f"[Чёрный список] {entry.get('vin')} | {entry.get('reason')}",
                        "tooltip": entry.get("contract", ""),
                        "data": entry
                    })

    return results
