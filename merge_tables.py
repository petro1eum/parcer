import os
import re
import csv
import glob
import pdfplumber
import pandas as pd
from typing import List
from openai import OpenAI

# Инициализация клиента OpenAI
client = OpenAI()

#######################################################
# 1) Функция извлечения из PDF (не меняем)
#######################################################

def extract_content_from_pdf_no_duplicate(input_pdf: str, output_folder: str):
    """
    Извлекает из PDF (постранично):
      - беглый текст (без таблиц) -> page_{N}_text.txt
      - таблицы (если есть)       -> page_{N}_tables.csv
    """
    os.makedirs(output_folder, exist_ok=True)
    with pdfplumber.open(input_pdf) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            tables_on_page = page.find_tables()
            if not tables_on_page:
                # Нет таблиц — сохраняем весь текст
                page_text = page.extract_text() or ""
                txt_path = os.path.join(output_folder, f"page_{page_index}_text.txt")
                with open(txt_path, "w", encoding="utf-8") as ft:
                    ft.write(page_text)
                continue
            
            # Есть таблицы — найдём bbox-ы
            table_bboxes = [t.bbox for t in tables_on_page]  # (x0, top, x1, bottom)
            words = page.extract_words() or []
            words_outside = []
            for w in words:
                x0, y0, x1, y1 = w['x0'], w['top'], w['x1'], w['bottom']
                inside_table = False
                for (tb_x0, tb_top, tb_x1, tb_bottom) in table_bboxes:
                    if (x0 >= tb_x0 and x1 <= tb_x1
                        and y0 >= tb_top and y1 <= tb_bottom):
                        inside_table = True
                        break
                if not inside_table:
                    words_outside.append(w)
            
            page_text_clean = " ".join([w["text"] for w in words_outside]).strip()
            if not page_text_clean:
                page_text_clean = page.extract_text() or ""
            
            txt_path = os.path.join(output_folder, f"page_{page_index}_text.txt")
            with open(txt_path, "w", encoding="utf-8") as ft:
                ft.write(page_text_clean)
            
            # Сохраняем таблицы (каждая extract_tables() -> list-of-list)
            table_data = page.extract_tables()
            if table_data:
                csv_path = os.path.join(output_folder, f"page_{page_index}_tables.csv")
                with open(csv_path, "w", newline="", encoding="utf-8") as fc:
                    writer = csv.writer(fc)
                    for tbl in table_data:
                        for row in tbl:
                            writer.writerow(row)
                        writer.writerow([])


#######################################################
# 2) Утилиты для пост-обработки CSV
#######################################################

def get_page_number(csv_filename: str) -> int:
    """
    'page_6_tables.csv' -> 6
    """
    base = os.path.basename(csv_filename)
    m = re.search(r'page_(\d+)_tables', base)
    return int(m.group(1)) if m else 999999

def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Читаем CSV (header=None), убираем полностью пустые строки, возвращаем DF.
    """
    df = pd.read_csv(csv_path, header=None, dtype=str, keep_default_na=False)
    # Удаляем полностью пустые строки
    df = df.dropna(how="all")
    # Удаляем те, где все ячейки пустые/пробельные
    df = df[~(df.apply(lambda row: ''.join(row.astype(str)).strip() == '', axis=1))]
    df = df.fillna('')
    return df

def remove_brackets_and_dots_around_number(s: str) -> str:
    """
    Превращаем '(1)', '1.', '(2)', '2)' => '1','1','2','2'.
    """
    s_strip = s.strip()
    # Добавляем точку в начале тоже, чтобы обработать случаи как "1." и ".1"
    pattern = r'^[\(\[\{\.]*([+-]?\d+(?:[.,]\d+)?)[\)\]\}\.]*$'
    m = re.match(pattern, s_strip)
    if m:
        return m.group(1).replace(',', '.')
    else:
        return s

def row_is_all_digits(row: List[str]) -> bool:
    """
    Проверяем, все ли элементы row — числа (после remove_brackets_and_dots_around_number).
    Пустые ячейки игнорируются.
    """
    if not row:
        return False
    
    non_empty_cells = [x for x in row if x.strip()]
    if not non_empty_cells:
        return False
        
    for x in non_empty_cells:
        x_clean = remove_brackets_and_dots_around_number(x)
        if not re.match(r'^[+-]?\d+(\.\d+)?$', x_clean.strip()):
            return False
    return True

def unify_empty_columns_in_first_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    *Главная функция*, убирающая "пустые" колонки
    в первой строке (деградированной шапке).
    
    Алгоритм:
      - Берём df.iloc[0] (первая строка), идём слева -> вправо:
        Если current == '' и left != '':
          Для всех строк i:
            df.iat[i, j-1] = df.iat[i, j-1] + "/" + df.iat[i, j]
          Удаляем столбец j
          (повторяем, пока больше нельзя слить)
    """
    if df.empty or df.shape[0] == 0 or df.shape[1] < 2:
        return df
    
    df2 = df.copy()
    changed = True
    while changed:
        changed = False
        if df2.shape[1] < 2:
            break
        
        first_row = df2.iloc[0].tolist()
        j = 1
        while j < df2.shape[1]:
            # Если слева есть, а тут пусто
            left_val = first_row[j-1].strip()
            curr_val = first_row[j].strip()
            if left_val != '' and curr_val == '':
                # "склеиваем" столбец j в j-1
                for i in range(df2.shape[0]):
                    left_cell = str(df2.iat[i, j-1]).strip()
                    curr_cell = str(df2.iat[i, j]).strip()
                    if left_cell and curr_cell:
                        merged = left_cell + "/" + curr_cell
                    else:
                        merged = left_cell if left_cell else curr_cell
                    df2.iat[i, j-1] = merged
                
                # Удаляем столбец j
                df2.drop(df2.columns[j], axis=1, inplace=True)
                df2.reset_index(drop=True, inplace=True)
                changed = True
                break
            else:
                j += 1

    return df2


#######################################################
# 3) Логика "слияния" таблиц
#######################################################

def merge_tables_in_folder(folder: str) -> List[str]:
    """
    Проходим по всем CSV-файлам 'page_*_tables.csv' по порядку:
      - Начинаем "группу" с первой, у которой строка #0 не numeric (это "настоящая" шапка).
      - Любая следующая страница, если #0 - "все цифры" (после очистки) => 
        считаем продолжением (сливаем пустые столбцы, убираем первую строку, concat).
      - Иначе — начинаем новую группу.

    Итог: merged_page_{start}-{end}.csv
    Возвращает: список использованных файлов
    """
    csv_files = glob.glob(os.path.join(folder, "page_*_tables.csv"))
    if not csv_files:
        print("Нет файлов page_*_tables.csv!")
        return []
    
    csv_files.sort(key=get_page_number)
    groups = []  # список (start_page, [list_of_csv_files])
    current_pages = []
    current_start = None
    used_files = set()  # Множество использованных файлов

    def flush_group():
        """Вспомогательная функция: переносит current_pages в groups."""
        nonlocal groups, current_pages, current_start
        if current_pages:
            groups.append((current_start, current_pages))
            current_pages = []
            current_start = None

    for idx, csv_file in enumerate(csv_files):
        df = load_csv(csv_file)
        if df.empty:
            continue

        # Берём первую строку
        first_row = df.iloc[0].tolist()
        # Проверяем, все ли цифры (после remove_brackets_and_dots_around_number)
        # => значит "деградированная шапка"
        if row_is_all_digits(first_row):
            # Если это "деградированная шапка"
            # проверяем, есть ли уже какая-то текущая группа
            if not current_pages:
                # Если нет, значит это странно (первая строка без "реальной" шапки?)
                # Начнём новую группу всё равно
                current_pages = [csv_file]
                current_start = get_page_number(csv_file)
            else:
                # Продолжение текущей группы
                current_pages.append(csv_file)
        else:
            # "Реальная" шапка
            # Сначала "закрываем" предыдущую группу (если была)
            flush_group()
            # Начинаем новую
            current_pages = [csv_file]
            current_start = get_page_number(csv_file)
    
    # В конце, если что-то осталось
    flush_group()

    # Теперь реально склеиваем группы
    for (start_page, file_list) in groups:
        if not file_list:
            continue

        # Читаем ПЕРВЫЙ CSV "как есть"
        main_df = load_csv(file_list[0])
        used_files.add(file_list[0])  # Добавляем в использованные
        
        for f2 in file_list[1:]:
            df2 = load_csv(f2)
            # 1) Удалим "пустые" столбцы в шапке
            df2 = unify_empty_columns_in_first_row(df2)
            # 2) Удалим первую строку (деградированная шапка)
            if df2.shape[0] > 1:
                df2 = df2.iloc[1:, :].reset_index(drop=True)
            else:
                # Если там всего 1 строка, значит после удаления ничего не останется
                df2 = pd.DataFrame()
            
            # Допилим кол-во столбцов
            if df2.shape[1] != main_df.shape[1]:
                diff = main_df.shape[1] - df2.shape[1]
                if diff>0:
                    # Добавим пустые столбцы
                    for _ in range(diff):
                        df2[df2.shape[1]] = ""
                elif diff<0:
                    # обрежем
                    df2 = df2.iloc[:, :main_df.shape[1]]
            
            if df2.shape[1] == main_df.shape[1]:
                main_df = pd.concat([main_df, df2], ignore_index=True)
                used_files.add(f2)  # Добавляем в использованные только если успешно объединили
            else:
                print(f"Внимание: {f2} имеет несовместимое число столбцов, пропускаем.")

        end_page = get_page_number(file_list[-1])
        if start_page == end_page:
            outname = f"merged_page_{start_page}.csv"
        else:
            outname = f"merged_page_{start_page}-{end_page}.csv"
        outpath = os.path.join(folder, outname)
        main_df.to_csv(outpath, index=False, header=False, encoding="utf-8")
        print(f"[INFO] Сформирован {outname}, объединив страницы {start_page}..{end_page}")
    
    return list(used_files)


#######################################################
# Пример запуска
#######################################################

def generate_summary(df: pd.DataFrame, output_file: str, input_folder: str) -> None:
    """
    Генерирует краткое описание (summary) таблицы, используя GPT и текст со страницы (page_X_text.txt).
    Сохраняет описание в файл {имя CSV}_summary.txt.
    """
    print(f"\nГенерация описания для файла: {output_file}")
    
    # Понять страницу (или диапазон) из имени файла
    if 'merged_page_' in output_file:
        page_num = re.search(r'merged_page_(\d+)', output_file).group(1)
        print(f"Это объединенная таблица, берём номер первой страницы: {page_num}")
    else:
        page_num = re.search(r'page_(\d+)_', output_file).group(1)
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
    
    # Анализируем содержимое таблицы
    table_content = ""
    if not df.empty:
        # Берем первые 5 строк таблицы для анализа
        preview = df.head(5).to_string(index=False)
        table_content = f"\n\nСодержимое первых строк таблицы:\n{preview}"
    
    system_msg = {
        "role": "system",
        "content": (
            "Ты должен описать конкретное содержимое таблицы в 2-3 предложениях. "
            "Обязательно укажи: "
            "1) Точное название таблицы (если есть номер - укажи его) "
            "2) Перечисли основные колонки/параметры из таблицы "
            "3) Для какого конкретного оборудования или процесса эти данные "
            "4) Какие конкретные значения или диапазоны значений используются "
            "Используй технические термины из текста. Не используй общие фразы."
        )
    }
    user_msg = {
        "role": "user",
        "content": f"Найди описание таблицы в следующем тексте и проанализируй её содержимое:\n\nТекст:\n{text_content}{table_content}"
    }
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_msg, user_msg],
            max_tokens=250,  # Увеличиваем лимит для более детального описания
            temperature=0.1
        )
        description = resp.choices[0].message.content.strip()
        
        summary_file = output_file.replace('.csv', '_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as sf:
            sf.write(description)
        print(f"  Файл с описанием таблицы сохранён в: {summary_file}")
        
    except Exception as e:
        print(f"  ОШИБКА при генерации описания: {str(e)}")


if __name__ == "__main__":
    # Укажите путь к входному PDF и выходной папке
    input_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/input"
    output_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/output"
    
    # Ваш PDF-файл
    pdf_name = "Инструкция Т-108 К-10 и метанирование 2021.pdf"
    input_file = os.path.join(input_folder, pdf_name)


    # 1) Сначала распарсим PDF на page_{N}_tables.csv (если надо):
    extract_content_from_pdf_no_duplicate(input_file, output_folder)

    # 2) Потом объединим нужные страницы:
    used_files = merge_tables_in_folder(output_folder)
    
    # 3) Удаляем только использованные исходные таблицы
    for f in used_files:
        os.remove(f)
        print(f"[INFO] Удален использованный файл {os.path.basename(f)}")
    
    # 4) Генерируем описания для всех объединенных таблиц
    merged_files = glob.glob(os.path.join(output_folder, "merged_page_*.csv"))
    for merged_file in merged_files:
        df = load_csv(merged_file)
        if not df.empty:
            generate_summary(df, merged_file, output_folder)

    
