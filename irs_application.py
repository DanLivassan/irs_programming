from constants import *
from irs_crawler import *
import concurrent.futures
import json
from file_system import FileSystem

url = 'https://apps.irs.gov/app/picklist/list/priorFormPublication.html'


def action_download(form_number: str, min_year: int, max_year: int):
    crawler = IrsCrawler(base_url=url, result_per_page=200)
    file_system = FileSystem(BASE_DIR)
    taxes = crawler.extract_taxes(form_number, min_year, max_year)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for tax in taxes.as_list():
            executor.submit(file_system.save_tax, tax)


def action_get_json(form_numbers):
    crawler = IrsCrawler(base_url=url, result_per_page=200)
    taxes = IrsTaxes([])

    for form_number in form_numbers.split(","):
        form_number = form_number.strip()
        taxes.append_taxes(crawler.extract_taxes(form_number, min_year=-1, max_year=-1))
    print(json.dumps([tax.to_dict() for tax in taxes.group_by_min_and_max_year_for_each_form_number()], indent=4))
