import unittest
import main
import pandas as pd
import json
import irs_application


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.data = None

    @classmethod
    def tearDownClass(self):
        self.data = None

    def test_parse_args(self):
        download_args = ["", "download", "Pnumber", "2010-2015"]
        wrong_pattern_args = ["", "download", "Pnumber", "201-2015"]
        min_greater_than_max_args = ["", "download", "Pnumber", "2015-2010"]
        self.assertEqual(irs_application.parse_args(download_args), (irs_application.DOWNLOAD, download_args[2], "2010", "2015"))
        self.assertEqual(irs_application.parse_args(wrong_pattern_args), False)
        self.assertEqual(irs_application.parse_args(min_greater_than_max_args), False)

        action_no_exists = ["", "noexists"]
        self.assertEqual(irs_application.parse_args(action_no_exists), False)

        search_empty = ["", "get_json"]
        self.assertEqual(irs_application.parse_args(search_empty), False)

    def test_extract_and_return(self):
        with open('./tests_files/example.html', encoding="utf-8") as f:
            lines = f.read()
            self.assertEqual(irs_application.extract_and_return_last_item(lines)[0], 2539)

    def test_json_format(self):
        test_data=None
        with open('./tests_files/example.html', encoding="utf-8") as f:
            lines = f.read()
            _, test_data = irs_application.extract_and_return_last_item(lines)
        with open('./tests_files/example.json', encoding='utf-8') as f2:
            lines = f2.read()
            json1 = json.loads(lines)
            json2 = json.loads(irs_application.json_format(pd.DataFrame(test_data)[:25]))
            self.assertEqual(len(json1), len(json2))

    def test_downloads_list(self):
        with open('./tests_files/example.html', encoding="utf-8") as f:
            lines = f.read()
            _, data = irs_application.extract_and_return_last_item(lines)
            df = pd.DataFrame(data)
            self.assertEqual(len(irs_application.pdf_download_list(df, "1900", "2020")), 25)

    def test_request_data(self):
        payload = {
            "indexOfFirstRow": '1',
            "sortColumn": "sortOrder",
            "value": "",
            "criteria": "formNumber",
            "resultsPerPage": "25",
            "isDescending": "false"
        }
        self.assertEqual(irs_application.request_data(irs_application.url, payload)[1], 200)


if __name__ == '__main__':
    unittest.main()