import os
import re
import csv
import json
import logging
from typing import Dict, Any, List

from openai import OpenAI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

###################################
# Pydantic модели (по необходимости)
###################################
class ColumnStructure(BaseModel):
    name: str
    meaning: str
    data_type: str
    relationships: List[str]

class GeneralStructure(BaseModel):
    type: str
    rows: int
    columns: int

class Content(BaseModel):
    purpose: str
    column_structure: List[ColumnStructure]

class Analysis(BaseModel):
    general_structure: GeneralStructure
    content: Content

###################################
# Пример итогового формата (OPTIONAL)
###################################
class DirectClient:
    """Пример обёртки над openai.ChatCompletion для упрощения вызовов."""
    def __init__(self):
        self.client = OpenAI()
        # Модель, поддерживающая JSON Mode или Structured Outputs
        self.model = "gpt-4o-mini-2024-07-18"
    
    def create(self, prompt: str, temperature=0) -> Dict[str, Any]:
        """
        Создаёт запрос к GPT (JSON Mode, так как response_format={"type":"json_object"}).
        
        Если нужно строгое следование схеме, 
        используйте type="json_schema" + "json_schema": {...}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that analyzes tables and "
                            "returns structured data in JSON format. "
                            "Always respond with valid JSON."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=2000
            )
            content = response.choices[0].message.content
            logger.info(f"GPT raw response: {content}")

            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                return {
                    "error": f"Failed to parse JSON: {str(e)}",
                    "raw_content": content
                }
        except Exception as e:
            logger.error(f"Error in GPT request: {e}")
            return {
                "error": f"Error in GPT request: {str(e)}"
            }

###################################
# ШАГ 1: Анализ структуры
###################################
def analyze_headers_and_relationships(
    client: DirectClient, 
    headers: List[str], 
    sample_rows: List[List[str]]
) -> Dict[str, Any]:
    """
    Шлём GPT часть данных (заголовки + первые несколько строк),
    чтобы определить основные колонки, колонки параметров, связи между строками и т.д.
    """
    sample_data = "\n".join(
        [",".join(headers)] + [",".join(row) for row in sample_rows[:5]]
    )
    
    prompt = f"""
Проанализируй структуру таблицы.

ЗАГОЛОВКИ:
{headers}

ПРИМЕР СТРОК (до 5):
{sample_data}

ОПИШИ В JSON:
1) main_columns - какие столбцы (номер или название) содержат:
   - название материала (material_name)
   - стандарт/ТУ (standard)
   - область применения (application)
2) parameter_columns - какие столбцы содержат:
   - название параметра (name)
   - значение параметра (value)
   - единицу измерения (unit) - если её нужно извлекать
3) row_relationships:
   - type: "independent", "hierarchical" или "continuation"
   - rules: массив строк с описанием логики

Формат вывода (пример):
{{
  "main_columns": {{
    "material_name": "...",
    "standard": "...",
    "application": "..."
  }},
  "parameter_columns": {{
    "name": "...",
    "value": "...",
    "unit": "..."
  }},
  "row_relationships": {{
    "type": "...",
    "rules": ["...", "..."]
  }}
}}
    """

    return client.create(prompt)

###################################
# ШАГ 2: Создание шаблона
###################################
def create_json_template(structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Исходя из анализа структуры, готовим JSON-шаблон,
    который будем отдавать в дальнейших промптах.
    """
    template = {
        "type": "technical_specification_table",
        "materials": [
            {
                "row_number": "integer",
                "name": "string",
                "standard": "string?",
                "parameters": [
                    {
                        "name": "string",
                        "value": "string",
                        "unit": "string?",
                        "limit_type": "enum(min,max,range,exact)",
                        "notes": "string?"
                    }
                ],
                "application": "string?"
            }
        ],
        "validation_rules": {
            "required_fields": ["name", "parameters"],
            "parameter_rules": {
                "value_patterns": [
                    "не более X -> max",
                    "не менее X -> min",
                    "X-Y -> range",
                    "X -> exact"
                ],
                "unit_extraction": "from_value_or_name"
            }
        }
    }
    return template

###################################
# ШАГ 3: Поиск семантических групп
###################################
def find_semantic_groups(
    client: DirectClient, 
    headers: List[str],
    rows: List[List[str]]
) -> Dict[str, Any]:
    """
    Шлём GPT весь CSV (или хотя бы часть),
    просим разделить данные на группы (газы, катализаторы, реагенты и т.д.),
    указать подгруппы, описать иерархические связи.
    """
    table_text = "\n".join([",".join(headers)] + [",".join(r) for r in rows])
    
    prompt = f"""
Найдите семантические группы в таблице на основе её содержимого.

ЗАГОЛОВКИ:
{headers}

ВСЯ ТАБЛИЦА (CSV-формат):
{table_text}

Выведите:
{{
  "groups": [
    {{
      "name": "название группы",
      "description": "короткое описание",
      "row_numbers": [int, int, ...],
      "subgroups": [
        {{
          "name": "подгруппа",
          "row_numbers": [int, int, ...]
        }}
      ]
    }}
  ],
  "ungrouped_rows": [int, int, ...]
}}
    """
    return client.create(prompt)

###################################
# ПОСТОБРАБОТКА
###################################
def format_chemical_formula(formula: str) -> str:
    """
    Пример форматирования химических формул с заменой латинскими символами и добавлением нижних индексов.
    """
    if not formula or not isinstance(formula, str):
        return formula
        
    try:
        # Приведём кириллические С/Н к латинице (если вдруг встречаются)
        formula = formula.replace('С', 'C').replace('Н', 'H')
        # Уберём лишние пробелы
        formula = formula.replace(' ', '')

        # Иногда бывает "CH" без индекса => превращаем в CH₄
        # но только если нет "CH4" или "CH₄" уже
        if 'CH' in formula and not any(x in formula for x in ['CH4', 'CH₄']):
            formula = formula.replace('CH', 'CH4')

        # Аналогично для C2H, C3H
        if 'C2H' in formula and not any(x in formula for x in ['C2H6', 'C₂H₆']):
            formula = formula.replace('C2H', 'C2H6')
        if 'C3H' in formula and not any(x in formula for x in ['C3H8', 'C₃H₈']):
            formula = formula.replace('C3H', 'C3H8')

        # Словарь замен для субскриптов
        replacements = {
            'CH4': 'CH₄',
            'CO2': 'CO₂',
            'H2': 'H₂',
            'C2H6': 'C₂H₆',
            'C3H8': 'C₃H₈',
            'C4H10': 'C₄H₁₀',
            'C5H12': 'C₅H₁₂',
            'C6H14': 'C₆H₁₄',
            'C7H16': 'C₇H₁₆',
            'C8H18': 'C₈H₁₈',
            'CH':  'CH₄',   # если случайно осталось CH
            'C2H4': 'C₂H₄',
            'C3H6': 'C₃H₆',
            'C4': 'C₄H₁₀',  # грубое упрощение
            'C5': 'C₅H₁₂',
            'C6': 'C₆H₁₄',
            'C7': 'C₇H₁₆',
            'C8': 'C₈H₁₈',
            'CзH': 'C₃H₈',   # если была буква 'з' вместо 3
        }
        
        for old, new in replacements.items():
            formula = formula.replace(old, new)
            
        # Ещё раз убираем пробелы
        formula = formula.replace(' ', '')
        
        return formula
    except Exception as e:
        logging.error(f"Error formatting chemical formula: {str(e)}")
        return formula

def format_range_value(value: str) -> str:
    """
    Приводим диапазоны к более-менее единообразному виду:
    - Удаляем 'в пределах'
    - '÷' заменяем на '-'
    - 'не более' убираем как текст
    - если есть X Y без разделителя - превращаем в X-Y
    - и т.д.
    """
    if not value or not isinstance(value, str):
        return value
    
    try:
        # Уберём «в пределах»
        value = value.replace('в пределах', '').strip()
        
        # Заменим «÷» на «-»
        value = value.replace('÷', '-')
        
        # Иногда бывает, что нет «-» или «,», но есть пробел:
        # "10 20" -> "10-20", если оба являются числами
        if ' ' in value and '-' not in value and ',' not in value:
            parts = value.split()
            if len(parts) == 2 and all(p.replace('.', '').replace(',', '').isdigit() for p in parts):
                value = f"{parts[0]}-{parts[1]}"
        
        # «не более X» -> убираем текст, остаётся X
        if 'не более' in value.lower():
            value = value.lower().replace('не более', '').strip()
        
        # «не менее X» -> убираем текст, остаётся X
        if 'не менее' in value.lower():
            value = value.lower().replace('не менее', '').strip()
        
        # Убираем пробелы вокруг дефиса
        value = value.replace(' - ', '-').replace(' -', '-').replace('- ', '-')
        
        # Если в значении есть запятая как разделитель, но нет дефиса
        # "10,20" -> "10-20"
        if ',' in value and '-' not in value:
            parts = value.split(',')
            if len(parts) == 2 and all(p.strip().replace('.', '').isdigit() for p in parts):
                value = f"{parts[0].strip()}-{parts[1].strip()}"
        
        # Удаляем ведущие/конечные пробелы
        value = value.strip()
        
        return value
    except Exception as e:
        logging.error(f"Error formatting range value: {str(e)}")
        return value

def define_limit_type(value: str) -> str:
    """
    Определяем limit_type на основании текста:
    - 'не более X' -> max
    - 'не менее X' -> min
    - 'X-Y' или 'X÷Y' -> range
    - 'X' -> exact
    """
    if not value or not isinstance(value, str):
        return ""
    
    val_lower = value.lower()
    if 'не более' in val_lower:
        return "max"
    if 'не менее' in val_lower:
        return "min"
    if '-' in value or '÷' in value:
        # Предположим, что раз есть дефис или знак «÷», то это диапазон
        return "range"
    # иначе по умолчанию exact
    return "exact"

def deduplicate_parameters(parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Удалить дубли по (name, value)."""
    seen = set()
    unique = []
    for p in parameters:
        key = (p.get("name"), p.get("value"))
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique

def process_parameters(params: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Проверяем/форматируем chem. формулы, диапазоны и т.д., а также назначаем limit_type."""
    processed = []
    for p in params:
        pcopy = dict(p)
        
        # Форматируем name как химию
        if "name" in pcopy:
            pcopy["name"] = format_chemical_formula(pcopy["name"])
        
        # Форматируем value как диапазон
        if "value" in pcopy:
            original_value = pcopy["value"]
            pcopy["value"] = format_range_value(original_value)
            # Определяем limit_type
            pcopy["limit_type"] = define_limit_type(original_value)
        
        processed.append(pcopy)
    # Дедупликация
    processed = deduplicate_parameters(processed)
    return processed

###################################
# ШАГ 4: Обработка группы
###################################
def process_group(
    client: DirectClient,
    structure: Dict[str, Any],
    template: Dict[str, Any],
    headers: List[str],
    rows: List[List[str]],
    group_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Для каждой группы (и подгруппы) шлём GPT данные,
    указываем: «вот наша структура, вот наш шаблон, извлеки материалы и их параметры».

    Возвращаем общий результат: {"materials": [...]}
    """
    all_materials = []

    group_name = group_info.get("name", "UnnamedGroup")
    row_numbers = group_info.get("row_numbers", [])
    # Берём нужные строки (учитывая, что CSV начинается с 0, а row_number может быть с 1)
    group_rows = [rows[i-1] for i in row_numbers if 1 <= i <= len(rows)]
    
    # Формируем CSV-текст именно для этой группы
    group_csv_text = "\n".join([",".join(headers)] + [",".join(r) for r in group_rows])
    
    extraction_prompt = f"""
Извлеките данные для группы "{group_name}" из фрагмента CSV:

СТРУКТУРА (JSON):
{json.dumps(structure, ensure_ascii=False, indent=2)}

ШАБЛОН (JSON):
{json.dumps(template, ensure_ascii=False, indent=2)}

ФРАГМЕНТ CSV:
{group_csv_text}

ОПИСАНИЕ ГРУППЫ:
{group_info.get("description", "")}

ПРАВИЛА:
1. Используйте номера столбцов, если были определены (main_columns, parameter_columns).
2. Извлекайте единицы измерения, если указано.
3. Определяйте limit_type: "не более X" -> max, "не менее X" -> min, "X-Y" -> range, "X" -> exact.
4. Химические формулы формировать аккуратно (CO₂, H₂, CH₄ и т.д.).
5. Не добавляйте лишние параметры, не дублируйте.
6. Сохраняйте все строки из CSV.
7. Верните JSON строго в формате:
{{
  "materials": [
    {{
      "row_number": int,
      "name": str,
      "standard": str | null,
      "parameters": [
        {{
          "name": str,
          "value": str,
          "unit": str | null,
          "limit_type": "min"|"max"|"range"|"exact"|null,
          "notes": str | null
        }}
      ],
      "application": str | null
    }}
  ]
}}
    """
    result = client.create(extraction_prompt)
    if "error" not in result and "materials" in result:
        all_materials.extend(result["materials"])
    
    # Обработка подгрупп
    if "subgroups" in group_info:
        for subg in group_info["subgroups"]:
            subg_name = subg.get("name", "UnnamedSubgroup")
            subg_rows = subg.get("row_numbers", [])
            subg_data = [rows[i-1] for i in subg_rows if 1 <= i <= len(rows)]
            subg_csv_text = "\n".join(
                [",".join(headers)] + [",".join(r) for r in subg_data]
            )
            
            subg_prompt = f"""
Извлеките данные для подгруппы "{subg_name}" (принадлежит группе "{group_name}").

СТРУКТУРА (JSON):
{json.dumps(structure, ensure_ascii=False, indent=2)}

ШАБЛОН (JSON):
{json.dumps(template, ensure_ascii=False, indent=2)}

ФРАГМЕНТ CSV:
{subg_csv_text}

ПРАВИЛА: (аналогично выше).
Верните JSON строго: {{ "materials": [...]}}.
            """
            subg_result = client.create(subg_prompt)
            if "error" not in subg_result and "materials" in subg_result:
                all_materials.extend(subg_result["materials"])
    
    # Постобработка (формулы, диапазоны, limit_type, дедупликация)
    for mat in all_materials:
        if "parameters" in mat:
            mat["parameters"] = process_parameters(mat["parameters"])
    
    return {"materials": all_materials}


###################################
# ОБЩАЯ ЛОГИКА АНАЛИЗА
###################################
def analyze_csv_with_rag(client: DirectClient, csv_path: str) -> Dict[str, Any]:
    """
    Шаги:
    1) Чтение CSV
    2) GPT-анализ заголовков (analyze_headers_and_relationships)
    3) Создание JSON шаблона (create_json_template)
    4) GPT-анализ семантических групп (find_semantic_groups)
    5) process_group(...) для каждой группы и подгруппы
    6) Складываем результаты в grouped_data + warnings
    """
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            rows = list(reader)
        
        ### 1) Анализ структуры
        logger.info("=== Анализ структуры (GPT) ===")
        structure = analyze_headers_and_relationships(client, headers, rows)
        if "error" in structure:
            return structure
        
        ### 2) Создание шаблона
        logger.info("=== Создание JSON-шаблона ===")
        template = create_json_template(structure)
        
        ### 3) Поиск семантических групп
        logger.info("=== Поиск семантических групп (GPT) ===")
        grouping = find_semantic_groups(client, headers, rows)
        if "error" in grouping:
            return grouping
        
        # grouping содержит "groups" + "ungrouped_rows"
        groups_info = grouping.get("groups", [])
        ungrouped = grouping.get("ungrouped_rows", [])
        
        ### 4) Обработка групп
        logger.info("=== Обработка групп ===")
        all_materials = []
        for group in groups_info:
            group_result = process_group(client, structure, template, headers, rows, group)
            all_materials.extend(group_result.get("materials", []))
        
        # Можно отдельно обработать ungrouped_rows (как отдельную «группу»)
        if ungrouped:
            pseudo_group = {
                "name": "ungrouped",
                "description": "Строки, не вошедшие ни в одну группу",
                "row_numbers": ungrouped,
                "subgroups": []
            }
            ungrouped_result = process_group(client, structure, template, headers, rows, pseudo_group)
            all_materials.extend(ungrouped_result.get("materials", []))
        
        ### 5) Превращаем всё в grouped_data
        grouped_data = {}
        for group in groups_info:
            gname = group.get("name", "UnnamedGroup")
            grouped_data[gname] = []
        grouped_data["ungrouped"] = []
        
        # row_to_group: помним, какой номер строки попал в какую группу
        row_to_group = {}
        for group in groups_info:
            gname = group.get("name", "UnnamedGroup")
            for rn in group.get("row_numbers", []):
                row_to_group[rn] = gname
            # подгруппы
            for subg in group.get("subgroups", []):
                for rn in subg.get("row_numbers", []):
                    row_to_group[rn] = gname
        
        # Упаковываем материалы в grouped_data
        for mat in all_materials:
            rnum = mat.get("row_number")
            gname = row_to_group.get(rnum, "ungrouped")
            
            row_obj = {
                "row_name": mat.get("name", ""),
                "indicators": []
            }
            if mat.get("standard"):
                row_obj["indicators"].append({
                    "header": "standard",
                    "value": mat["standard"]
                })
            if mat.get("application"):
                row_obj["indicators"].append({
                    "header": "application",
                    "value": mat["application"]
                })
            # Параметры
            for param in mat.get("parameters", []):
                row_obj["indicators"].append({
                    "header": param.get("name", ""),
                    "value": param.get("value", "")
                })
            
            if gname not in grouped_data:
                grouped_data[gname] = []
            grouped_data[gname].append(row_obj)
        
        # Предупреждения
        warning_msgs = []
        if not groups_info and not ungrouped:
            warning_msgs.append("GPT не смогло выделить группы.")
        
        # Финальный результат
        result = {
            "analysis": {
                "structure": structure,
                "groups_info": grouping
            },
            "grouped_data": grouped_data,
        }
        if warning_msgs:
            result["warning"] = "\n".join(warning_msgs)
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при анализе CSV: {e}")
        return {"error": str(e)}


###################################
# ФОРМАТИРОВАНИЕ В ТЕКСТ
###################################
def format_analysis_output(result_json: Dict[str, Any], output_file) -> None:
    """
    Записывает в текстовом виде:
    - Информацию о группах
    - Информацию о структуре
    - Содержимое grouped_data
    - Предупреждения
    """
    def wline(line=""):
        output_file.write(line + "\n")
    
    wline("=== Итоговый анализ таблицы ===")
    
    if "analysis" in result_json:
        analysis = result_json["analysis"]
        
        wline("\n--- Структура заголовков (GPT) ---")
        structure = analysis.get("structure", {})
        wline(json.dumps(structure, ensure_ascii=False, indent=2))
        
        wline("\n--- Информация о группах (GPT) ---")
        groups_info = analysis.get("groups_info", {})
        wline(json.dumps(groups_info, ensure_ascii=False, indent=2))
    
    if "grouped_data" in result_json:
        wline("\n=== Группированные данные ===")
        for gname, rows in result_json["grouped_data"].items():
            wline(f"Группа: {gname}, строк: {len(rows)}")
            for idx, row_obj in enumerate(rows, start=1):
                wline(f"  {idx}) row_name = {row_obj.get('row_name')}")
                indicators = row_obj.get("indicators", [])
                for ind in indicators:
                    wline(f"       - {ind.get('header')}: {ind.get('value')}")
    
    if "warning" in result_json and result_json["warning"]:
        wline("\n--- ПРЕДУПРЕЖДЕНИЯ ---")
        for line in result_json["warning"].split("\n"):
            wline(f"! {line}")

###################################
# MAIN
###################################
if __name__ == "__main__":
    # Пример пути к CSV-файлу
    csv_path = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/output/merged_page_11-15.csv"

    # Извлекаем номера страниц из имени файла
    page_numbers = re.search(r'page_(\d+)-(\d+)', csv_path)
    page_suffix = f"page_{page_numbers.group(1)}-{page_numbers.group(2)}" if page_numbers else "unknown"

    # Создаём директорию для результатов
    output_dir = os.path.join(os.path.dirname(csv_path), "analysis_results")
    os.makedirs(output_dir, exist_ok=True)

    # Создаём клиент
    client = DirectClient()

    # Запуск «многошагового» анализа CSV
    result_json = analyze_csv_with_rag(client, csv_path)

    # Сохраняем результат в JSON
    json_output_path = os.path.join(output_dir, f"table_analysis_{page_suffix}.json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    
    # Сохраняем результат в TXT
    txt_output_path = os.path.join(output_dir, f"table_analysis_{page_suffix}.txt")
    with open(txt_output_path, 'w', encoding='utf-8') as f:
        format_analysis_output(result_json, f)

    print("\n=== АНАЛИЗ ЗАВЕРШЕН ===")
    print(f"Результаты сохранены в:\n - JSON: {json_output_path}\n - TXT:  {txt_output_path}")
    
    # Если нужно вывести статистику по grouped_data
    if "grouped_data" in result_json:
        gd = result_json["grouped_data"]
        total_rows = sum(len(arr) for arr in gd.values())
        total_indicators = sum(
            sum(len(x.get("indicators", [])) for x in arr) 
            for arr in gd.values()
        )
        print("\nСтатистика:")
        print(f"Групп: {len(gd)}")
        print(f"Всего строк: {total_rows}")
        print(f"Всего показателей: {total_indicators}")
    
    if "warning" in result_json:
        print("\nПредупреждения:")
        for line in result_json["warning"].split("\n"):
            print(f"- {line}")