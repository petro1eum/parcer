import os
import json
import glob
import pandas as pd
from typing import Dict, Any
import pdfplumber
from PIL import Image
import base64
from openai import OpenAI
import csv

# Инициализация клиента OpenAI
client = OpenAI()

def analyze_pages_connection(current_page_img: str, next_page_img: str) -> Dict[str, Any]:
    """
    Отправляет изображения двух страниц в GPT и просит определить, является ли
    таблица на второй странице продолжением таблицы с первой страницы.
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

    1. Размерность таблиц ДОЛЖНА быть идентичной:
    - То же количество столбцов (даже если в качестве заголовков используются цифры 1,2,3...)
    - Если в первой таблице есть цифры-номера столбцов (1,2,3...), то во второй таблице 
        должны быть те же номера в том же порядке
    - Заголовки могут:
        * Полностью отсутствовать
        * Быть заменены на цифры
        * Быть оригинальными
    НО количество столбцов И нумерация (если есть) должны ТОЧНО совпадать!

    2. Содержимое должно быть логически связано:
    - Продолжается нумерация строк
    - Или продолжается логическая последовательность данных

    Дополнительные признаки (НЕ ОБЯЗАТЕЛЬНЫЕ):
    - Текст "Продолжение таблицы X"
    - Или "Продолжение" над таблицей

    ВАЖНО! На второй странице НЕ ДОЛЖНО быть:
    - Нового названия "Таблица ..."
    - Измененной структуры (другого количества столбцов)
    - Другой нумерации столбцов (если они пронумерованы)

    Если разное количество столбцов или не совпадает нумерация - это ГАРАНТИРОВАННО разные таблицы!

    В поле reason укажи КОНКРЕТНУЮ причину принятого решения.
    В поле same_dimensions укажи, совпадает ли количество столбцов И нумерация (если есть).

    ВАЖНО: Верни только JSON, без лишнего текста!'''
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
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # или другая доступная модель
            messages=[system_msg, user_msg],
            max_tokens=150,
        )
        response_text = resp.choices[0].message.content.strip()
        
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                json_data = json.loads(json_str)
                # Проверяем наличие обязательных полей
                required_fields = ['is_continuation', 'table_title', 'reason', 'same_dimensions']
                if not all(field in json_data for field in required_fields):
                    print(f"В ответе GPT отсутствуют обязательные поля: {response_text}")
                    return {"is_continuation": False, "table_title": "", "reason": "Invalid response", "same_dimensions": False}
                return json_data
        except json.JSONDecodeError:
            print(f"Невалидный JSON в ответе GPT: {response_text}")
            return {"is_continuation": False, "table_title": "", "reason": "Invalid JSON", "same_dimensions": False}
            
    except Exception as e:
        print(f"Ошибка при анализе страниц: {str(e)}")
        return {"is_continuation": False, "table_title": "", "reason": str(e), "same_dimensions": False}

def encode_image_to_base64(image_path: str) -> str:
    """Кодирует изображение в base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_page_image(pdf_path: str, page_num: int, output_folder: str) -> str:
    """Создает изображение страницы PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]
        img = page.to_image()
        img_path = os.path.join(output_folder, f'temp_page_{page_num}.png')
        img.save(img_path)
        return img_path

def get_page_number(filename):
    """Извлекает номер страницы из имени файла: page_6_tables.csv -> 6"""
    return int(filename.split('page_')[1].split('_')[0])

def generate_summary(df: pd.DataFrame, output_file: str, input_folder: str) -> None:
    """
    Генерирует описание таблицы, используя соответствующий текстовый файл и GPT.
    """
    print(f"\nГенерация описания для файла: {output_file}")
    
    # Определяем номер первой страницы из имени файла
    if 'merged_page_' in output_file:
        page_num = output_file.split('merged_page_')[1].split('-')[0]
        print(f"Это объединенная таблица, берем номер первой страницы: {page_num}")
    else:
        page_num = output_file.split('page_')[1].split('_')[0]
        print(f"Это одиночная таблица, номер страницы: {page_num}")
    
    # Ищем соответствующий текстовый файл
    text_file = os.path.join(input_folder, f'page_{page_num}_text.txt')
    print(f"Ищем текстовый файл: {text_file}")
    
    if not os.path.exists(text_file):
        print(f"  ОШИБКА: Текстовый файл не найден: {text_file}")
        return
    
    print(f"Текстовый файл найден")
        
    # Читаем содержимое текстового файла
    with open(text_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    print(f"Прочитано {len(text_content)} символов из текстового файла")
    print(f"Начало текста: {text_content[:200]}...")
    
    # Формируем запрос к GPT
    system_msg = {
        "role": "system",
        "content": (
            "Ты должен найти название и описание таблицы в тексте и вернуть его в виде 2-3 предложений. "
            "Описание должно объяснять содержимое и назначение таблицы. "
            "Не включай статистику или технические детали. "
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
        )
        description = resp.choices[0].message.content.strip()
        
        # Сохраняем описание в файл
        summary_file = output_file.replace('.csv', '_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as sf:
            sf.write(description)
        print(f"  Файл с описанием таблицы сохранён в {summary_file}")
        
    except Exception as e:
        print(f"  ОШИБКА при генерации описания: {str(e)}")

def merge_connected_tables(input_folder: str, pdf_path: str):
    """
    Проходит по всем CSV файлам последовательно и объединяет связанные таблицы.
    Исправлены:
     - "сдвиг влево" (убрана принудительная вырезка первой строки)
     - исключение слияния таблиц с одной и той же страницы
     - добавлен вывод краткого описания (summary) каждой итоговой таблицы
    """
    print("\nНачинаем обработку CSV файлов...")
    csv_files = glob.glob(os.path.join(input_folder, 'page_*_tables.csv'))
    # Сортируем по номеру страницы
    csv_files = sorted(csv_files, key=get_page_number)
    
    if not csv_files:
        print("CSV файлы не найдены")
        return
    
    print(f"Найдено файлов: {len(csv_files)}")
    print("Порядок обработки файлов:")
    for f in csv_files:
        print(f"  Страница {get_page_number(f)}: {f}")
    
    temp_folder = os.path.join(input_folder, 'temp_images')
    os.makedirs(temp_folder, exist_ok=True)
    
    try:
        # Добавляем множество для отслеживания обработанных страниц
        processed_pages = set()
        
        current_idx = 0
        while current_idx < len(csv_files):
            current_file = csv_files[current_idx]
            current_page = get_page_number(current_file)
            
            # Пропускаем уже обработанные страницы
            if current_page in processed_pages:
                current_idx += 1
                continue
                
            print(f"\nПроверяем страницу {current_page} ({current_file})")
            
            # Начинаем собирать связанные таблицы
            connected_files = [current_file]
            
            # Проверяем следующие страницы по порядку
            next_page = current_page + 1
            while True:
                next_file = os.path.join(input_folder, f'page_{next_page}_tables.csv')
                
                # Если следующего файла нет - прерываем проверку
                if not os.path.exists(next_file):
                    print(f"  Файл страницы {next_page} не существует, прерываем проверку")
                    break
                
                # Если это та же страница (что бывает редко, но всё же) — 
                # значит там просто другая таблица, не надо объединять
                if get_page_number(next_file) == current_page:
                    print(f"  Файл страницы {current_page} повторяется (другая таблица?), не объединяем")
                    break

                print(f"  Проверяем связь со страницей {next_page}")
                
                try:
                    # Создаем изображения для проверки
                    current_img = create_page_image(pdf_path, current_page, temp_folder)
                    next_img = create_page_image(pdf_path, next_page, temp_folder)
                    
                    # Проверяем связь между страницами
                    result = analyze_pages_connection(current_img, next_img)
                    print(f"  Результат проверки: {result}")
                    
                    # Удаляем временные изображения
                    os.remove(current_img)
                    os.remove(next_img)
                    
                    if result["is_continuation"] and result["same_dimensions"]:
                        print(f"  Страница {next_page} является продолжением")
                        connected_files.append(next_file)
                        current_page = next_page
                        next_page += 1
                    else:
                        print(f"  Страница {next_page} НЕ является продолжением: {result['reason']}")
                        break
                except Exception as e:
                    print(f"  ОШИБКА при проверке страниц {current_page} и {next_page}: {str(e)}")
                    break
            
            # Если нашли связанные таблицы - объединяем их
            if len(connected_files) > 1:
                for file in connected_files:
                    processed_pages.add(get_page_number(file))
                    
                first_page = get_page_number(connected_files[0])
                last_page = get_page_number(connected_files[-1])
                output_file = os.path.join(input_folder, f'merged_page_{first_page}-{last_page}_tables.csv')
                
                print(f"\nОбъединяем таблицы со страниц {first_page}-{last_page}")
                print(f"Файлы для объединения: {connected_files}")
                
                try:
                    all_data = []
                    # Читаем первую таблицу
                    first_df = pd.read_csv(connected_files[0])
                    num_columns = len(first_df.columns)
                    headers = first_df.columns.tolist()
                    print(f"\nПервая таблица:")
                    print(f"  Количество столбцов: {num_columns}")
                    print(f"  Заголовки: {headers}")
                    all_data.append(first_df)
                    
                    for file in connected_files[1:]:
                        print(f"\nЧитаем файл: {file}")
                        df = pd.read_csv(file)
                        print(f"  Прочитано столбцов: {len(df.columns)}")
                        print(f"  Первые несколько строк:")
                        print(df.head())
                        
                        # Проверяем количество столбцов
                        if len(df.columns) != num_columns:
                            print(f"\n  НЕСОВПАДЕНИЕ СТОЛБЦОВ:")
                            print(f"    Ожидается: {num_columns}")
                            print(f"    Получено: {len(df.columns)}")
                            print(f"    Пытаемся исправить через GPT...")
                            
                            df = fix_split_columns(df, num_columns)
                            print(f"\n  После исправления:")
                            print(f"    Столбцов: {len(df.columns)}")
                            print(f"    Данные:")
                            print(df.head())
                            
                            # Проверяем результат исправления
                            if len(df.columns) != num_columns:
                                print(f"\n  ОШИБКА: Не удалось исправить столбцы!")
                                raise ValueError(f"Не удалось исправить несовпадение столбцов в файле {file}")
                            else:
                                print(f"  Столбцы успешно исправлены")
                        
                        # Присваиваем те же названия столбцов, что и в первой таблице
                        df.columns = headers
                        all_data.append(df)
                    
                    result_df = pd.concat(all_data, ignore_index=True)
                    print(f"  Итоговая таблица: {len(result_df)} строк, {len(result_df.columns)} столбцов")
                    result_df.to_csv(output_file, index=False)
                    print(f"  Сохранено в {output_file}")
                    
                    # Генерация краткого описания
                    generate_summary(result_df, output_file, input_folder)
                    
                except Exception as e:
                    print(f"  ОШИБКА при объединении таблиц: {str(e)}")
                
                # Переходим к следующей непроверенной странице
                current_idx = csv_files.index(connected_files[-1]) + 1
            else:
                processed_pages.add(current_page)
                # Если связей не нашли - просто создаём summary для одиночного файла
                df_single = pd.read_csv(current_file)
                generate_summary(df_single, current_file, input_folder)
                
                print("  Нет связанных таблиц (или только одна). Summary создано.")
                # Переходим к следующему файлу
                current_idx += 1
                
    finally:
        # Очищаем временную папку
        if os.path.exists(temp_folder):
            for file in os.listdir(temp_folder):
                os.remove(os.path.join(temp_folder, file))
            os.rmdir(temp_folder)
        print("\nОбработка завершена")

def fix_split_columns(df: pd.DataFrame, expected_columns: int) -> pd.DataFrame:
    """
    Пытается исправить разъехавшиеся столбцы сначала через эвристики, затем через GPT.
    """
    if len(df.columns) <= expected_columns:
        return df
        
    # Сначала пробуем простой способ с Unnamed columns
    unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
    if unnamed_cols:
        for unnamed_col in unnamed_cols:
            cols = df.columns.tolist()
            current_idx = cols.index(unnamed_col)
            if current_idx > 0:
                prev_col = cols[current_idx - 1]
                df[prev_col] = df[prev_col].astype(str) + ' ' + df[unnamed_col].fillna('').astype(str)
                df[prev_col] = df[prev_col].replace('nan nan', '').str.strip()
                df = df.drop(columns=[unnamed_col])
    
    # Если все еще неправильное количество столбцов - используем GPT
    if len(df.columns) != expected_columns:
        # print(f"\n  НЕСОВПАДЕНИЕ СТОЛБЦОВ:")
        # print(f"    Ожидается: {expected_columns}")
        # print(f"    Получено: {len(df.columns)}")
        # print(f"    Пытаемся исправить через GPT...")
        
        system_msg = {
            "role": "system",
            "content": """Проанализируй таблицу и верни только JSON в формате:
{
    "merge_columns": [
        {
            "columns": ["имя_столбца1", "имя_столбца2"],
            "target_column": "имя_целевого_столбца"
        }
    ]
}"""
        }
        
        sample_data = df.head().to_string()
        user_msg = {
            "role": "user",
            "content": f"В таблице {len(df.columns)} столбцов, нужно получить {expected_columns}.\nСтолбцы: {df.columns.tolist()}\nДанные:\n{sample_data}"
        }
        
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[system_msg, user_msg],
                max_tokens=150,
            )
            fix_instructions = json.loads(resp.choices[0].message.content)
            
            for merge_group in fix_instructions['merge_columns']:
                cols_to_merge = merge_group['columns']
                target_col = merge_group['target_column']
                print(f"  GPT предлагает объединить {cols_to_merge} в {target_col}")
                df[target_col] = df[cols_to_merge].apply(
                    lambda x: ' '.join(x.dropna().astype(str)).strip(), axis=1
                )
                for col in cols_to_merge:
                    if col != target_col:
                        df = df.drop(columns=[col])
                        
        except Exception as e:
            print(f"  ОШИБКА при использовании GPT: {str(e)}")
    
    return df

if __name__ == "__main__":
    input_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/output"
    pdf_path = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/input/Инструкция Т-108 К-10 и метанирование 2021.pdf"
    
    merge_connected_tables(input_folder, pdf_path)