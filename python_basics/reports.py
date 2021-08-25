import csv
import locale
from collections import Counter
from datetime import date
from datetime import timedelta
from operator import attrgetter


HEADER_COLUMN_WIDTH = 72
AMOUNT_COLUMN_WIDTH = 12

class ReportRecord:
    def __init__(self, key):
        self.key = key
        self.amounts = Counter()
        self.total = 0
        self.children = {}

    def add_row(self, path, date, amount):
        self.amounts[date] += amount
        self.total += amount

        if path:
            key = path.pop(0)
            try:
                child = self.children[key]
            except KeyError:
                child = self.children[key] = ReportRecord(key)
            child.add_row(path, date, amount)

    def walk(self, level=0):
        yield level, self
        for child in sorted(self.children.values(), key=attrgetter('total'), reverse=True):
            yield from child.walk(level + 1)

def make_date_range(min_date, max_date):
    result = []
    current = min_date
    while current <= max_date:
        result.append(current)
        next_month = current.month + 1
        current = date(current.year + next_month // 12, (next_month - 1) % 12 + 1, 1)
    return result


def format_report_header(date_range):
    column_headers = [month.strftime('%b %Y') for month in date_range]
    column_headers.append('итог')

    offset = ' ' * HEADER_COLUMN_WIDTH
    header = ''.join(f'{header:>{AMOUNT_COLUMN_WIDTH}}' for header in column_headers)

    return offset + header

def format_report_record(record, level, date_range):
    label = ' ' * (4 * level) + record.key
    first_column = f'{label:<{HEADER_COLUMN_WIDTH}}'

    amounts = [record.amounts.get(month, 0) for month in date_range]
    amounts.append(record.total)
    amounts_formatted = ''.join(
        f'{amount:>{AMOUNT_COLUMN_WIDTH}.2f}'
        for amount in amounts
    )

    return first_column + amounts_formatted

def main():
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

    registry = {
        'buy': ReportRecord('Покупка'),
        'sale': ReportRecord('Продажа'),
    }

    with open('catalog_2.csv', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        min_date = None
        max_date = None
        for row in reader:
            row_type = row['type']
            row_date = date.fromisoformat(row['date']).replace(day=1)
            row_amount = float(row['amount']) * float(row['price'])
            path = [
                row['shop'],
                row['category'] or 'Без категории',
                row['name'],
            ]
            registry[row_type].add_row(path, row_date, row_amount)
            min_date = min(min_date or row_date, row_date)
            max_date = max(max_date or row_date, row_date)

        date_range = make_date_range(min_date, max_date)
        print(format_report_header(date_range))
        for record in registry.values():
            for level, row in record.walk():
                print(format_report_record(row, level, date_range))


if __name__ == '__main__':
    main()