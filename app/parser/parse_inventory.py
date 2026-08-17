import pandas as pd
from typing import Generator, Dict, Any, List, Tuple

from app.parser import fields_names as fnames


def find_blocks(df: pd.DataFrame) -> List[Tuple[int, int]]:
    """
    Находит все блоки данных в датафрейме.
    Возвращает список кортежей (header_row, data_start_row, data_end_row).
    """
    blocks = []
    header_rows = []
    data_start_row = None

    for idx, row in df.iterrows():
        first_cell = str(row[0]).strip().lower() if pd.notna(row[0]) else ''
        second_cell = str(row[1]).strip().lower() if pd.notna(row[1]) else ''
        third_cell = str(row[2]).strip().lower() if pd.notna(row[2]) else ''

        # Если нашли заголовок 'код строки'
        if 'код строки' in first_cell:
            header_rows.append(idx)
        # Пропускаем строку с номерами столбцов (1, 2, 3, ...)
        elif first_cell == '1' and second_cell == '2' and third_cell == '3':
            continue
        # Если нашли строку с числами (начало данных)
        elif first_cell.isdigit() and header_rows:
            # Проверяем, что это не пустая строка-заголовок
            if not second_cell.isdigit() or len(second_cell) > 1:
                data_start_row = idx
                # Ищем конец блока (пустая строка или не число)
                current_row = idx
                while current_row < len(df):
                    check_cell = str(df.iloc[current_row, 0]).strip() if pd.notna(df.iloc[current_row, 0]) else ''
                    if not check_cell or not check_cell.isdigit():
                        break
                    current_row += 1
                data_end_row = current_row

                # Находим соответствующий заголовок
                header_row = header_rows[-1]
                blocks.append((header_row, data_start_row, data_end_row))

                # Сбрасываем header_rows для следующего блока
                header_rows = []
                # Продолжаем поиск следующего блока
                continue

    return blocks


def parse_block(df: pd.DataFrame, header_row: int, data_start_row: int, data_end_row: int) -> Generator[
    Dict[str, Any], None, None]:
    """
    Парсит один блок данных.
    """
    # Получаем названия столбцов из заголовка
    actual_headers = []
    for col in range(len(df.columns)):
        val = df.iloc[header_row, col]
        if pd.notna(val):
            actual_headers.append(str(val).strip())
        else:
            actual_headers.append('')

    # Находим индексы нужных столбцов
    col_indices = {}
    for idx, name in enumerate(actual_headers):
        name_lower = name.lower()
        if 'код строки' in name_lower:
            col_indices['row_num'] = idx
        elif 'наименование объекта' in name_lower:
            col_indices[fnames.NAME_IN_ACCOUNT] = idx
        elif 'номер (код) объекта' in name_lower or 'инвентарный' in name_lower:
            col_indices[fnames.INVENTORY] = idx
        elif 'место / подразделение' in name_lower:
            col_indices['department'] = idx
        elif 'количество' in name_lower:
            col_indices[fnames.QUANTITY] = idx
        elif 'балансовая стоимость' in name_lower:
            col_indices[fnames.PRICE] = idx
        elif 'единица измерения' in name_lower:
            col_indices['unit'] = idx

    # Итерация по данным блока
    for current_row in range(data_start_row, data_end_row):
        row = df.iloc[current_row]
        first_cell = str(row[0]).strip() if pd.notna(row[0]) else ''

        # Если строка пустая или не число — пропускаем
        if not first_cell or not first_cell.isdigit():
            continue

        # Собираем данные
        data = {}
        for key, col_idx in col_indices.items():
            val = row[col_idx] if col_idx < len(row) else None
            if pd.notna(val):
                data[key] = str(val).strip()
            else:
                data[key] = None

        # Добавляем единицу измерения
        if 'unit' in col_indices and col_indices['unit'] + 1 < len(row):
            unit_name = row[col_indices['unit'] + 1] if col_indices['unit'] + 1 < len(row) else None
            if pd.notna(unit_name):
                data['unit_name'] = str(unit_name).strip()

        yield data


def parse_inventory_file(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Парсит инвентарную опись и возвращает генератор словарей с данными об изделиях.
    """
    df = pd.read_excel(file_path, header=None, dtype=str, engine='openpyxl')

    # Находим все блоки данных
    blocks = find_blocks(df)

    if not blocks:
        raise ValueError("Не найдены блоки данных в файле")

    # Парсим каждый блок
    for header_row, data_start_row, data_end_row in blocks:
        yield from parse_block(df, header_row, data_start_row + 1, data_end_row)


# Пример использования
if __name__ == "__main__":
    file_path = "/home/alexey/Документы/job/warehouse/Инвентаризационная_опись_по_объектам_НФА_ф_0510466_№_837_от_26_06.xlsx"

    try:
        total = 0
        for idx, item in enumerate(parse_inventory_file(file_path), 1):
            print(f"Изделие {idx}:")
            print(f"  Номер строки: {item.get('row_num')}")
            print(f"  Наименование: {item.get(fnames.NAME_IN_ACCOUNT)}")
            print(f"  Инвентарный номер: {item.get(fnames.INVENTORY)}")
            print(f"  Место: {item.get('department')}")
            print(f"  Количество: {item.get(fnames.QUANTITY)}")
            print(f"  Стоимость: {item.get(fnames.PRICE)}")
            print(f"  Единица измерения: {item.get('unit_name')}")
            print()
            total += 1
            if idx >= 10:  # Покажем только первые 10 записей
                break

        print(f"Всего обработано изделий: {total}")

    except Exception as e:
        print(f"Ошибка: {e}")