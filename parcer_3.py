import pdfplumber
import os
import csv

def extract_content_from_pdf(input_file, output_folder):
    """
    Извлекает текст и таблицы из PDF файла постранично
    """
    with pdfplumber.open(input_file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Извлекаем текст
            text = page.extract_text()
            if text:
                text_filename = os.path.join(output_folder, f'page_{page_num}_text.txt')
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(text)
            
            # Извлекаем таблицы
            tables = page.extract_tables()
            if tables:
                tables_filename = os.path.join(output_folder, f'page_{page_num}_tables.csv')
                with open(tables_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for table in tables:
                        writer.writerows(table)

if __name__ == "__main__":
    input_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/input"
    output_folder = "/Users/edcher/Library/CloudStorage/Box-Box/Cherednik/Angara/Technology/parcer/output"
    
    input_file = os.path.join(input_folder, "Инструкция Т-108 К-10 и метанирование 2021.pdf")
    
    os.makedirs(output_folder, exist_ok=True)
    extract_content_from_pdf(input_file, output_folder)
