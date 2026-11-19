"""Этап 2 (Вариант Б): проверка пакета по контракту schema.json."""
import copy
import json
from typing import Any

# ЭТАП 2 — ВТОРАЯ ПАРА. Разработчик: Михайлова Александра Анатольевна.
def load_json_file(filename: str) -> dict[str, Any]:
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

def validate_by_schema(packet: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """Проверяет типы, обязательные поля, границы, enum и физическое правило."""
    errors: list[str] = []
    props = schema.get("properties", {})
    if not isinstance(packet, dict):
        return False, ["Корень пакета должен быть объектом"]
    for field in schema.get("required", []):
        if field not in packet:
            errors.append(f"Отсутствует обязательное поле '{field}'")
    if errors:
        return False, errors

    for field in ("pad_id", "well_id"):
        value = packet[field]
        if not isinstance(value, str) or len(value.strip()) < props[field]["minLength"]:
            errors.append(f"Поле '{field}' должно быть непустой строкой")

    for field in ("p_res_mpa", "p_bhp_mpa"):
        rules = props[field]
        value = packet[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"Поле '{field}' должно быть числом")
        elif not (rules["minimum"] <= value <= rules["maximum"]):
            errors.append(f"Давление {field}={value} вне границ схемы [{rules['minimum']}; {rules['maximum']}]")

    if not isinstance(packet["mode"], str) or packet["mode"] not in props["mode"]["enum"]:
        errors.append(f"Режим mode={packet['mode']!r} не входит в enum {props['mode']['enum']}")
    if not isinstance(packet["is_online"], bool):
        errors.append("Поле 'is_online' должно быть логическим типом (boolean)")

    pres, pbhp = packet["p_res_mpa"], packet["p_bhp_mpa"]
    if (all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (pres, pbhp))
            and packet["mode"] == "PUMPING" and pbhp > pres):
        errors.append("Физическое противоречие: при режиме PUMPING Pзаб > Pпл!")

    rules = props["sensors"]
    sensors = packet["sensors"]
    if not isinstance(sensors, list) or len(sensors) < rules["minItems"]:
        errors.append(f"Массив 'sensors' должен содержать минимум {rules['minItems']} датчика")
    else:
        item_rules = rules["items"]
        for index, item in enumerate(sensors):
            if not isinstance(item, dict):
                errors.append(f"Датчик #{index} должен быть объектом (dict)")
                continue
            for field in item_rules["required"]:
                if field not in item:
                    errors.append(f"В датчике #{index} отсутствует поле '{field}'")
            if "code" in item and (not isinstance(item["code"], str) or not item["code"].strip()):
                errors.append(f"Датчик #{index}: поле 'code' должно быть непустой строкой")
            if "unit" in item and item["unit"] not in item_rules["properties"]["unit"]["enum"]:
                errors.append(f"Датчик #{index}: единица {item['unit']!r} не входит в enum {item_rules['properties']['unit']['enum']}")
            if "value" in item and (not isinstance(item["value"], (int, float)) or isinstance(item["value"], bool)):
                errors.append(f"Датчик #{index}: поле 'value' должно быть числом")
    return len(errors) == 0, errors

def show_result(number: int, label: str, packet: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, list[str]]:
    ok, errors = validate_by_schema(packet, schema)
    print(f"[Сценарий {number}] {label} -> {'УСПЕШНО (VALID)' if ok else 'ОТКЛОНЕНО'}")
    for error in errors:
        print(" x", error)
    return ok, errors

if __name__ == "__main__":
    print("НАЧАЛО ЭТАПА 2 (ВТОРАЯ ПАРА)")
    schema_doc = load_json_file("schema.json")
    valid_pkt = load_json_file("data.json")
    print("=" * 66)
    print("ПРОВЕРКА КОНТРАКТА ДАННЫХ (Вариант Б)")
    print("=" * 66)
    show_result(1, "Эталонный файл data.json", valid_pkt, schema_doc)
    bad_enum = copy.deepcopy(valid_pkt)
    bad_enum["mode"] = "OVERDRIVE"
    bad_enum["sensors"][0]["unit"] = "psi"
    show_result(2, "Нарушение enum режима и единицы", bad_enum, schema_doc)
    too_few = copy.deepcopy(valid_pkt)
    too_few["sensors"] = [valid_pkt["sensors"][0]]
    show_result(3, "Только один датчик", too_few, schema_doc)
    bad_phys = copy.deepcopy(valid_pkt)
    bad_phys["mode"] = "PUMPING"
    bad_phys["p_bhp_mpa"] = 50.0
    bad_phys["p_res_mpa"] = 20.0
    show_result(4, "Pзаб > Pпл при PUMPING", bad_phys, schema_doc)
    # Челлендж № 2: аналитик подготовил копию с ровно двумя нарушениями.
    show_result(5, "Слепая проверка broken_data.json", load_json_file("broken_data.json"), schema_doc)
    print("КОНЕЦ ЭТАПА 2 (ВТОРАЯ ПАРА)")
