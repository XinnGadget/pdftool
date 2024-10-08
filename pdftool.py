# -*- coding: utf-8 -*-
"""Экспорт pdf в растр"""

import sys
import pymupdf

EXPORT_DPI = 250

PRINTER_SIZES = (29.7, 42)


def pt2cm(pt: float) -> float:
    return round(pt*(2.54/72), 2)


def get_page_size_cm(page) -> tuple[float, float]:
    width = pt2cm(page.mediabox.width)
    height = pt2cm(page.mediabox.height)
    return width, height


def normalise_size(size: tuple[float, float]) -> tuple[float, float]:
    """Нормализуем размер чтобы меньшее число было первым"""
    return size if size[0] < size[1] else (size[1], size[0])


def group_sizes(document) -> dict:
    """"Возвращает структуру списков, по ключу размеру
    (42, 59.4):
        [page1, page3]
    (29.7, 42):
        [page2]
    """
    page_sizes = {}
    for page in document:
        width, height = normalise_size(get_page_size_cm(page))

        if (width, height) in page_sizes:
            page_sizes[(width, height)].append(page)
        else:
            page_sizes.update({(width, height): [page]})

    return page_sizes


def get_unique_sizes(page_sizes) -> list:
    """Ищем уникальные размеры и нормализуем их по меньшей стороне"""
    unique_sizes = set()
    for size in page_sizes.keys():
        unique_sizes.add(normalise_size(size))

    return list(unique_sizes)


def is_equal_size(size1, size2) -> bool:
    return True if normalise_size(size1) == normalise_size(size2) else False


def filter2printer(sizes: list) -> list:
    ret = []
    for size in sizes:
        if (size[0] <= PRINTER_SIZES[0]) and (size[1] <= PRINTER_SIZES[1]):
            ret.append(size)
    return ret


def choose_to_export(unique_sizes) -> list:
    for num, size in enumerate(unique_sizes, start=1):
        print(f'{num}) {size[0]}x{size[1]}')
    print('a) Все')
    print('p) Принтерная печать')
    print('l) Широкоформатная печать')
    print('q) Выход')

    choice = input('Выберите пункт: ')

    if choice.isnumeric():
        return [unique_sizes[int(choice)-1]]
    elif choice.lower() == 'a':
        return unique_sizes
    elif choice.lower() == 'p':
        return filter2printer(unique_sizes)
    elif choice.lower() == 'l':
        #TODO: фильтрация для печать на плоттере
        pass
    elif choice.lower() == 'q':
        sys.exit(0)


def main():
    pdf_files = sys.argv[1:]
    for pdf_file in pdf_files:
        print('Открываем файл', pdf_file)
        doc = pymupdf.open(pdf_file)

        grouped_page_sizes = group_sizes(doc)

        for num, size in enumerate(grouped_page_sizes.keys()):
            print(f'{size[0]}x{size[1]} = {len(grouped_page_sizes[size])} шт')

        print()

        unique_sizes = get_unique_sizes(grouped_page_sizes)

        export_sizes = choose_to_export(unique_sizes)

        for num, page in enumerate(doc, start=1):
            width, height = get_page_size_cm(page)

            for size in export_sizes:
                if is_equal_size((width, height), size):
                    img = page.get_pixmap(dpi=EXPORT_DPI)
                    filename = f'{width}x{height}_{pdf_file.removesuffix('.pdf')}_{num:02}'
                    print(f'Сохраняю {filename}.png')
                    img.save(f'{filename}.png')


if __name__ == "__main__":
    main()
