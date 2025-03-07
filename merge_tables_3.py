import os
import csv
import pdfplumber
import json
import glob
import pandas as pd
from typing import Dict, Any
from PIL import Image
import base64
from openai import OpenAI

# ---------------------------
# Настройка OpenAI: 
#   Способ 1: установите переменную окружения OPENAI_API_KEY
#       export OPENAI_API_KEY="ваш_ключ"
#   Способ 2: пропишите ключ непосредственно:
#       openai.api_key = "ваш_ключ"
# ---------------------------
client = OpenAI()

# openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_content_from_pdf_no_duplicate(input_file: str, output_folder: str):
    """
    Извлекает постранично из PDF:
      - Текст (без текста таблиц), сохраняя в page_{N}_text.txt
      - Таблицы (если есть), сохраняя в page_{N}_tables.csv
    """
    with pdfplumber.open(input_file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # 1) Ищем все таблицы на странице
            tables_on_page = page.find_tables()
            table_bboxes = [table.bbox for table in tables_on_page]  # bbox = (x0, top, x1, bottom)

            # 2) Извлекаем все слова на странице
            words = page.extract_words()
            
            # 3) Отфильтровываем слова, которые попадают в любую из таблиц (по bounding box)
            words_outside_tables = []
            for w in words:
                x0, y0, x1, y1 = w['x0'], w['top'], w['x1'], w['bottom']
                
                inside_any_table = False
                for (tb_x0, tb_top, tb_x1, tb_bottom) in table_bboxes:
                    # Если слово хоть чуть-чуть попадает в bbox таблицы, считаем, что оно "внутри"
                    if (x0 >= tb_x0 and x1 <= tb_x1 and
                        y0 >= tb_top and y1 <= tb_bottom):
                        inside_any_table = True
                        break
                if not inside_any_table:
                    words_outside_tables.append(w)

            # 4) Склеиваем слова, чтобы получить "беглый" текст страницы без таблиц
            filtered_text = " ".join([w['text'] for w in words_outside_tables])
            filtered_text = filtered_text.strip()
            
            if filtered_text:
                text_filename = os.path.join(output_folder, f'page_{page_num}_text.txt')
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(filtered_text)

            # 5) Извлекаем данные таблиц стандартным методом extract_tables()
            tables_data = page.extract_tables()
            if tables_data:
                tables_filename = os.path.join(output_folder, f'page_{page_num}_tables.csv')
                with open(tables_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for table in tables_data:
                        writer.writerows(table)

def analyze_pages_connection(current_page_img: str, next_page_img: str) -> Dict[str, Any]:
    """
    Сравнивает изображения двух страниц (current_page_img, next_page_img), 
    отправляет их в GPT-4 (через модель gpt-4o-mini), чтобы определить,
    является ли таблица на второй странице продолжением таблицы на первой.
    """
    base64_current = encode_image_to_base64(current_page_img)
    base64_next = encode_image_to_base64(next_page_img)

    system_msg = {
        'role': 'system',
        'content': '''Верни только JSON с четырьмя полями:
{
    "is_continuation": true/false,
    "table_title": "Название исходной таблицы",
    "reason": "Причина принятого решения",
    "same_dimensions": true/false
}

ПРАВИЛА определения продолжения таблицы:
1) Одинаковое количество столбцов, совпадающие заголовки/нумерация (если есть).
2) Продолжение нумерации строк или логической последовательности данных.

Если разное количество столбцов или не совпадает нумерация - это точно разные таблицы!
Верни только JSON, без лишнего текста!'''
    }

    user_msg = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Верни JSON с полями is_continuation, table_title, reason и same_dimensions"
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_current}"},
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_next}"},
            },
        ],
    }

    try:
        # Не меняем model="gpt-4o-mini" — как просили.
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_msg, user_msg],
            max_tokens=150,
            temperature=0.0
        )
        response_text = resp.choices[0].message.content.strip()
        
        # Ищем JSON в ответе
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = response_text[start:end]
            try:
                json_data = json.loads(json_str)
                required_fields = ['is_continuation', 'table_title', 'reason', 'same_dimensions']
                if not all(field in json_data for field in required_fields):
                    print(f"В ответе GPT отсутствуют обязательные поля: {response_text}")
                    return {
                        "is_continuation": False,
                        "table_title": "",
                        "reason": "Invalid response",
                        "same_dimensions": False
                    }
                return json_data
            except json.JSONDecodeError:
                print(f"Невалидный JSON в ответе GPT: {response_text}")
                return {
                    "is_continuation": False,
                    "table_title": "",
                    "reason": "Invalid JSON",
                    "same_dimensions": False
                }
        
        print(f"Не удалось извлечь JSON из ответа GPT: {response_text}")
        return {
            "is_continuation": False,
            "table_title": "",
            "reason": "JSON not found",
            "same_dimensions": False
        }

    except Exception as e:
        print(f"Ошибка при анализе страниц: {str(e)}")
        return {
            "is_continuation": False,
            "table_title": "",
            "reason": str(e),
            "same_dimensions": False
        }

def encode_image_to_base64(image_path: str) -> str:
    """Кодирует указанное изображение PNG в base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_page_image(pdf, page_num: int, output_folder: str) -> str:
    """
    Создает PNG-изображение заданной страницы (page_num) PDF-файла (pdfplumber-объект)
    и сохраняет его во временную папку output_folder (тем самым создаёт "temp_page_{N}.png").
    Возвращает путь к изображению.
    """
    if page_num < 1 or page_num > len(pdf.pages):
        raise ValueError(f"Страница {page_num} отсутствует в PDF. Всего страниц: {len(pdf.pages)}.")

    page = pdf.pages[page_num - 1]
    page_img = page.to_image()
    img_path = os.path.join(output_folder, f'temp_page_{page_num}.png')
    page_img.save(img_path)
    return img_path

def get_page_number(filename: str) -> int:
    """Извлекает номер страницы из имени CSV-файла вида: page_6_tables.csv -> 6"""
    return int(filename.split('page_')[1].split('_')[0])

def generate_summary(df: pd.DataFrame, output_file: str, input_folder: str) -> None:
    """
    Генерирует краткое описание (summary) таблицы, используя GPT и текст со страницы (page_X_text.txt).
    Сохраняет описание в файл {имя CSV}_summary.txt.
    """
    print(f"\nГенерация описания для файла: {output_file}")
    
    # Понять страницу (или диапазон) из имени файла
    if 'merged_page_' in output_file:
        page_num = output_file.split('merged_page_')[1].split('-')[0]
        print(f"Это объединенная таблица, берём номер первой страницы: {page_num}")
    else:
        page_num = output_file.split('page_')[1].split('_')[0]
        print(f"Это одиночная таблица, номер страницы: {page_num}")
    
    # Пытаемся найти соответствующий текстовый файл
    text_file = os.path.join(input_folder, f'page_{page_num}_text.txt')
    print(f"Ищем текстовый файл: {text_file}")
    
    if not os.path.exists(text_file):
        print(f"  ОШИБКА: Текстовый файл не найден: {text_file}")
        return
    
    print(f"Текстовый файл найден.")
    with open(text_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    print(f"Прочитано {len(text_content)} символов из текстового файла.")
    
    system_msg = {
        "role": "system",
        "content": (
            "Ты должен найти название и краткое описание таблицы в тексте и вернуть его в 2-3 предложениях. "
            "Сформулируй общую суть и назначение, без перечисления технических деталей."
        )
    }
    user_msg = {
        "role": "user",
        "content": f"Найди описание таблицы в следующем тексте:\n\n{text_content}"
    }
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_msg, user_msg],
            max_tokens=150,
            temperature=0.1
        )
        description = resp.choices[0].message.content.strip()
        
        summary_file = output_file.replace('.csv', '_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as sf:
            sf.write(description)
        print(f"  Файл с описанием таблицы сохранён в: {summary_file}")
        
    except Exception as e:
        print(f"  ОШИБКА при генерации описания: {str(e)}")

def merge_connected_tables(pdf, input_folder: str):
    """
    Проходит по всем CSV-файлам (page_*_tables.csv), объединяет таблицы, 
    которые GPT распознал как продолжения, и генерирует summary.
    """
    print("\nНачинаем обработку CSV-файлов...")
    csv_files = glob.glob(os.path.join(input_folder, 'page_*_tables.csv'))
    csv_files = sorted(csv_files, key=get_page_number)
    
    if not csv_files:
        print("CSV-файлы не найдены. Завершаем работу.")
        return
    
    print(f"Найдено файлов: {len(csv_files)}")
    print("Порядок обработки файлов:")
    for f in csv_files:
        print(f"  Страница {get_page_number(f)}: {f}")
    
    temp_folder = os.path.join(input_folder, 'temp_images')
    os.makedirs(temp_folder, exist_ok=True)
    
    try:
        processed_pages = set()
        current_idx = 0
        
        while current_idx < len(csv_files):
            current_file = csv_files[current_idx]
            current_page = get_page_number(current_file)
            
            if current_page in processed_pages:
                current_idx += 1
                continue
            
            print(f"\nПроверяем страницу {current_page} ({current_file})")
            connected_files = [current_file]
            
            # Ищем таблицы на следующих страницах
            next_page = current_page + 1
            while True:
                next_file = os.path.join(input_folder, f'page_{next_page}_tables.csv')
                if not os.path.exists(next_file):
                    print(f"  Файл страницы {next_page} не существует. Прерываем проверку цепочки.")
                    break
                if get_page_number(next_file) == current_page:
                    print(f"  Файл страницы {current_page} повторяется (другая таблица?). Не объединяем.")
                    break
                
                print(f"  Проверяем связь со страницей {next_page}...")
                try:
                    current_img = create_page_image(pdf, current_page, temp_folder)
                    next_img = create_page_image(pdf, next_page, temp_folder)
                    
                    result = analyze_pages_connection(current_img, next_img)
                    print(f"  Результат проверки: {result}")
                    
                    # Удаляем временные изображения
                    if os.path.exists(current_img):
                        os.remove(current_img)
                    if os.path.exists(next_img):
                        os.remove(next_img)
                    
                    if result["is_continuation"] and result["same_dimensions"]:
                        print(f"  Страница {next_page} является продолжением таблицы со стр. {current_page}")
                        connected_files.append(next_file)
                        current_page = next_page
                        next_page += 1
                    else:
                        print(f"  Страница {next_page} НЕ является продолжением: {result['reason']}")
                        break
                except Exception as e:
                    print(f"  ОШИБКА при проверке связи страниц {current_page} и {next_page}: {str(e)}")
                    break
            
            # Если список connected_files > 1, значит объединим
            if len(connected_files) > 1:
                for cf in connected_files:
                    processed_pages.add(get_page_number(cf))
                
                first_page = get_page_number(connected_files[0])
                last_page = get_page_number(connected_files[-1])
                output_file = os.path.join(input_folder, f'merged_page_{first_page}-{last_page}_tables.csv')
                
                print(f"\nОбъединяем таблицы со страниц {first_page}-{last_page}")
                print(f"Файлы для объединения: {connected_files}")
                
                try:
                    all_data = []
                    first_df = pd.read_csv(connected_files[0], encoding='utf-8')
                    num_columns = len(first_df.columns)
                    headers = first_df.columns.tolist()
                    
                    all_data.append(first_df)
                    for file in connected_files[1:]:
                        df = pd.read_csv(file, encoding='utf-8')
                        
                        # Если не совпадает количество столбцов, пытаемся исправить
                        if len(df.columns) != num_columns:
                            print(f"  Несовпадение столбцов: есть {len(df.columns)}, ожидается {num_columns}. Пытаемся исправить...")
                            df = fix_split_columns(df, num_columns)
                            if len(df.columns) != num_columns:
                                raise ValueError(f"Не удалось исправить количество столбцов в {file}")
                        
                        # Выравниваем названия столбцов
                        df.columns = headers
                        all_data.append(df)
                    
                    result_df = pd.concat(all_data, ignore_index=True)
                    print(f"  Итоговая объединённая таблица: {len(result_df)} строк, {len(result_df.columns)} столбцов.")
                    result_df.to_csv(output_file, index=False, encoding='utf-8')
                    
                    # Генерируем summary
                    generate_summary(result_df, output_file, input_folder)
                    
                except Exception as e:
                    print(f"  ОШИБКА при объединении: {str(e)}")
                
                # Переходим сразу за последнюю объединённую
                current_idx = csv_files.index(connected_files[-1]) + 1
            
            else:
                # Нет продолжения, обрабатываем одиночную таблицу
                processed_pages.add(current_page)
                df_single = pd.read_csv(current_file, encoding='utf-8')
                generate_summary(df_single, current_file, input_folder)
                print("  Нет связанных таблиц. Summary создано.")
                current_idx += 1
                
    finally:
        # Удаляем временные изображения
        if os.path.exists(temp_folder):
            for file_name in os.listdir(temp_folder):
                full_path = os.path.join(temp_folder, file_name)
                if os.path.isfile(full_path):
                    os.remove(full_path)
            os.rmdir(temp_folder)
        print("\nОбработка завершена.")

def fix_split_columns(df: pd.DataFrame, expected_columns: int) -> pd.DataFrame:
    """
    Пытается исправить "разъехавшиеся" столбцы эвристически (объединяя Unnamed),
    а затем через GPT (не меняя model='gpt-4o-mini').
    Возвращает df с нужным количеством столбцов (если получилось).
    """
    if len(df.columns) == expected_columns:
        return df
    
    # 1) Пробуем объединить Unnamed-столбцы в предыдущий
    unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
    if unnamed_cols:
        for ucol in unnamed_cols:
            cols = df.columns.tolist()
            idx = cols.index(ucol)
            if idx > 0:
                prev_col = cols[idx - 1]
                df[prev_col] = df[prev_col].astype(str) + ' ' + df[ucol].fillna('').astype(str)
                df[prev_col] = df[prev_col].replace('nan nan', '').str.strip()
                df.drop(columns=[ucol], inplace=True)
    
    # 2) Если всё ещё много столбцов, пробуем GPT
    if len(df.columns) > expected_columns:
        print(f"  Применяем GPT для объединения столбцов...")
        system_msg = {
            "role": "system",
            "content": """Проанализируй структуру таблицы и верни JSON:
{
  "merge_columns": [
    {
      "columns": ["имя_столбца1", "имя_столбца2"],
      "target_column": "имя_итогового_столбца"
    },
    ...
  ]
}
Не добавляй лишний текст!"""
        }
        sample_data = df.head().to_string()
        user_msg = {
            "role": "user",
            "content": (
                f"В таблице {len(df.columns)} столбцов, требуется {expected_columns}.\n"
                f"Столбцы: {list(df.columns)}\n"
                f"Пример данных:\n{sample_data}\n"
                f"Верни только JSON!"
            )
        }
        
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[system_msg, user_msg],
                max_tokens=300,
                temperature=0.0
            )
            instructions = resp.choices[0].message.content.strip()
            
            fix_instructions = json.loads(instructions)
            merges = fix_instructions.get("merge_columns", [])
            
            for merge_group in merges:
                cols_to_merge = merge_group.get("columns", [])
                target_col = merge_group.get("target_column", "")
                
                missing = [c for c in cols_to_merge if c not in df.columns]
                if missing:
                    print(f"  GPT указал несуществующие столбцы: {missing}. Пропускаем эти.")
                    continue
                
                if target_col and target_col not in df.columns:
                    df[target_col] = ""
                
                for col in cols_to_merge:
                    if col == target_col:
                        continue
                    df[target_col] = df[target_col].astype(str) + " " + df[col].fillna("").astype(str)
                    df.drop(columns=[col], inplace=True)
                
                df[target_col] = df[target_col].replace('nan', '').str.strip()
                
        except Exception as e:
            print(f"  ОШИБКА при использовании GPT для исправления: {str(e)}")
    
    return df

if __name__ == "__main__":
    # Укажите путь к входному PDF и выходной папке
    input_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/input"
    output_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/output"
    
    # Ваш PDF-файл
    pdf_name = "Инструкция Т-108 К-10 и метанирование 2021.pdf"
    input_file = os.path.join(input_folder, pdf_name)

    # Создаем выходную папку (если нет)
    os.makedirs(output_folder, exist_ok=True)

    # ШАГ 1: Извлечь текст и таблицы из PDF (постранично)
    extract_content_from_pdf_no_duplicate(input_file, output_folder)

    # ШАГ 2: Открыть PDF и объединить таблицы, которые GPT распознает как продолжения
    with pdfplumber.open(input_file) as pdf:
        merge_connected_tables(pdf, output_folder)