import csv
from datetime import date
from dataclasses import dataclass
from typing import Iterable, Iterator
from contextlib import suppress  
from collections import defaultdict
from operator import attrgetter
BUY = 'buy'
SALE = 'sale'
TRANSLATION = {
    BUY: 'Покупки',
    SALE: 'Продажи',
}
DEFAULT_INDENT = '      '
MONTHS_ROW_INDENT = ' ' * 60
COLUMN_WIDTH = 10
HEADER_COLUMN_WIDTH = 55
@dataclass
class Row:
    type: str
    date: date
    shop: str
    category: str
    name: str
    amount: int
    price: float
    def __post_init__(self):
        self.amount = int(self.amount)
        self.price = float(self.price)
        self.date = date.fromisoformat(self.date).replace(day=1)
@dataclass
class Report:
    content: dict[str, 'Group']
    months_range: set[date]
def generate_row_path(row: Row) -> Iterator[str]:
    yield from [row.shop, row.category or 'Без категории', row.name]
class Group:
    def __init__(self, name: str) -> None:
        self.name = name
        self.sums_by_months = defaultdict(float)
        self.total_sum_for_period = 0.0
        self.subgroups = {}
                 
    def add_row(self, row: Row, row_spec_path: Iterator[str]):
        row_total_price = row.amount * row.price
        self.sums_by_months[row.date] += row_total_price
        self.total_sum_for_period += row_total_price
        with suppress(StopIteration):
            key = next(row_spec_path)
            group = self.subgroups.get(key)
            
            if not group:
                group = Group(name=key)
                self.subgroups[key] = group
            
            group.add_row(row, row_spec_path)
def get_report() -> Report:
    type_groups = {SALE: Group(SALE), BUY: Group(BUY)}
    months_range = set()
    # Group(sale).subgroups = {'ТГК-2': Group(ТКГ-2).subgroups({'Посуда': Group(Посуда).subgroups({'Набор ножей «Overlord»': Group(ножи)})})}
    
    with open('catalog_2.csv', 'r') as source_file:
        for row in csv.DictReader(source_file):
            row_object = Row(**row)
            months_range.add(row_object.date)
            type_groups[row_object.type].add_row(row_object, generate_row_path(row_object))
    return Report(type_groups, sorted(months_range))
def get_row_data_aligned_with_months_range(
    full_months_range: Iterable[date],
    row_data: dict[date, float]
):
    return [row_data.get(x, 0.0) for x in full_months_range]
class ReportPrinter:
    def _print_column_headers_row(self, month_range: Iterable[date]):
        column_names = [x.strftime("%b %Y") for x in month_range]
        column_names.append('ИТОГО')
        print(f'{MONTHS_ROW_INDENT}{DEFAULT_INDENT.join(x.rjust(COLUMN_WIDTH) for x in column_names)}')
    def _print_row(self, content: Iterable[str], header='', level=0):
        level_indent = DEFAULT_INDENT * level
        indented_header = level_indent + header
        header = (
            indented_header
            if len(indented_header) < HEADER_COLUMN_WIDTH 
            else indented_header[:HEADER_COLUMN_WIDTH].rstrip() + '…'
        )
        after_header_indent = ' ' * (len(MONTHS_ROW_INDENT) - len(header))
        print(f'{header}{after_header_indent}{DEFAULT_INDENT.join(x.rjust(COLUMN_WIDTH) for x in content)}')
    def _print_group(
        self,
        group: Group, 
        full_months_range: Iterable[date],
        header:str = '', 
        level: int = 0
    ):
        group_content = get_row_data_aligned_with_months_range(full_months_range, group.sums_by_months)
        group_content.append(group.total_sum_for_period)
        
        self._print_row(
            [f'{x:.2f}' for x in group_content],
            header=header, 
            level=level
        )
        
        if group.subgroups:
            sorted_subgroups = sorted(
                group.subgroups.values(),
                key=attrgetter('total_sum_for_period'),
                reverse=True
            )
            for subgroup in sorted_subgroups:
                self._print_group(subgroup, full_months_range, header=subgroup.name, level=level + 1)
    def print_report(self, report: Report):
        self._print_column_headers_row(report.months_range)
        for type_group_name, type_group in report.content.items():
            type_group_name_translated = TRANSLATION[type_group_name]
            self._print_group(type_group, report.months_range, header=type_group_name_translated)
ReportPrinter().print_report(get_report())