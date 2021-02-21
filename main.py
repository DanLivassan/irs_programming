from bs4 import BeautifulSoup
import requests
import os, sys
import pandas as pd
import json
from pathlib import Path
import concurrent.futures
import re

GET_JSON = 'get_json'
DOWNLOAD = "download"

indexOfFirstRow = 0
resultsPerPage = 200

path_pattern = "{}/{} - {}.pdf"
data = []
url = 'https://apps.irs.gov/app/picklist/list/priorFormPublication.html'


def get_payload(value, indexOfFirstRow):
    return {
        "indexOfFirstRow": indexOfFirstRow,
        "sortColumn": "sortOrder",
        "value": value,
        "criteria": "formNumber",
        "resultsPerPage": resultsPerPage,
        "isDescending": "false"
    }


def parse_args(args_list):

    if args_list[1] == GET_JSON:
        try:
            return GET_JSON, args_list[2]
        except Exception as e:
            return handle_error(e.__str__())
    elif args_list[1] == DOWNLOAD:
        try:
            rex = re.compile("^[0-9]{4}-[0-9]{4}")
            if rex.match(args_list[3]):
                min_year, max_year = args_list[3].split("-")
                if min_year > max_year:
                    raise Exception("The minimum year is greater than the maximum year")
                return DOWNLOAD, args_list[2], min_year, max_year
            else:
                raise Exception("The pattern of the year should be yyyy-yyyy")
        except Exception as e:
            return handle_error(e.__str__())
    else:
        return handle_error("This action not exists")


def handle_error(err_str=""):
    print(err_str)
    print('\n\nCommand Error!\n\nCall the commands as bellow: '
          '\n\npython main.py get_json "<form_number>"'
          '\npython main.py download "<form_number>" <min_year>-<max_year>\n\n')
    return False


def request_data(url, payload):
    r = requests.get(url, params=payload)
    return r.content, r.status_code


def extract_and_return_last_item(content):
    soup = BeautifulSoup(content, 'html.parser')
    last_item = int(soup.find(attrs={"class": "ShowByColumn"}).text.strip().replace(",", "").split(" ")[-2])
    for line in soup.find(attrs={"class": "picklist-dataTable"}).find_all('tr')[1:]:
        data.append(
            {
                "form_number": line.find_all('td')[0].text.strip(),
                "form_title": line.find_all('td')[1].text.strip(),
                "year": line.find_all('td')[2].text.strip(),
                "download_link": line.find_all('td')[0].a['href']
            }
        )

    return last_item, data


def json_format(df):
    df["max"] = 0
    df["min"] = 0
    df_max = df.groupby(["form_number"])['year'].max()
    df_min = df.groupby(["form_number"])['year'].min()
    for raw in df.values:
        df["max"]=df_max[raw[0]]
        df["min"] = df_min[raw[0]]
    del df["year"]
    del df["download_link"]
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    return json.dumps(parsed, indent=4)


download_list = []


def download(pos):
    path_name = download_list[pos][0]
    file_path = "{}".format(path_name)
    print("{}/{} - {}.pdf - Downloading pdfs.".format(path_name, path_name, download_list[pos][1]))
    Path(file_path).mkdir(parents=True, exist_ok=True)
    r = requests.get(download_list[pos][2], allow_redirects=True)
    open('./{}/{} - {}.pdf'.format(path_name, path_name, download_list[pos][1]), 'wb').write(r.content)


def pdf_download_list(df, min_year, max_year):

    df = df[df["year"] >= min_year]
    df = df[df["year"] <= max_year]

    list_of_download = []
    for index, data in enumerate(df.values):
        form_number = data[0]
        year = data[2]
        url = data[3]
        list_of_download.append((form_number, year, url))
    return list_of_download


if __name__ == "__main__":
    arg_list = parse_args(sys.argv)

    if arg_list:

        payload = get_payload(arg_list[1], indexOfFirstRow)

        while indexOfFirstRow + resultsPerPage < extract_and_return_last_item(request_data(url, payload)[0])[0]:
            indexOfFirstRow = indexOfFirstRow + resultsPerPage
            payload = get_payload(arg_list[1], indexOfFirstRow)
        df = pd.DataFrame(data)

        if arg_list[0] == DOWNLOAD:
            download_list = pdf_download_list(df, arg_list[2], arg_list[3])
            print("Downloading pdfs...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(download, range(len(download_list)))
        elif arg_list[0] == GET_JSON:
            print(json_format(df))
        else:
            handle_error("")
