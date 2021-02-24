import requests
from bs4 import BeautifulSoup
import pandas as pd


class IrsQuery:

    def __init__(self, results_per_page: int, index_of_first_row: int, form_number: str):
        """
        :param results_per_page: The results per page on the payload of search
        :param index_of_first_row: The index of the first row on the payload of search
        :param form_number: The form number that will be searched
        """
        self.result_per_page = results_per_page
        self.index_of_first_row = index_of_first_row
        self.form_number = form_number

    def to_dict(self):
        """
        This method return a formatted payload query
        """
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
        """
        :param form_number: The form number of Tax
        :param form_title: The title of Tax
        :param year: The year of the Tax
        :param download_link: The download link of pdf file
        """
        self.form_number = form_number
        self.form_title = form_title
        self.year = year
        self.download_link = download_link

    def download(self):
        """
            This method return a Response with the pdf file that will be downloaded in download_link url
        """
        r = requests.get(self.download_link, allow_redirects=True)
        if r.status_code != 200:
            raise Exception("Fail to download tax {}".format(self.form_number))
        return r.content

    def to_dict(self):
        """
            This method return dict of the fields
         """
        return {
            'form_number': self.form_number,
            'form_title': self.form_title,
            'year': self.year,
            'download_link': self.download_link,
        }


class IrsReducedTax:

    def __init__(self, form_number: str, form_title: str, min_year: int, max_year: int):
        """
        This is a reduced tax that represents the minimum and maximum year of records founded on irs site
        :param form_number: The form number of tax
        :param form_title: The title of tax
        :param min_year: minimum year founded
        :param max_year: maximum year founded
        """
        self.form_number = form_number
        self.form_title = form_title
        self.min_year = min_year
        self.max_year = max_year

    def to_dict(self):
        """
            This method return dict of the fields
        """
        return {
            'form_number': self.form_number,
            'form_title': self.form_title,
            'min_year': self.min_year,
            'max_year': self.max_year,
        }


class IrsTaxes:

    def __init__(self, irs_taxes: [IrsTax]):
        """
        :param irs_taxes: Collection of Tax
        """
        self.irs_taxes = irs_taxes

    def as_list(self) -> [IrsTax]:
        """
        :return: Return collection of Tax
        """
        return self.irs_taxes

    def append_taxes(self, irs_taxes):
        """
        This method concatenate the 2 list of IrsTax
        :param irs_taxes: list of irsTax
        :return: concatenated list of irsTax
        """
        self.irs_taxes += irs_taxes.as_list()

    def group_by_min_and_max_year_for_each_form_number(self) -> [IrsReducedTax]:
        """
        This method group the taxes by minimum and maximum of years and return a list of reducedTax
        :return: list of reducedTax
        """
        df = pd.DataFrame.from_records([tax.to_dict() for tax in self.as_list()])
        df['min_year'] = df.groupby('form_number')['year'].transform('min')
        df['max_year'] = df.groupby('form_number')['year'].transform('max')
        del df["year"]
        del df["download_link"]
        df = df.drop_duplicates()

        return [IrsReducedTax(tax[0], tax[1], tax[2], tax[3]) for tax in df.values.tolist()]


class IrsCrawler:

    def __init__(self, base_url: str, result_per_page: int):
        """
        :param base_url: Url of website of irs application 
        :param result_per_page: Results per page of the search
        """
        self.base_url = base_url
        self.result_per_page = result_per_page

    def _request_data(self, query: IrsQuery) -> bytes:
        """
        This method make a Get request with the query and return the response
        :param query: payload of get request
        :return: html content of the page
        """
        r = requests.get(self.base_url, params=query.to_dict())
        if r.status_code != 200:
            raise Exception("Fail to get irs taxes")
        return r.content

    @staticmethod
    def _parse_html_taxes(html: bytes, expected_form_number: str, min_year: int, max_year: int) -> [IrsTax]:
        """
        This method search the parameter on the html page, filter, format and return a list of IrsTax
        :param html: content of html page
        :param expected_form_number: the form number that is expected to be filtered
        :param min_year: In download action of irs_application is needed to filter minimum of year
        :param max_year: In download action of irs_application is needed to filter maximum of year
        :return: list of IrsTax
        """
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
        """
        This method returns the number of the last item
        :param html:  html page
        :return: number of last item
        """
        soup = BeautifulSoup(html, 'html.parser')
        return int(soup.find(attrs={"class": "ShowByColumn"}).text.strip().replace(",", "").split(" ")[-2])

    def extract_taxes(self, form_number: str, min_year: int, max_year: int) -> IrsTaxes:
        """
        This is a public method that you get the query , peform the search and return the Taxes
        :param form_number:
        :param min_year:
        :param max_year:
        :return:
        """
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
