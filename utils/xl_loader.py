from typing import Dict, List
from .logger import log
from .decorators import error_handler
from .xlwt import Workbook


class XlHandler:
    """
    This class allows to write data into xl sheets

    Args:
        self.xl: excel workbook
    """

    def __init__(self):
        self.xl = Workbook()

    @error_handler("Excel write sheets")
    def write_data(self, data: Dict[str, List[any]], sheet: str, ) -> None:
        sheet = self.xl.add_sheet(sheet)
        row_counter = 0
        for key, value in data.items():
            for num in range(len(value)):
                row = sheet.row(num)
                column = row_counter
                row.write(column, value[num])
            row_counter += 1

    @error_handler("Excel save file")
    def save(self, filename: str) -> None:
        self.xl.save(filename)



