import json
import os

def global_search(keyword):
    keyword = keyword.lower()
    results = []

    # Тревоги
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
                    results.append({
                        "source": "alarm",
                        "text": f"[Тревога] {alarm.get('vin')} | {alarm.get('contract')} | {alarm.get('message')}",
                        "tooltip": f"{alarm.get('brand')} | {alarm.get('lessee')}",
                        "data": alarm
                    })

    # Заметки
    if os.path.exists("notes/notes_data.json"):
        with open("notes/notes_data.json", "r", encoding="utf-8") as f:
            notes = json.load(f)
            for note in notes:
                if keyword in note.get("text", "").lower():
                    results.append({
                        "source": "note",
                        "text": f"[Заметка] {note.get('text')[:40]}...",
                        "tooltip": note.get("text"),
                        "data": note
                    })

    # Чёрный список
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
