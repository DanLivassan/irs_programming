import unittest
import main
import irs_application
import constants
from irs_crawler import *


class TestCrawler(unittest.TestCase):

    def test_irstax_when_fail_download(self):
        irs_tax = IrsTax("Form Number", "Form Title", 2000, "https://www.irs.gov/pub/pdf/does_not_exists.pdf")
        self.assertRaises(Exception, irs_tax.download)

    def test_irstaxes_group_by_min_and_max_year_grouping_two_form_numbers(self):
        irs_tax_list = [
            IrsTax("Form Number 1", "Form Title", 2000, "https://www.irs.gov/pub/pdf/does_not_exists.pdf"),
            IrsTax("Form Number 1", "Form Title", 2005, "https://www.irs.gov/pub/pdf/does_not_exists.pdf"),
            IrsTax("Form Number 1", "Form Title", 2010, "https://www.irs.gov/pub/pdf/does_not_exists.pdf"),
            IrsTax("Form Number 2", "Form Title", 2000, "https://www.irs.gov/pub/pdf/does_not_exists.pdf"),
            IrsTax("Form Number 2", "Form Title", 2005, "https://www.irs.gov/pub/pdf/does_not_exists.pdf"),
            IrsTax("Form Number 2", "Form Title", 2010, "https://www.irs.gov/pub/pdf/does_not_exists.pdf")
        ]
        irs_taxes = IrsTaxes(irs_tax_list)
        self.assertEqual(len(irs_taxes.group_by_min_and_max_year_for_each_form_number()), 2)

    def test_irscrawler_extract_taxes(self):
        url = 'https://apps.irs.gov/app/picklist/list/priorFormPublication.html'
        irs_crawler = IrsCrawler(url, 200)
        irs_taxes = irs_crawler.extract_taxes("Form W-2", 2000, 2010)
        self.assertIs(type(irs_taxes), IrsTaxes)


class TestMain(unittest.TestCase):

    def test_parse_args(self):
        download_args = ["", "download", "Pnumber", "2010-2015"]
        wrong_pattern_args = ["", "download", "Pnumber", "201-2015"]
        min_greater_than_max_args = ["", "download", "Pnumber", "2015-2010"]
        self.assertEqual(main.parse_args(download_args), (main.DOWNLOAD, download_args[2], "2010", "2015"))
        self.assertEqual(main.parse_args(wrong_pattern_args), False)
        self.assertEqual(main.parse_args(min_greater_than_max_args), False)

        action_no_exists = ["", "noexists"]
        self.assertEqual(main.parse_args(action_no_exists), False)

        search_empty = ["", "get_json"]
        self.assertEqual(main.parse_args(search_empty), False)


if __name__ == '__main__':
    unittest.main()