import pdfplumber
import os
import csv

def extract_content_from_pdf_no_duplicate(input_file, output_folder):
    """
    Извлекает текст (без текста таблиц) и таблицы из PDF файла постранично
    """
    with pdfplumber.open(input_file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # 1) Получаем все таблицы (как объекты) на странице
            tables_on_page = page.find_tables()
            # Формируем список bounding box-ов таблиц
            table_bboxes = [table.bbox for table in tables_on_page]  
            # bbox имеет вид (x0, top, x1, bottom)

            # 2) Извлекаем все слова со страницы
            words = page.extract_words()  
            # words – это список слов, каждое слово – dict с координатами и текстом

            # 3) Оставляем только те слова, которые не входят ни в один bbox таблицы
            words_outside_tables = []
            for w in words:
                x0, y0, x1, y1 = w['x0'], w['top'], w['x1'], w['bottom']
                
                # Проверяем, не попадает ли слово в прямоугольник каждой таблицы
                inside_any_table = False
                for (tb_x0, tb_top, tb_x1, tb_bottom) in table_bboxes:
                    # Если слово пересекается с координатами таблицы, считаем, что оно "в таблице"
                    # Немного упрощённая логика: проверяем, что все углы (или центр) попадают в bbox
                    if (x0 >= tb_x0 and x1 <= tb_x1 and
                        y0 >= tb_top and y1 <= tb_bottom):
                        inside_any_table = True
                        break  # Достаточно найти одно совпадение
            
                # Если слово НЕ в таблице – добавляем к результату
                if not inside_any_table:
                    words_outside_tables.append(w)

            # 4) Склеиваем слова в строку (можно гибко управлять пробелами/переносами)
            # Здесь делаем простой вариант
            filtered_text = " ".join([w['text'] for w in words_outside_tables])
            
            # Если есть текст
            if filtered_text.strip():
                text_filename = os.path.join(output_folder, f'page_{page_num}_text.txt')
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(filtered_text)

            # 5) Извлекаем данные таблиц (построчно) и пишем в CSV
            tables_data = page.extract_tables()
            if tables_data:
                tables_filename = os.path.join(output_folder, f'page_{page_num}_tables.csv')
                with open(tables_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for table in tables_data:
                        writer.writerows(table)

if __name__ == "__main__":
    input_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/input"
    output_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/output"
    
    input_file = os.path.join(input_folder, "Инструкция Т-108 К-10 и метанирование 2021.pdf")
    
    os.makedirs(output_folder, exist_ok=True)
    extract_content_from_pdf_no_duplicate(input_file, output_folder)