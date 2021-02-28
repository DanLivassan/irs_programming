from irs_crawler import IrsCrawler, IrsTax, IrsTaxes
from irs_parser import IrsParser, IrsParseValidator
from file_system import FileSystem

import constants
import os
import random
import requests
import unittest


class TestCrawler(unittest.TestCase):

    def test_irstax_when_fail_download(self):
        irs_tax = IrsTax("Form Number", "Form Title", 2000, "https://www.irs.gov/pub/pdf/does_not_exists.pdf")
        self.assertRaises(requests.exceptions.InvalidURL, irs_tax.download)

    def test_irstaxes_group_by_min_and_max_year_grouping_two_form_numbers(self):
        form_number_1 = "Form Number 1"
        form_title_1 = "Form Number 1"
        form_number_2 = "Form Number 2"
        form_title_2 = "Form Number 2"
        download_link = "#"
        min_year = 1999
        max_year = 2021
        irs_tax_list = []
        for i in range(10):
            irs_tax_list.append(
                IrsTax(form_number_1, form_title_1, random.randint(min_year + 1, max_year - 1), download_link))
            irs_tax_list.append(
                IrsTax(form_number_2, form_title_2, random.randint(min_year + 1, max_year - 1), download_link))

        # min and max years
        irs_tax_list.append(IrsTax(form_number_1, form_title_1, min_year, download_link))
        irs_tax_list.append(IrsTax(form_number_2, form_title_2, min_year, download_link))
        irs_tax_list.append(IrsTax(form_number_1, form_title_1, max_year, download_link))
        irs_tax_list.append(IrsTax(form_number_2, form_title_2, max_year, download_link))

        irs_taxes = IrsTaxes(irs_tax_list)
        for irs_reduced_tax in irs_taxes.group_by_min_and_max_year_for_each_form_number():
            self.assertEqual(irs_reduced_tax.min_year, min_year)
            self.assertEqual(irs_reduced_tax.max_year, max_year)
        self.assertEqual(len(irs_taxes.group_by_min_and_max_year_for_each_form_number()), 2)

    def test_irscrawler_extract_taxes(self):
        url = 'https://apps.irs.gov/app/picklist/list/priorFormPublication.html'
        irs_crawler = IrsCrawler(url, 200)
        irs_taxes = irs_crawler.extract_taxes("Form W-2", 2000, 2010)
        self.assertIs(type(irs_taxes), IrsTaxes)


class TestParserValidator(unittest.TestCase):
    def test_download_format_of_yearrange_is_invalid(self):
        validator = IrsParseValidator(constants.DOWNLOAD)

        is_valid = validator.date_range_is_valid("200-2020")

        self.assertEqual(is_valid, False)

    def test_download_minyear_greater_than_max_year(self):
        validator = IrsParseValidator(constants.DOWNLOAD)

        is_valid = validator.date_range_is_valid("2021-2015")

        self.assertEqual(is_valid, False)

    def test_download_year_out_of_the_maximum_range(self):
        validator = IrsParseValidator(constants.DOWNLOAD)

        greater_than_max_is_valid = validator.date_range_is_valid("2020-2100")
        less_than_min_is_valid = validator.date_range_is_valid("1800-2000")

        self.assertEqual(greater_than_max_is_valid, False)
        self.assertEqual(less_than_min_is_valid, False)


class TestFileSystem(unittest.TestCase):
    def test_right_format_and_filename(self):
        form_number = "form_number"
        directory = "/directory"
        year = 2000
        irs_tax = IrsTax(form_number, "", year, "#")
        pattern = f"{directory}/{form_number} - {year}.pdf"
        file_system = FileSystem(directory)

        file_path = file_system.format_and_return_filename(irs_tax, file_system.base_directory)

        self.assertEqual(file_path, pattern)

    def test_savetax(self):
        form_number = "form_number"
        base_directory = constants.BASE_DIR + "/tests_files"
        year = 2000
        url = "https://www.irs.gov/pub/irs-prior/p1--2017.pdf"
        irs_tax = IrsTax(form_number, "", year, url)
        file_system = FileSystem(base_directory)

        file_system.save_tax(irs_tax)
        directory = "{}/{}".format(file_system.base_directory, irs_tax.form_number)
        self.assertTrue(os.path.isfile(file_system.format_and_return_filename(irs_tax, directory)))


if __name__ == '__main__':
    unittest.main()
