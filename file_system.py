from irs_crawler import IrsTax
from pathlib import Path


class FileSystem:

    def __init__(self, base_directory: str):
        self.base_directory = base_directory

    def save_tax(self, irs_tax: IrsTax):
        """
        This function save the pdf file of the tax passed by parameter
        :param irs_tax: The tax that will be saved in pdf
        """
        directory = "{}/{}".format(self.base_directory, irs_tax.form_number)
        file_path = irs_tax.format_and_return_filename(directory)
        Path(directory).mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as file:
            file.write(irs_tax.download())
        print("{} saved!".format(file_path))
