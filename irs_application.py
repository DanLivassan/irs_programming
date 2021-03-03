from file_system import FileSystem
from irs_crawler import IrsCrawler, IrsTaxes
import concurrent.futures
import constants
import json


class IrsAction:
    @staticmethod
    def perform_action(**kwargs):
        raise NotImplemented


class IrsActionDownload(IrsAction):
    @staticmethod
    def perform_action(**kwargs):
        """
        The download action get a form number, maximum and minimum of years as parameters.
        Performs http request, format the path and save pdfs files
        :param form_number: the form number of the tax that will be downloaded pdfs files
        :param min_year: the minimum year of the search
        :param max_year: the maximum year of the search
        """
        crawler = IrsCrawler(base_url=constants.URL, result_per_page=200)
        file_system = FileSystem(constants.BASE_DIR)
        taxes = crawler.extract_taxes(kwargs['form_number'], kwargs['min_year'], kwargs['max_year'])
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for tax in taxes.irs_taxes:
                executor.submit(file_system.save_tax, tax)


class IrsActionGetJson(IrsAction):
    @staticmethod
    def perform_action(**kwargs):
        """
        Gets the form numbers list and return a json response
        :param form_numbers: list of forms numbers of the taxes that will be shown in the json format
        """
        crawler = IrsCrawler(base_url=constants.URL, result_per_page=200)
        taxes = IrsTaxes([])

        for form_number in kwargs['form_numbers']:
            if not form_number:
                continue
            form_number = form_number.strip()
            taxes.append_taxes(crawler.extract_taxes(form_number))
        print(json.dumps([tax.to_dict() for tax in taxes.group_by_min_and_max_year_for_each_form_number()], indent=4))


ACTIONS = {
    constants.DOWNLOAD: IrsActionDownload,
    constants.GET_JSON: IrsActionGetJson
}