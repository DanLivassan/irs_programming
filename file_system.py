from irs_crawler import IrsTax
from pathlib import Path


class FileSystem:

    def __init__(self, base_directory: str):
        self.base_directory = base_directory

    def save_tax(self, irs_tax: IrsTax):
        directory = "{}/{}".format(self.base_directory, irs_tax.form_number)
        Path(directory).mkdir(parents=True, exist_ok=True)
        with open('{}/{} - {}.pdf'.format(directory, irs_tax.form_number, irs_tax.year), 'wb') as file:
            file.write(irs_tax.download())
