import json
from pathlib import Path
from datetime import datetime, timezone

MEMORY_PATH = Path(__file__).resolve().parent.parent / "data" / "student_memory.json"

def load_memory(student_name: str) -> dict:
    if not MEMORY_PATH.exists():
        return {"student": student_name, "topics": [], "sessions": []}
    try:
        data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        return data.get(student_name.lower(), {
            "student": student_name, "topics": [], "sessions": []
        })
    except (json.JSONDecodeError, OSError):
        return {"student": student_name, "topics": [], "sessions": []}

def save_memory(student_name: str, topic: str, score=None, summary=""):
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        all_data = json.loads(MEMORY_PATH.read_text(encoding="utf-8")) if MEMORY_PATH.exists() else {}
    except (json.JSONDecodeError, OSError):
        all_data = {}
    key = student_name.lower()
    record = all_data.get(key, {"student": student_name, "topics": [], "sessions": []})
    record["topics"] = list(dict.fromkeys(record.get("topics", []) + [topic]))[-30:]
    record.setdefault("sessions", []).append({
        "topic": topic,
        "score": score,
        "summary": summary[:1200],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    record["sessions"] = record["sessions"][-30:]
    all_data[key] = record
    MEMORY_PATH.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")
