from bs4 import BeautifulSoup
from constants import *
from pathlib import Path

import concurrent.futures
import json
import pandas as pd
import re
import requests

resultsPerPage = 200

path_pattern = "{}/{} - {}.pdf"
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
        return handle_error("This action does not exists")


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
    data = []
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
    df['min_year'] = df.groupby('form_number')['year'].transform('min')
    df['max_year'] = df.groupby('form_number')['year'].transform('max')
    del df["year"]
    del df["download_link"]
    df = df.drop_duplicates()
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    return json.dumps(parsed, indent=4)


def download(download_item):
    path_name = download_item[0]
    file_path = "{}".format(path_name)
    print("{}/{} - {}.pdf - Downloading pdfs.".format(path_name, path_name, download_item[1]))
    Path(file_path).mkdir(parents=True, exist_ok=True)
    r = requests.get(download_item[2], allow_redirects=True)
    open(BASE_DIR + '/{}/{} - {}.pdf'.format(path_name, path_name, download_item[1]), 'wb').write(r.content)


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


def action_download(args):
    data = []
    indexOfFirstRow = 0
    payload = get_payload(args[1], indexOfFirstRow)

    while True:
        last_item, d = extract_and_return_last_item(request_data(url, payload)[0])
        data += d
        indexOfFirstRow = indexOfFirstRow + resultsPerPage
        payload = get_payload(args[1], indexOfFirstRow)
        if indexOfFirstRow + resultsPerPage >= last_item:
            break
    df = pd.DataFrame(data)
    df = df[df['form_number'] == args[1]]
    download_list = pdf_download_list(df, args[2], args[3])
    print("Downloading pdfs...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download, download_list)


def action_get_json(args):
    data = []
    df = pd.DataFrame(columns=['form_number', 'form_title', 'year', 'download_link'])
    for form_number in args[1].split(","):
        indexOfFirstRow = 0
        form_number = form_number.strip()
        payload = get_payload(form_number, indexOfFirstRow)

        while True:
            last_item, d = extract_and_return_last_item(request_data(url, payload)[0])
            data += d
            indexOfFirstRow = indexOfFirstRow + resultsPerPage
            payload = get_payload(form_number, indexOfFirstRow)
            df_in = pd.DataFrame(d)
            if indexOfFirstRow + resultsPerPage >= last_item:
                df_in = df_in[df_in['form_number'] == form_number]
                df = df.append(df_in)
                break
    print(json_format(df))