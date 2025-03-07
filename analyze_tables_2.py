import os
import json
import logging
import csv
from typing import Dict, Any, List
from openai import OpenAI
from pydantic import BaseModel
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class RowData(BaseModel):
    row_number: int
    text: str
    values: Dict[str, str]

class TableAnalysis(BaseModel):
    analysis: Analysis
    cleaned_groups: Dict[str, List[RowData]]
    warning: str | None = None
    error: str | None = None

class DirectClient:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4o-mini-2024-07-18"  # Используем последнюю версию с поддержкой Structured Outputs
    
    def create(self, prompt: str) -> Dict[str, Any]:
        """Создает запрос к GPT с использованием Structured Outputs."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that analyzes tables and returns structured data in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=4000,
                n=1,
                stop=None,
            )
            
            content = response.choices[0].message.content
            logger.info(f"Raw response: {content}")
            
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return {
                    "error": f"Failed to parse JSON response: {str(e)}",
                    "raw_response": content
                }
        except Exception as e:
            logger.error(f"Error in GPT request: {e}")
            return {
                "error": f"Error in GPT request: {str(e)}"
            }

def analyze_headers_and_relationships(client: DirectClient, headers: List[str], sample_rows: List[List[str]]) -> Dict[str, Any]:
    """Анализирует заголовки и связи между строками."""
    
    # Prepare sample data, handling multi-line headers
    header_text = "\n".join([str(h).replace('\n', ' ').strip() for h in headers])
    sample_data = "\n".join([
        ",".join([str(cell).replace('\n', ' ').strip() for cell in row])
        for row in sample_rows[:10]  # Include more sample rows
    ])
    
    structure_prompt = """Проанализируйте структуру заголовков и связи между строками в таблице.

ЗАГОЛОВКИ:
{}

ПРИМЕР ДАННЫХ:
{}

Определите:
1. Структуру данных:
   - Где находится номер п/п
   - Где находится название материала/вещества
   - Где находится стандарт/ТУ
   - Где находятся показатели и их значения
   - Где находится область применения
2. Связи между строками:
   - Как определить, что строка продолжает предыдущую запись
   - Как определить, что строка содержит новый показатель
   - Как определить, что строка начинает новый материал
3. Формат значений:
   - Как извлекать единицы измерения
   - Как обрабатывать диапазоны значений
   - Как определять тип предела (мин/макс)

Верните результат в формате:
{{
    "main_columns": {{
        "material_number": "номер столбца с номером п/п",
        "material_name": "номер столбца с названием материала",
        "standard": "номер столбца со стандартом",
        "application": "номер столбца с областью применения"
    }},
    "parameter_columns": {{
        "name": "номер столбца с названием показателя",
        "value": "номер столбца со значением",
        "unit_extraction": "правило извлечения единиц измерения"
    }},
    "row_relationships": {{
        "type": "тип связи между строками (independent/hierarchical/continuation)",
        "rules": [
            "правило определения связи 1",
            "правило определения связи 2"
        ]
    }},
    "value_processing": {{
        "unit_patterns": ["шаблон1", "шаблон2"],
        "range_patterns": ["шаблон1", "шаблон2"],
        "limit_patterns": {{
            "min": ["не менее", "более"],
            "max": ["не более", "менее"],
            "exact": ["равно", "точно"]
        }}
    }}
}}""".format(header_text, sample_data)

    return client.create(structure_prompt)

def create_json_template(structure: Dict[str, Any]) -> Dict[str, Any]:
    """Создает шаблон JSON на основе анализа структуры."""
    
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
                    "не менее X -> min",
                    "не более X -> max",
                    "X-Y -> range",
                    "X -> exact"
                ],
                "unit_extraction": "from_value_or_name"
            }
        }
    }
    
    return template

def find_semantic_groups(client: DirectClient, headers: List[str], rows: List[List[str]]) -> Dict[str, Any]:
    """Находит семантические группы в данных."""
    
    # Анализируем все строки для точного определения групп
    table_text = "\n".join([",".join(headers)] + [",".join(row) for row in rows])
    
    group_prompt = """Найдите семантические группы в таблице.

ЗАГОЛОВКИ:
{}

ДАННЫЕ:
{}

ИНСТРУКЦИИ:
1. Проанализируйте все названия сущностей (оборудования, материалов/веществ)
2. Найдите логические группы (например: газы, катализаторы, реагенты и т.д.)
3. Определите строки, относящиеся к каждой группе
4. Учитывайте иерархические связи между строками
5. Убедитесь, что каждая строка отнесена к группе или помечена как негруппированная

Верните результат в формате:
{{
    "groups": [
        {{
            "name": "название группы",
            "description": "описание группы",
            "row_numbers": [номера строк],
            "subgroups": [
                {{
                    "name": "название подгруппы",
                    "row_numbers": [номера строк]
                }}
            ]
        }}
    ],
    "ungrouped_rows": [номера строк, не вошедших в группы]
}}""".format(",".join(headers), table_text)

    return client.create(group_prompt)

def format_chemical_formula(formula):
    """Format chemical formulas with proper subscripts."""
    if not formula or not isinstance(formula, str):
        return formula
        
    try:
        # First, standardize the input
        formula = formula.replace('С', 'C').replace('Н', 'H')
        formula = formula.replace(' ', '')
        
        # Handle special cases first
        if 'CH' in formula and not any(x in formula for x in ['CH4', 'CH₄']):
            formula = formula.replace('CH', 'CH₄')
        if 'C2H' in formula and not any(x in formula for x in ['C2H6', 'C₂H₆']):
            formula = formula.replace('C2H', 'C₂H₆')
        if 'C3H' in formula and not any(x in formula for x in ['C3H8', 'C₃H₈']):
            formula = formula.replace('C3H', 'C₃H₈')
        
        # Extended replacements dictionary
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
            'CH': 'CH₄',
            'C2H4': 'C₂H₄',
            'C3H6': 'C₃H₆',
            'C4': 'C₄H₁₀',
            'C5': 'C₅H₁₂',
            'C6': 'C₆H₁₄',
            'C7': 'C₇H₁₆',
            'C8': 'C₈H₁₈',
            'CзH': 'C₃H₈',
        }
        
        # Process the formula
        for old, new in replacements.items():
            formula = formula.replace(old, new)
            
        # Clean up any remaining spaces
        formula = formula.replace(' ', '')
        
        return formula
    except Exception as e:
        logging.error(f"Error formatting chemical formula: {str(e)}")
        return formula

def deduplicate_parameters(parameters):
    """Remove duplicate parameters while preserving order."""
    seen = set()
    unique_params = []
    
    for param in parameters:
        # Create a unique key based on name and value
        key = (param['name'], param['value'])
        if key not in seen:
            seen.add(key)
            # Format chemical formulas in parameter names
            param['name'] = format_chemical_formula(param['name'])
            unique_params.append(param)
    
    return unique_params

def format_range_value(value):
    """Format range values consistently."""
    if not value or not isinstance(value, str):
        return value
    
    try:
        # Remove "в пределах" and extra spaces
        value = value.replace('в пределах', '').strip()
        
        # Handle various separators
        value = value.replace('÷', '-')
        
        # Fix spaces in ranges
        if ' ' in value and '-' not in value and ',' not in value:
            parts = value.split()
            if len(parts) == 2 and all(p.replace('.', '').replace(',', '').isdigit() for p in parts):
                value = f"{parts[0]}-{parts[1]}"
        
        # Handle "не более" values
        if 'не более' in value:
            value = value.replace('не более', '').strip()
            
        # Remove spaces around separators
        value = value.replace(' - ', '-').replace(' -', '-').replace('- ', '-')
        
        # Handle missing separators in ranges
        if ',' in value and '-' not in value:
            parts = value.split(',')
            if len(parts) == 2 and all(p.strip().replace('.', '').isdigit() for p in parts):
                value = f"{parts[0].strip()}-{parts[1].strip()}"
                
        # Clean up any remaining spaces
        value = value.strip()
        
        return value
    except Exception as e:
        logging.error(f"Error formatting range value: {str(e)}")
        return value

def safe_process_response(response_text):
    """Safely process API response."""
    try:
        if not response_text:
            return None
            
        # Handle incomplete JSON
        if response_text.strip().endswith('"type": "technical_spec'):
            return None
            
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error processing response: {str(e)}")
        return None

def process_parameters(parameters):
    """Process and validate parameters."""
    if not parameters:
        return parameters
    
    processed = []
    for param in parameters:
        try:
            if not isinstance(param, dict):
                continue
                
            # Create a copy to avoid modifying the original
            processed_param = param.copy()
            
            # Format chemical formulas in name
            if 'name' in processed_param:
                processed_param['name'] = format_chemical_formula(processed_param['name'])
                
            # Format range values
            if 'value' in processed_param:
                processed_param['value'] = format_range_value(processed_param['value'])
                
            processed.append(processed_param)
        except Exception as e:
            logging.error(f"Error processing parameter: {str(e)}")
            continue
    
    return processed

def process_group(client: DirectClient, structure: Dict[str, Any], template: Dict[str, Any], 
                 headers: List[str], rows: List[List[str]], group_info: Dict[str, Any]) -> Dict[str, Any]:
    """Process a group of materials."""
    try:
        all_materials = []
        
        # Обрабатываем основные строки группы
        group_rows = [rows[i-1] for i in group_info["row_numbers"] if 0 < i <= len(rows)]
        if group_rows:
            # Формируем текст для группы
            group_text = "\n".join([",".join(headers)] + [",".join(row) for row in group_rows])
            
            extraction_prompt = """Извлеките данные для группы "{}" согласно структуре и шаблону.

СТРУКТУРА:
{}

ШАБЛОН:
{}

ДАННЫЕ ГРУППЫ:
{}

ОПИСАНИЕ ГРУППЫ:
{}

ПРАВИЛА:
1. Используйте номера столбцов из структуры точно как указано
2. Следуйте правилам связи строк
3. Извлекайте единицы измерения согласно указанному способу
4. Определяйте тип предела строго по шаблонам:
   - "не более X" -> max
   - "не менее X" -> min
   - "X-Y" или "X÷Y" -> range
   - просто "X" -> exact
5. Химические формулы:
   - Сохраняйте точное написание (H₂, CO₂, CH₄ и т.д.)
   - Не изменяйте индексы и регистр
   - Сохраняйте все знаки и символы
6. Значения:
   - Сохраняйте точное написание чисел (0,001 а не 0.001)
   - Сохраняйте все разделители как в оригинале
   - Диапазоны записывайте точно как в исходнике
7. Не добавляйте параметры, которых нет в исходных данных
8. Не дублируйте параметры
9. Обрабатывайте все строки из группы

Верните данные строго по шаблону.""".format(
                group_info["name"],
                json.dumps(structure, ensure_ascii=False, indent=2),
                json.dumps(template, ensure_ascii=False, indent=2),
                group_text,
                group_info.get("description", "")
            )

            result = client.create(extraction_prompt)
            if "error" not in result and "materials" in result:
                all_materials.extend(result["materials"])
        
        # Обрабатываем подгруппы
        if "subgroups" in group_info:
            for subgroup in group_info["subgroups"]:
                subgroup_rows = [rows[i-1] for i in subgroup["row_numbers"] if 0 < i <= len(rows)]
                if subgroup_rows:
                    subgroup_text = "\n".join([",".join(headers)] + [",".join(row) for row in subgroup_rows])
                    
                    subgroup_prompt = """Извлеките данные для подгруппы "{}" (часть группы "{}") согласно структуре и шаблону.

СТРУКТУРА:
{}

ШАБЛОН:
{}

ДАННЫЕ ПОДГРУППЫ:
{}

ПРАВИЛА:
1. Используйте номера столбцов из структуры точно как указано
2. Следуйте правилам связи строк
3. Извлекайте единицы измерения согласно указанному способу
4. Определяйте тип предела строго по шаблонам:
   - "не более X" -> max
   - "не менее X" -> min
   - "X-Y" или "X÷Y" -> range
   - просто "X" -> exact
5. Химические формулы:
   - Сохраняйте точное написание (H₂, CO₂, CH₄ и т.д.)
   - Не изменяйте индексы и регистр
   - Сохраняйте все знаки и символы
6. Значения:
   - Сохраняйте точное написание чисел (0,001 а не 0.001)
   - Сохраняйте все разделители как в оригинале
   - Диапазоны записывайте точно как в исходнике
7. Не добавляйте параметры, которых нет в исходных данных
8. Не дублируйте параметры
9. Обрабатывайте все строки из подгруппы

Верните данные строго по шаблону.""".format(
                        subgroup["name"],
                        group_info["name"],
                        json.dumps(structure, ensure_ascii=False, indent=2),
                        json.dumps(template, ensure_ascii=False, indent=2),
                        subgroup_text
                    )

                    subgroup_result = client.create(subgroup_prompt)
                    if "error" not in subgroup_result and "materials" in subgroup_result:
                        all_materials.extend(subgroup_result["materials"])
        
        # Process parameters for each material
        for material in all_materials:
            try:
                if 'parameters' in material:
                    material['parameters'] = process_parameters(material['parameters'])
                    material['parameters'] = deduplicate_parameters(material['parameters'])
            except Exception as e:
                logging.error(f"Error processing material parameters: {str(e)}")
                continue
        
        return {"materials": all_materials}
    except Exception as e:
        logging.error(f"Error processing group: {str(e)}")
        return {"materials": []}

def process_chunk(client: DirectClient, structure: Dict[str, Any], template: Dict[str, Any],
                 headers: List[str], rows: List[List[str]], start_idx: int, chunk_size: int = 15) -> Dict[str, Any]:
    """Обрабатывает чанк строк."""
    
    # Получаем строки для чанка
    end_idx = min(start_idx + chunk_size, len(rows))
    chunk_rows = rows[start_idx:end_idx]
    
    # Формируем текст для чанка
    chunk_text = "\n".join([",".join(headers)] + [",".join(row) for row in chunk_rows])
    
    extraction_prompt = """Извлеките данные из части таблицы согласно структуре и шаблону.

СТРУКТУРА:
{}

ШАБЛОН:
{}

ДАННЫЕ (строки {}-{}):
{}

ПРАВИЛА:
1. Используйте номера столбцов из структуры точно как указано
2. Следуйте правилам связи строк
3. Извлекайте единицы измерения согласно указанному способу
4. Определяйте тип предела строго по шаблонам:
   - "не более X" -> max
   - "не менее X" -> min
   - "X-Y" или "X÷Y" -> range
   - просто "X" -> exact
5. Химические формулы:
   - Сохраняйте точное написание (H₂, CO₂, CH₄ и т.д.)
   - Не изменяйте индексы и регистр
   - Сохраняйте все знаки и символы
6. Значения:
   - Сохраняйте точное написание чисел (0,001 а не 0.001)
   - Сохраняйте все разделители как в оригинале
   - Диапазоны записывайте точно как в исходнике
7. Не добавляйте параметры, которых нет в исходных данных
8. Не дублируйте параметры
9. Обрабатывайте все строки из чанка

Верните данные строго по шаблону.""".format(
        json.dumps(structure, ensure_ascii=False, indent=2),
        json.dumps(template, ensure_ascii=False, indent=2),
        start_idx + 1,
        end_idx,
        chunk_text
    )

    return client.create(extraction_prompt)

def extract_table_data(data: List[List[str]]) -> Dict[str, Any]:
    """Extract and process table data."""
    try:
        results = {
            "materials": [],
            "groups": []
        }
        
        current_material = None
        current_parameter = None
        
        for row_idx, row in enumerate(data, 1):
            try:
                if not row or all(not cell.strip() for cell in row):
                    continue
                
                # Clean row data
                row = [str(cell).replace('\n', ' ').strip() for cell in row]
                
                # Check if this is a material row (starts with a number like "1.", "2.", etc.)
                if row[0] and re.match(r'^\d+\.?$', row[0].strip()):
                    if current_material:
                        results["materials"].append(current_material)
                    
                    current_material = {
                        "row_number": row_idx,
                        "number": row[0].strip(),
                        "name": row[1].strip() if len(row) > 1 and row[1] else "",
                        "standard": row[2].strip() if len(row) > 2 and row[2] else "",
                        "parameters": [],
                        "application": row[5].strip() if len(row) > 5 and row[5] else ""
                    }
                    current_parameter = None
                
                # Check if this is a parameter row
                elif current_material and row[3].strip() and not row[0].strip():
                    parameter = {
                        "name": row[3].strip(),
                        "value": row[4].strip() if len(row) > 4 and row[4] else "",
                        "unit": "",  # Will be extracted from value or name
                        "limit_type": "exact"  # Default, will be updated based on patterns
                    }
                    
                    # Extract unit and limit type from value
                    if parameter["value"]:
                        # Check for limit type
                        if "не более" in parameter["value"].lower():
                            parameter["limit_type"] = "max"
                        elif "не менее" in parameter["value"].lower():
                            parameter["limit_type"] = "min"
                        elif "-" in parameter["value"] or "÷" in parameter["value"]:
                            parameter["limit_type"] = "range"
                        
                        # Extract unit
                        unit_match = re.search(r'(?:^|\s)([%°С]\s*(?:об\.|масс\.|вес\.|мол\.)?|(?:г|кг|м3|МПа|кПа|Па|мм|см|м|л)\s*/\s*(?:г|кг|м3|МПа|кПа|Па|мм|см|м|л)|[%°С]|(?:г|кг|м3|МПа|кПа|Па|мм|см|м|л))', parameter["value"])
                        if unit_match:
                            parameter["unit"] = unit_match.group(1).strip()
                            parameter["value"] = parameter["value"].replace(parameter["unit"], "").strip()
                    
                    current_material["parameters"].append(parameter)
                    current_parameter = parameter
                
                # Check if this is a continuation row
                elif current_material and any(cell.strip() for cell in row):
                    # If it's a continuation of the material name
                    if row[1].strip() and not row[3].strip():
                        current_material["name"] += " " + row[1].strip()
                    # If it's a continuation of the standard
                    if row[2].strip() and not row[3].strip():
                        current_material["standard"] += " " + row[2].strip()
                    # If it's a continuation of the application
                    if row[5].strip():
                        current_material["application"] += " " + row[5].strip()
                    # If it's a continuation of the parameter
                    if row[3].strip() and current_parameter:
                        current_parameter["name"] += " " + row[3].strip()
                    if row[4].strip() and current_parameter:
                        current_parameter["value"] += " " + row[4].strip()
            
            except Exception as row_error:
                logging.warning(f"Error processing row {row_idx}: {str(row_error)}")
                continue
        
        # Don't forget to add the last material
        if current_material:
            results["materials"].append(current_material)
        
        return results
    except Exception as e:
        logging.error(f"Error extracting table data: {str(e)}")
        return {"materials": [], "groups": []}

def analyze_csv_with_rag(client: DirectClient, csv_path: str) -> Dict[str, Any]:
    """Анализирует CSV файл по стратегии: структура -> шаблон -> данные."""
    try:
        # Читаем файл
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        # Шаг 1: Анализ заголовков и связей
        logger.info("Анализ структуры заголовков и связей...")
        structure = analyze_headers_and_relationships(client, headers, rows)
        if "error" in structure:
            return structure
        
        # Шаг 2: Создание шаблона
        logger.info("Создание шаблона данных...")
        template = create_json_template(structure)
        
        # Шаг 3: Извлечение данных
        logger.info("Извлечение данных...")
        data = extract_table_data(rows)
        if "error" in data:
            return data
        
        # Объединяем результаты
        result = {
            "structure": structure,
            "data": data
        }
        
        # Проверяем результаты
        warnings = validate_extracted_data(result, len(rows))
        if warnings:
            result["warnings"] = warnings
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при анализе CSV: {e}")
        return {"error": str(e)}

def validate_extracted_data(result: Dict[str, Any], total_rows: int) -> List[str]:
    """Проверяет полноту и корректность извлеченных данных."""
    warnings = []
    
    if "data" not in result:
        warnings.append("Отсутствуют данные")
        return warnings
    
    data = result["data"]
    if "materials" not in data:
        warnings.append("Отсутствует секция materials")
        return warnings
    
    # Проверяем обработанные строки
    processed_rows = set()
    for material in data["materials"]:
        if "row_number" in material:
            processed_rows.add(material["row_number"])
        
        # Проверяем обязательные поля
        required_fields = ["name", "parameters"]
        missing_fields = [f for f in required_fields if f not in material]
        if missing_fields:
            warnings.append(f"Строка {material.get('row_number', '?')}: отсутствуют поля {', '.join(missing_fields)}")
        
        # Проверяем параметры
        if "parameters" in material:
            for idx, param in enumerate(material["parameters"]):
                required_param_fields = ["name", "value"]
                missing_param_fields = [f for f in required_param_fields if f not in param]
                if missing_param_fields:
                    warnings.append(
                        f"Строка {material.get('row_number', '?')}, параметр {idx + 1}: "
                        f"отсутствуют поля {', '.join(missing_param_fields)}"
                    )
    
    # Проверяем пропущенные строки
    missing_rows = sorted(set(range(1, total_rows + 1)) - processed_rows)
    if missing_rows:
        warnings.append(f"Не обработаны строки: {missing_rows}")
    
    return warnings

def format_analysis_output(result_json: Dict[str, Any], output_file) -> None:
    """Форматирует и записывает результаты анализа в файл."""
    
    def write_section(title: str):
        output_file.write(f"\n{'='*50}\n{title}\n{'='*50}\n")
    
    def write_subsection(title: str):
        output_file.write(f"\n{'-'*30}\n{title}\n{'-'*30}\n")
    
    # 1. Структура таблицы
    write_section("СТРУКТУРА ТАБЛИЦЫ")
    if "structure" in result_json:
        structure = result_json["structure"]
        
        # Основные колонки
        write_subsection("Основные колонки")
        main_cols = structure.get("main_columns", {})
        output_file.write(f"Название материала: столбец {main_cols.get('material_name', '?')}\n")
        output_file.write(f"Стандарт/ТУ: столбец {main_cols.get('standard', '?')}\n")
        output_file.write(f"Область применения: столбец {main_cols.get('application', '?')}\n")
        
        # Колонки параметров
        write_subsection("Колонки параметров")
        param_cols = structure.get("parameter_columns", {})
        output_file.write(f"Название параметра: столбец {param_cols.get('name', '?')}\n")
        output_file.write(f"Значение параметра: столбец {param_cols.get('value', '?')}\n")
        output_file.write(f"Способ извлечения единиц измерения: {param_cols.get('unit_extraction', '?')}\n")
        
        # Связи между строками
        write_subsection("Связи между строками")
        row_rels = structure.get("row_relationships", {})
        output_file.write(f"Тип связи: {row_rels.get('type', '?')}\n")
        if "rules" in row_rels:
            output_file.write("\nПравила связей:\n")
            for rule in row_rels["rules"]:
                output_file.write(f"- {rule}\n")
    
    # 2. Извлеченные данные
    write_section("ИЗВЛЕЧЕННЫЕ ДАННЫЕ")
    if "data" in result_json and "materials" in result_json["data"]:
        materials = result_json["data"]["materials"]
        materials.sort(key=lambda x: x.get("row_number", 0))
        
        for material in materials:
            write_subsection(f"Строка {material.get('row_number', '?')}")
            
            # Основная информация
            output_file.write(f"Наименование: {material.get('name', '')}\n")
            if material.get('standard'):
                output_file.write(f"Стандарт/ТУ: {material['standard']}\n")
            
            # Параметры
            if "parameters" in material and material["parameters"]:
                output_file.write("\nПараметры:\n")
                for param in material["parameters"]:
                    output_file.write(f"\n  • {param.get('name', '')}\n")
                    output_file.write(f"    Значение: {param.get('value', '')}\n")
                    if param.get('unit'):
                        output_file.write(f"    Единица измерения: {param['unit']}\n")
                    if param.get('limit_type'):
                        output_file.write(f"    Тип предела: {param['limit_type']}\n")
                    if param.get('notes'):
                        output_file.write(f"    Примечания: {param['notes']}\n")
            
            # Область применения
            if material.get('application'):
                output_file.write(f"\nОбласть применения: {material['application']}\n")
    
    # 3. Предупреждения
    if "warnings" in result_json and result_json["warnings"]:
        write_section("ПРЕДУПРЕЖДЕНИЯ")
        for warning in result_json["warnings"]:
            output_file.write(f"! {warning}\n")
    
    # 4. Статистика
    write_section("СТАТИСТИКА")
    if "data" in result_json and "materials" in result_json["data"]:
        materials = result_json["data"]["materials"]
        total_materials = len(materials)
        total_parameters = sum(len(m.get("parameters", [])) for m in materials)
        
        output_file.write(f"Всего материалов: {total_materials}\n")
        output_file.write(f"Всего параметров: {total_parameters}\n")
        output_file.write(f"Среднее количество параметров на материал: {total_parameters/total_materials:.1f}\n")

def save_results(results: Dict[str, Any], output_dir: str, base_filename: str) -> None:
    """Save analysis results to files."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON results
        json_path = os.path.join(output_dir, f"{base_filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        # Save text results
        txt_path = os.path.join(output_dir, f"{base_filename}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            format_analysis_output(results, f)
            
        logging.info(f"\nРезультаты сохранены в:\n- JSON: {json_path}\n- Текст: {txt_path}")
    except Exception as e:
        logging.error(f"Error saving results: {str(e)}")

def process_csv_data(data: List[List[str]]) -> Dict[str, Any]:
    """Process CSV data safely."""
    try:
        if not data or not isinstance(data, list):
            raise ValueError("Invalid CSV data")
            
        # Process the data
        results = {"materials": []}
        
        for row in data:
            try:
                if not row or len(row) < 3:  # Minimum required fields
                    continue
                    
                material = {
                    "name": row[0].strip() if row[0] else "",
                    "parameters": []
                }
                
                # Process parameters if they exist
                if len(row) > 3:
                    param = {
                        "name": row[2].strip() if row[2] else "",
                        "value": row[3].strip() if len(row) > 3 and row[3] else "не указано",
                        "unit": row[4].strip() if len(row) > 4 and row[4] else "не указано"
                    }
                    material["parameters"].append(param)
                
                results["materials"].append(material)
            except Exception as row_error:
                logging.warning(f"Error processing row: {str(row_error)}")
                continue
        
        return results
    except Exception as e:
        logging.error(f"Error processing CSV data: {str(e)}")
        return {"materials": []}

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

    # Анализируем CSV
    result_json = analyze_csv_with_rag(client, csv_path)
    
    # Сохраняем результат в JSON
    json_output_path = os.path.join(output_dir, f"table_analysis_{page_suffix}.json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    
    # Сохраняем в текстовом виде
    txt_output_path = os.path.join(output_dir, f"table_analysis_{page_suffix}.txt")
    with open(txt_output_path, 'w', encoding='utf-8') as f:
        format_analysis_output(result_json, f)

    # Выводим статистику
    print("\n=== АНАЛИЗ ЗАВЕРШЕН ===")
    print(f"\nРезультаты сохранены в:")
    print(f"- JSON: {json_output_path}")
    print(f"- Текст: {txt_output_path}")
    
    if "grouped_data" in result_json:
        groups = result_json["grouped_data"]
        total_rows = sum(len(items) for items in groups.values())
        total_indicators = sum(
            sum(len(item.get("indicators", [])) for item in items if isinstance(item, dict))
            for items in groups.values()
        )
        
        print(f"\nСтатистика обработки:")
        print(f"- Групп: {len(groups)}")
        print(f"- Строк: {total_rows}")
        print(f"- Показателей: {total_indicators}")
        
        if "warning" in result_json:
            print(f"\nПредупреждения:")
            for line in result_json["warning"].split("\n"):
                print(f"- {line}")