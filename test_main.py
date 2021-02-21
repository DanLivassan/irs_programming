import unittest
import main


class TestMain(unittest.TestCase):
    def test_request_data(self):
        payload = {
            "indexOfFirstRow": '1',
            "sortColumn": "sortOrder",
            "value": "",
            "criteria": "formNumber",
            "resultsPerPage": "25",
            "isDescending": "false"
        }
        self.assertEqual(main.request_data(main.url, payload)[1], 200)


if __name__ == '__main__':
    unittest.main()