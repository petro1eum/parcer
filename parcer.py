import os
import json
import base64
import fitz                # PyMuPDF
import pdfplumber
from pdf2image import convert_from_path
from docx2pdf import convert as docx2pdf_convert
from pathlib import Path
from typing import List, Dict, Any, Optional

# GPT - клиент (замените на ваш импорт / класс)
from openai import OpenAI

# Инициализация GPT-клиента (как в вашем примере)
client = OpenAI()

def convert_docx_to_pdf(input_docx_path: str, output_pdf_path: str):
    docx2pdf_convert(input_docx_path, output_pdf_path)

def convert_pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 300) -> List[str]:
    """
    Разбивает PDF на набор PNG-изображений, по одному на страницу.
    Возвращает список путей к изображению.
    """
    pages = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, page in enumerate(pages, start=1):
        img_path = os.path.join(output_dir, f"page_{i}.png")
        page.save(img_path, "PNG")
        image_paths.append(img_path)
    return image_paths

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_page_gpt_4o_mini(image_path: str, page_number: int) -> Dict[str, Any]:
    """
    Отправляет изображение страницы в LLM (GPT), просит вернуть JSON со структурой:
      {
        "headings": [
          {
            "heading_id": "1.1",
            "heading_title": "1.1 Заголовок раздела"
          }
        ],
        "tables": [
          {
            "table_id": "T1",
            "table_title": "Название таблицы",
            "table_continues_from_previous_page": false,
            "original_table_title": "Исходное название таблицы, если это продолжение"
          }
        ]
      }
    """
    print(f"\nАнализируем страницу {page_number} через GPT...")
    base64_image = encode_image_to_base64(image_path)

    system_msg = {
        "role": "system",
        "content": (
            "Вы - эксперт по анализу технической документации. Ваша задача - помочь в создании структурированного оглавления "
            "и правильной обработке многостраничных таблиц в технических инструкциях.\n\n"
            
            "ЦЕЛЬ АНАЛИЗА:\n"
            "1. Создать точное оглавление документа, выделив все нумерованные разделы\n"
            "2. Правильно идентифицировать и связать таблицы, которые могут продолжаться на нескольких страницах\n\n"
            
            "АНАЛИЗ ЗАГОЛОВКОВ РАЗДЕЛОВ:\n"
            "1. Что считать заголовком:\n"
            "   - ТОЛЬКО нумерованные разделы (1., 1.1, 1.2.1 и т.д.)\n"
            "   - Заголовок должен быть выделен визуально (жирный шрифт, отступы и т.д.)\n"
            "   - Должен содержать номер и название раздела\n\n"
            
            "2. Что НЕ считать заголовком:\n"
            "   - Названия оборудования или процессов\n"
            "   - Ненумерованные подзаголовки\n"
            "   - Названия таблиц и рисунков\n"
            "   - Технические термины, даже если они выделены\n\n"
            
            "АНАЛИЗ ТАБЛИЦ:\n"
            "ВАЖНО: В технической документации очень часто встречаются большие таблицы, "
            "занимающие несколько страниц. Одна из ключевых задач - правильно определить такие таблицы "
            "и установить связь между их частями на разных страницах, чтобы собрать всю таблицу.\n\n"
            
            "МНОГОСТРАНИЧНЫЕ ТАБЛИЦЫ:\n"
            "1. Типичные случаи:\n"
            "   - Большие таблицы спецификаций оборудования\n"
            "   - Таблицы с описанием технологических параметров\n"
            "   - Таблицы соответствия и взаимосвязей\n"
            "   - Списки контрольных точек и измерений\n\n"
            
            "2. Как распознать части одной таблицы:\n"
            "   - Одинаковая структура и названия столбцов\n"
            "   - Продолжающаяся нумерация строк\n"
            "   - Логическая связность содержимого\n"
            "   - Единый стиль оформления\n"
            "   - Сквозная тема или предмет описания\n\n"
            
            "3. Типичные указатели на продолжение:\n"
            "   - Текст 'Продолжение таблицы X'\n"
            "   - Отсутствие нового заголовка таблицы\n"
            "   - Шапка таблицы, которая повторяется на нескольких страницах или начинается с новой страницы и содержит в самой верхней строке 1 2 3 4 5 и т.д.\n"
            "   - Прерванные на середине строки или ячейки\n"
            "   - Продолжение списка однотипных элементов\n"
            "   - Ссылки на предыдущие части ('см. начало таблицы')\n\n"
            
            "4. Особенности обработки:\n"
            "   - Первая страница таблицы всегда имеет заголовок\n"
            "   - Промежуточные страницы могут иметь повторяющиеся заголовки столбцов\n"
            "   - Последняя страница часто имеет явное завершение (итоги, подписи)\n"
            "   - Нумерация и форматирование сохраняются через все страницы\n\n"
            
            "5. Что следует учитывать:\n"
            "   - Таблица может прерываться другим содержимым\n"
            "   - Возможны различия в форматировании на разных страницах\n"
            "   - Могут быть подзаголовки или группировки внутри таблицы\n"
            "   - Возможны сноски и примечания, относящиеся ко всей таблице\n\n"
            
            "ФОРМАТ ВЫВОДА:\n"
            "Верните только JSON следующей структуры:\n"
            "{\n"
            '  "headings": [\n'
            '    {\n'
            '      "heading_id": "1.2",        // Точный номер раздела\n'
            '      "heading_title": "1.2 Термины и определения"  // Полный текст с номером\n'
            '    }\n'
            "  ],\n"
            '  "tables": [\n'
            '    {\n'
            '      "table_id": "T1",          // Уникальный ID таблицы на странице\n'
            '      "table_title": "Описание терминов",  // Текущее содержимое\n'
            '      "table_continues_from_previous_page": true,  // Продолжение или новая?\n'
            '      "original_table_title": "Таблица 1"  // Исходное название таблицы\n'
            '    }\n'
            "  ]\n"
            "}\n\n"
            
            "ВАЖНО:\n"
            "- Анализируйте каждую страницу в контексте структуры документа\n"
            "- Обращайте особое внимание на связность таблиц между страницами\n"
            "- Не добавляйте никакого дополнительного текста в ответ\n"
            "- Если сомневаетесь в продолжении таблицы - проверьте структуру столбцов"
            
            "ПРАВИЛА ОПРЕДЕЛЕНИЯ НАЗВАНИЙ ТАБЛИЦ:\n"
            "1. Название новой таблицы:\n"
            "   - Всегда начинается со слова 'Таблица' с номером\n"
            "   - Находится НАД таблицей\n"
            "   - Часто выделено полужирным шрифтом или отступом\n"
            "   - Пример: 'Таблица 1 - Технические характеристики'\n\n"
            
            "2. Содержимое первой строки или ячейки:\n"
            "   - НЕ является названием таблицы\n"
            "   - Это обычно заголовок столбца или первая запись\n"
            "   - Даже если это важный текст, он часть данных\n\n"
            
            "3. Нумерация в первой строке заголовка без пояснений (1, 2, 3...):\n"
            "   - Указывает на продолжение предыдущей таблицы\n"
            "   - Это порядковые номера строк, а не новые таблицы\n"
            "   - Сохраняйте original_table_title от первой части\n\n"
            
            "ОБРАБОТКА МНОГОСТРАНИЧНЫХ ТАБЛИЦ:\n"
            "1. Первое появление таблицы:\n"
            "   - Записать точное название ('Таблица X - Название')\n"
            "   - Сохранить это название как original_table_title\n"
            "   - table_continues_from_previous_page = false\n\n"
            
            "2. Все последующие части той же таблицы:\n"
            "   - Использовать тот же original_table_title\n"
            "   - table_continues_from_previous_page = true\n"
            "   - table_title = краткое описание текущего содержимого\n"
            "   - НЕ создавать новую таблицу, если видите продолжение нумерации строк\n\n"
            
            "3. Признаки продолжения таблицы:\n"
            "   - Продолжающаяся нумерация строк\n"
            "   - Те же заголовки столбцов\n"
            "   - Отсутствие нового названия 'Таблица X'\n"
            "   - Текст 'Продолжение таблицы' или 'Продолжение'\n\n"
            
            "ВАЖНО ПРИ ОПРЕДЕЛЕНИИ ТАБЛИЦ:\n"
            "- Не путать первую строку данных с названием таблицы\n"
            "- Сохранять один original_table_title для всех частей таблицы\n"
            "- Нумерация строк (1,2,3...) указывает на продолжение таблицы\n"
            "- Новая таблица ВСЕГДА имеет явное название 'Таблица X'\n"
        )
    }

    user_msg = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"Analyze page {page_number}. Return JSON with 'headings' and 'tables'."
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
            },
        ],
    }

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_msg, user_msg],
            max_tokens=1500,
        )
        txt = resp.choices[0].message.content
        print(f"GPT ответ для страницы {page_number}:\n{txt}\n{'-'*50}")
    except Exception as e:
        print(f"Ошибка при вызове GPT для страницы {page_number}: {str(e)}")
        return {"headings": [], "tables": []}

    # Очищаем текст от возможных markdown-маркеров
    txt = txt.replace('```json', '').replace('```', '').strip()

    # Пытаемся распарсить
    try:
        data = json.loads(txt)
        return data
    except:
        # Попробуем вычленить JSON между фигурными скобками
        try:
            start_idx = txt.find('{')
            end_idx = txt.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = txt[start_idx:end_idx]
                data = json.loads(json_str)
                return data
        except:
            pass

    return {"headings": [], "tables": []}

def extract_hierarchical_paragraphs(all_headings: List[Dict], pdf_plumb, total_pages: int, output_dir: str):
    # Сортируем заголовки по номеру страницы и позиции
    all_headings.sort(key=lambda x: (x["page_num"], x.get("heading_idx", 0)))
    
    # Проходим по всем заголовкам
    for i, current_heading in enumerate(all_headings[:-1]):
        next_heading = all_headings[i + 1]
        chunk_text = []
        
        # Собираем текст между текущим и следующим заголовком
        for pg in range(current_heading["page_num"], next_heading["page_num"] + 1):
            page_text = pdf_plumb.pages[pg-1].extract_text()
            
            if pg == current_heading["page_num"]:
                # На первой странице берем текст после заголовка
                start_idx = page_text.find(current_heading["heading_title"])
                if start_idx != -1:
                    start_idx += len(current_heading["heading_title"])
                    page_text = page_text[start_idx:].strip()
            
            if pg == next_heading["page_num"]:
                # На последней странице берем текст до следующего заголовка
                end_idx = page_text.find(next_heading["heading_title"])
                if end_idx != -1:
                    page_text = page_text[:end_idx].strip()
            
            if page_text:
                chunk_text.append(page_text)
        
        # Сохраняем текст в правильную папку
        if chunk_text:
            # Создаем иерархию папок
            path_parts = current_heading["heading_id"].split('.')
            current_path = output_dir
            for part in path_parts:
                current_path = os.path.join(current_path, part)
                os.makedirs(current_path, exist_ok=True)
            
            # Формируем имя файла
            heading_title = clean_filename(current_heading["heading_title"].replace(current_heading["heading_id"], "")).strip()
            filename = f"{current_heading['heading_id']}_{heading_title}.txt"
            filepath = os.path.join(current_path, filename)
            
            # Сохраняем текст
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(chunk_text))

def collect_headings(all_pages_data: List[Dict], start_page: int, pdf_plumb) -> List[Dict]:
    """Собирает и нормализует все заголовки из документа"""
    all_headings = []
    seen_headings = set()
    heading_idx_counter = 0
    
    # Собираем заголовки как раньше
    for i, page_data in enumerate(all_pages_data, start=start_page):
        page_headings = page_data.get("headings", [])
        
        for h in page_headings:
            heading_id = h["heading_id"]
            heading_title = h["heading_title"].strip()
            
            if heading_id in seen_headings:
                continue
                
            parts = heading_id.split('.')
            normalized_id = '.'.join(str(int(p)) for p in parts if p.strip())
            
            heading_idx_counter += 1
            all_headings.append({
                "heading_id": normalized_id,
                "heading_title": heading_title,
                "page_num": i,
                "level": len(parts),
                "parent_id": '.'.join(parts[:-1]) if len(parts) > 1 else None,
                "heading_idx": heading_idx_counter
            })
            
            seen_headings.add(heading_id)
    
    # Проверяем пропущенные заголовки
    print("\nПроверяем пропущенные заголовки...")
    all_headings = check_missing_headings(all_headings, pdf_plumb)
    
    return all_headings

def save_heading_content(heading: Dict, content: str, output_dir: str):
    """Сохраняет содержимое раздела в файл с нормализованным именем"""
    # Получаем номер и название раздела
    heading_id = heading["heading_id"]
    heading_title = heading["heading_title"]
    
    # Убираем номер из названия если он там есть
    title_parts = heading_title.split(' ', 1)
    if len(title_parts) > 1 and title_parts[0] == heading_id:
        title = title_parts[1]
    else:
        title = heading_title
    
    # Нормализуем название файла
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('-_')
    
    filename = f"{heading_id}_{safe_title[:50]}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def check_missing_headings(headings: List[Dict], pdf_plumb) -> List[Dict]:
    """Проверяет пропущенные заголовки и пытается их найти"""
    all_headings = headings.copy()
    
    # Сначала выведем все найденные заголовки
    print("\nНайденные заголовки:")
    for h in all_headings:
        print(f"{h['heading_id']}: {h['heading_title']} (стр. {h['page_num']})")
    
    # Группируем по уровням и проверяем пропуски
    levels = {}
    for h in headings:
        parts = h["heading_id"].split('.')
        level = len(parts)
        parent = '.'.join(parts[:-1])
        if parent not in levels:
            levels[parent] = []
        levels[parent].append(int(parts[-1]))
    
    # Проверяем пропуски на каждом уровне
    for parent, numbers in levels.items():
        numbers.sort()
        expected = set(range(1, max(numbers) + 1))
        missing = expected - set(numbers)
        
        if missing:
            print(f"\nПроверяем пропущенные разделы для {parent if parent else 'корневого уровня'}:")
            
            for num in missing:
                missing_id = f"{parent}.{num}" if parent else str(num)
                print(f"\nИщем раздел {missing_id}...")
                
                # Определяем диапазон поиска
                prev_heading = next((h for h in all_headings if h["heading_id"] < missing_id), None)
                next_heading = next((h for h in all_headings if h["heading_id"] > missing_id), None)
                
                if prev_heading:
                    print(f"Предыдущий заголовок: {prev_heading['heading_id']}: {prev_heading['heading_title']}")
                if next_heading:
                    print(f"Следующий заголовок: {next_heading['heading_id']}: {next_heading['heading_title']}")
                
                start_page = prev_heading["page_num"] if prev_heading else 1
                end_page = next_heading["page_num"] if next_heading else len(pdf_plumb.pages)
                
                print(f"Ищем между страницами {start_page} и {end_page}")
                
                # Проверяем каждую страницу
                for page_num in range(start_page, end_page + 1):
                    page_text = pdf_plumb.pages[page_num-1].extract_text()
                    print(f"Проверяем страницу {page_num}...")
                    found_heading = verify_heading_with_gpt(missing_id, page_text, page_num)
                    
                    if found_heading:
                        print(f"Найден пропущенный заголовок: {found_heading['heading_title']} на странице {page_num}")
                        all_headings.append(found_heading)
                        break
                else:
                    print(f"Заголовок {missing_id} не найден в указанном диапазоне")
    
    return sorted(all_headings, key=lambda x: [int(p) for p in x["heading_id"].split('.')])

def verify_heading_with_gpt(heading_id: str, page_text: str, page_num: int) -> Optional[Dict]:
    """
    Проверяет через GPT, есть ли на странице пропущенный заголовок
    """
    system_msg = {
        "role": "system",
        "content": (
            "Вы - эксперт по анализу технической документации. Ваша задача - найти на странице пропущенный заголовок."
                        
            "АНАЛИЗ ЗАГОЛОВКОВ РАЗДЕЛОВ:\n"
            "1. Что считать заголовком:\n"
            "   - ТОЛЬКО нумерованные разделы (1., 1.1, 1.2.1 и т.д.)\n"
            "   - Заголовок должен быть выделен визуально (жирный шрифт, отступы и т.д.)\n"
            "   - Должен содержать номер и название раздела\n\n"
            
            "2. Что НЕ считать заголовком:\n"
            "   - Названия оборудования или процессов\n"
            "   - Ненумерованные подзаголовки\n"
            "   - Названия таблиц и рисунков\n"
            "   - Технические термины, даже если они выделены\n\n"
        )
    }

    user_msg = {
        "role": "user",
        "content": (
            f"Ищем на странице {page_num} заголовок с номером {heading_id}.\n"
            f"Текст страницы:\n\n{page_text}"
        )
    }
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_msg, user_msg],
            max_tokens=500,
            temperature=0  # Делаем ответы более предсказуемыми
        )
        
        # Пытаемся найти JSON в ответе
        content = resp.choices[0].message.content
        try:
            # Пробуем прямой парсинг
            result = json.loads(content)
        except json.JSONDecodeError:
            # Ищем JSON между фигурными скобками
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                result = json.loads(content[start:end])
            else:
                print(f"Не удалось распарсить ответ GPT: {content}")
                return None
        
        if result.get("found"):
            return {
                "heading_id": heading_id,
                "heading_title": result["heading_title"],
                "page_num": page_num,
                "level": len(heading_id.split('.')),
                "heading_idx": 0
            }
    except Exception as e:
        print(f"Ошибка при проверке заголовка {heading_id} на странице {page_num}: {str(e)}")
        print(f"Ответ GPT: {resp.choices[0].message.content if 'resp' in locals() else 'нет ответа'}")
    
    return None

def clean_filename(filename: str) -> str:
    """Очищает строку для использования в имени файла"""
    # Убираем пробелы в начале и конце
    filename = filename.strip()
    # Заменяем все неалфавитные символы на подчеркивание
    filename = "".join(c if c.isalnum() else "_" for c in filename)
    # Убираем множественные подчеркивания
    while "__" in filename:
        filename = filename.replace("__", "_")
    return filename[:50]  # Ограничиваем длину

def main(input_file: str, output_dir: str, start_page: int = 1, end_page: int = 10, is_docx: bool = False, dpi: int = 150):
    """
    Базовый конвейер:
    1) docx -> pdf (если надо)
    2) pdf -> изображения
    3) gpt-анализ страниц, сбор заголовков / таблиц
    4) 'Склеиваем' многостраничные таблицы
    5) Извлекаем текстовые параграфы между заголовками
    6) Сохраняем результаты
    """
    print(f"\nНачинаем обработку файла: {input_file}")
    print(f"Страницы для анализа: {start_page}..{end_page}")
    
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # 1) Если DOCX, конвертируем
    if is_docx:
        print("\nКонвертация DOCX в PDF...")
        pdf_path = os.path.join(temp_dir, "converted.pdf")
        convert_docx_to_pdf(input_file, pdf_path)
    else:
        pdf_path = input_file

    # 2) PDF -> изображения (для анализа GPT)
    print("\nКонвертация PDF в изображения...")
    images_dir = os.path.join(temp_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    image_paths = convert_pdf_to_images(pdf_path, images_dir, dpi=dpi)
    total_pages = len(image_paths)
    print(f"Всего изображений (страниц): {total_pages}")

    # Ограничим страницы
    selected_images = image_paths[start_page-1:end_page]
    print(f"Выбрано для анализа {len(selected_images)} страниц.")

    # Открываем PDF через PyMuPDF и pdfplumber
    pdf_doc = fitz.open(pdf_path)
    pdf_plumb = pdfplumber.open(pdf_path)

    # 3) GPT-анализ: находим заголовки и таблицы
    print("\nАнализируем страницы через GPT...")
    all_pages_data = []
    for i, img_path in enumerate(selected_images, start=start_page):
        page_data = analyze_page_gpt_4o_mini(img_path, i)
        # page_data = {"headings": [...], "tables": [...]}
        all_pages_data.append(page_data)

    # Сохраняем сырые результаты
    raw_output_path = os.path.join(output_dir, "raw_gpt_structure.json")
    with open(raw_output_path, "w", encoding="utf-8") as f:
        json.dump(all_pages_data, f, ensure_ascii=False, indent=2)
    print(f"Сырые данные сохранены: {raw_output_path}")

    # 4) Собираем многостраничные таблицы
    print("\nСобираем (склеиваем) многостраничные таблицы...")
    tables_output_dir = os.path.join(output_dir, "tables")
    os.makedirs(tables_output_dir, exist_ok=True)

    page_idx = 0
    tables_info = []  # Список {"table_id", "table_title", "start_page", "end_page", "original_table_title"}
    current_table = None

    while page_idx < len(all_pages_data):
        cur_page = start_page + page_idx
        page_struct = all_pages_data[page_idx]
        page_tables = page_struct.get("tables", [])

        for t in page_tables:
            t_id = t.get("table_id", f"T_{cur_page}")
            t_ttl = t.get("table_title", "")
            orig_ttl = t.get("original_table_title", "")
            continues_from_prev = t.get("table_continues_from_previous_page", False)

            if continues_from_prev and current_table:
                # Продолжаем текущую таблицу
                current_table["end_page"] = cur_page
            else:
                # Сохраняем предыдущую таблицу, если была
                if current_table:
                    tables_info.append(current_table)
                
                # Начинаем новую таблицу
                current_table = {
                    "table_id": t_id,
                    "table_title": orig_ttl or t_ttl,  # Используем оригинальное название если есть
                    "original_table_title": orig_ttl,
                    "start_page": cur_page,
                    "end_page": cur_page
                }

        page_idx += 1

    # Добавляем последнюю таблицу
    if current_table:
        tables_info.append(current_table)

    # Группируем части одной таблицы по original_table_title
    grouped_tables = {}
    for t in tables_info:
        key = t["original_table_title"] or t["table_title"]
        if key not in grouped_tables:
            grouped_tables[key] = t
        else:
            # Обновляем конечную страницу если это продолжение
            if t["start_page"] > grouped_tables[key]["end_page"]:
                grouped_tables[key]["end_page"] = t["end_page"]

    final_tables = list(grouped_tables.values())

    # Сохраняем каждую таблицу в отдельный PDF
    for t in final_tables:
        sp = t["start_page"]
        ep = t["end_page"]
        t_id = t["table_id"]
        t_ttl = t["original_table_title"] or t["table_title"]

        out_pdf = fitz.open()
        out_pdf.insert_pdf(pdf_doc, from_page=sp-1, to_page=ep-1)
        safe_ttl = "".join([c if c.isalnum() else "_" for c in t_ttl])[:50]
        out_path = os.path.join(tables_output_dir, f"{t_id}_{safe_ttl}.pdf")
        out_pdf.save(out_path)
        out_pdf.close()

    print(f"Уникальных таблиц обработано: {len(final_tables)}")

    # 5) Извлекаем текст параграфов (между заголовками)
    print("\nИзвлекаем параграфы между заголовками...")
    # Собираем и нормализуем заголовки
    all_headings = collect_headings(all_pages_data, start_page, pdf_plumb)

    # Извлекаем текст с учетом иерархии
    extract_hierarchical_paragraphs(all_headings, pdf_plumb, total_pages, output_dir)

    pdf_plumb.close()
    pdf_doc.close()

    print("\nГотово! Результаты сохранены:")
    print(f"1) Сырые данные GPT: {raw_output_path}")
    print(f"2) PDF таблиц: {tables_output_dir}/ (по одной таблице в файле)")
    print(f"3) Параграфы: {output_dir}/ (каждый заголовок + текст)")
    print("--------------------------------------------------")

# --------------------------
# Запуск скрипта
# --------------------------
if __name__ == "__main__":
    # Папка с файлом для парсинга (вход)
    input_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/input"
    # Папка для файлов с результатами (выход)
    output_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/output"

    input_file = os.path.join(input_folder, "Инструкция Т-108 К-10 и метанирование 2021.pdf")
    # Если DOCX, поставить is_docx=True
    main(input_file, output_folder, start_page=10, end_page=20, is_docx=False, dpi=150)