"""Этап 1 (Вариант Б): пакет телеметрии, сериализация и чтение JSON."""
import json
from typing import Any

# ЭТАП 1 — ПЕРВАЯ ПАРА. Разработчик: Шахманова Самира Расуловна.
N1, N2 = 7, 12
N = N1 + N2

def build_telemetry_packet() -> dict[str, Any]:
    """Формирует пакет по формулам раздела 4.2 методички."""
    return {
        "pad_id": f"PAD-{10 + (N % 20)}",
        "well_id": f"W-{200 + N}",
        "p_res_mpa": 22.0 + 0.5 * (N % 20),
        "p_bhp_mpa": 12.0 + 0.4 * (N % 20),
        "mode": "PUMPING",
        "is_online": True,  # Челлендж № 1
        "sensors": [
            {"code": "T-01", "value": 45.0 + 1.5 * (N % 15), "unit": "C"},
            {"code": "Q-01", "value": 60.0 + 4.0 * (N % 25), "unit": "m3/d"},
            {"code": "P-01", "value": 14.0, "unit": "MPa"},  # Челлендж № 1
        ],
    }

def save_to_json(data: dict[str, Any], filename: str = "data.json") -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_from_json(filename: str = "data.json") -> dict[str, Any]:
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

def print_telemetry_summary(packet: dict[str, Any]) -> None:
    drawdown = packet["p_res_mpa"] - packet["p_bhp_mpa"]
    print("=" * 58)
    print(f"ПАКЕТ ТЕЛЕМЕТРИИ: Куст {packet['pad_id']} | Скважина {packet['well_id']}")
    print("=" * 58)
    print(f"Режим работы: {packet['mode']}")
    print(f"Связь со станцией: {packet['is_online']}")
    print(f"Давления: Pпл = {packet['p_res_mpa']} МПа, Pзаб = {packet['p_bhp_mpa']} МПа (dP = {drawdown:.2f} МПа)")
    print(f"Опрошено датчиков: {len(packet['sensors'])} шт.")
    for sensor in packet["sensors"]:
        print(f" -> Датчик {sensor['code']}: {sensor['value']} {sensor['unit']}")
    print("=" * 58)

if __name__ == "__main__":
    print("НАЧАЛО ЭТАПА 1 (ПЕРВАЯ ПАРА)")
    packet = build_telemetry_packet()
    save_to_json(packet)
    print("[OK] Файл data.json записан")
    loaded = load_from_json()
    assert loaded == packet, "Ошибка: данные при чтении JSON исказились!"
    print("[OK] Обратное чтение через json.load() прошло успешно")
    print_telemetry_summary(loaded)
    print("КОНЕЦ ЭТАПА 1 (ПЕРВАЯ ПАРА)")
