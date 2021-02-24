import requests
from bs4 import BeautifulSoup
import pandas as pd


class IrsQuery:

    def __init__(self, results_per_page: int, index_of_first_row: int, form_number: str):
        self.result_per_page = results_per_page
        self.index_of_first_row = index_of_first_row
        self.form_number = form_number

    def to_dict(self):
        return {
            "indexOfFirstRow": self.index_of_first_row,
            "sortColumn": "sortOrder",
            "value": self.form_number,
            "criteria": "formNumber",
            "resultsPerPage": self.result_per_page,
            "isDescending": "false"
        }


class IrsTax:

    def __init__(self, form_number: str, form_title, year: int, download_link: str):
        self.form_number = form_number
        self.form_title = form_title
        self.year = year
        self.download_link = download_link

    def download(self):
        r = requests.get(self.download_link, allow_redirects=True)
        if r.status_code != 200:
            raise Exception("Fail to download tax {}".format(self.form_number))
        return r.content

    def to_dict(self):
        return {
            'form_number': self.form_number,
            'form_title': self.form_title,
            'year': self.year,
            'download_link': self.download_link,
        }


class IrsReducedTax:

    def __init__(self, form_number: str, form_title: str, min_year: int, max_year: int):
        self.form_number = form_number
        self.form_title = form_title
        self.min_year = min_year
        self.max_year = max_year

    def to_dict(self):
        return {
            'form_number': self.form_number,
            'form_title': self.form_title,
            'min_year': self.min_year,
            'max_year': self.max_year,
        }


class IrsTaxes:

    def __init__(self, irs_taxes: [IrsTax]):
        self.irs_taxes = irs_taxes

    def as_list(self) -> [IrsTax]:
        return self.irs_taxes

    def append_taxes(self, irs_taxes):
        self.irs_taxes += irs_taxes.as_list()

    def group_by_min_and_max_year_for_each_form_number(self) -> [IrsReducedTax]:
        df = pd.DataFrame.from_records([tax.to_dict() for tax in self.as_list()])
        df['min_year'] = df.groupby('form_number')['year'].transform('min')
        df['max_year'] = df.groupby('form_number')['year'].transform('max')
        del df["year"]
        del df["download_link"]
        df = df.drop_duplicates()

        return [IrsReducedTax(tax[0], tax[1], tax[2], tax[3]) for tax in df.values.tolist()]


class IrsCrawler:

    def __init__(self, base_url: str, result_per_page: int):
        self.base_url = base_url
        self.result_per_page = result_per_page

    def _request_data(self, query: IrsQuery) -> bytes:
        r = requests.get(self.base_url, params=query.to_dict())
        if r.status_code != 200:
            raise Exception("Fail to get irs taxes")
        return r.content

    @staticmethod
    def _parse_html_taxes(html: bytes, expected_form_number: str, min_year: int, max_year: int) -> [IrsTax]:
        data = []
        soup = BeautifulSoup(html, 'html.parser')
        for line in soup.find(attrs={"class": "picklist-dataTable"}).find_all('tr')[1:]:
            form_number = line.find_all('td')[0].text.strip()
            form_title = line.find_all('td')[1].text.strip()
            year = int(line.find_all('td')[2].text.strip())
            download_link = line.find_all('td')[0].a['href']
            if expected_form_number != form_number:
                continue
            if year > max_year != -1:
                continue
            if year < min_year != -1:
                continue
            data.append(IrsTax(
                form_number=form_number,
                form_title=form_title,
                year=year,
                download_link=download_link
            ))
        return data

    @staticmethod
    def _parse_last_item(html: bytes) -> int:
        soup = BeautifulSoup(html, 'html.parser')
        return int(soup.find(attrs={"class": "ShowByColumn"}).text.strip().replace(",", "").split(" ")[-2])

    def extract_taxes(self, form_number: str, min_year: int, max_year: int) -> IrsTaxes:
        query = IrsQuery(form_number=form_number, index_of_first_row=0, results_per_page=self.result_per_page)
        data = []
        last_item = self.result_per_page
        while query.index_of_first_row + self.result_per_page <= last_item:
            html = self._request_data(query)
            last_item = self._parse_last_item(html)
            irs_taxes = self._parse_html_taxes(html, form_number, min_year, max_year)
            data += [tax for tax in irs_taxes]
            query.index_of_first_row += self.result_per_page
        return IrsTaxes(data)
