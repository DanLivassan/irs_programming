#!/home/dan/PycharmProjects/webcrawler/venv/bin/ python3

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
max_year = 2020
min_year = 2020


indexOfFirstRow = 0
resultsPerPage = 200
value = ""

path_pattern = "{}/{} - {}.pdf"
data = []
url = 'https://apps.irs.gov/app/picklist/list/priorFormPublication.html'


payload = {
    "indexOfFirstRow": indexOfFirstRow,
    "sortColumn": "sortOrder",
    "value": value,
    "criteria": "formNumber",
    "resultsPerPage": resultsPerPage,
    "isDescending": "false"
}


def command_error_msg(err_str=""):
    print(err_str)
    print('\n\nCommand Error!\n\nCall the commands as bellow: '
          '\n\npython main.py get_json "<form_number>"'
          '\npython main.py download "<form_number>" <min_year>-<max_year>\n\n')


def request_data(url, payload):
    r = requests.get(url, params=payload)
    return r.content


def extract_data(content):
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

    return last_item


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
    print(json.dumps(parsed, indent=4))


download_list = []


def download(pos):
    path_name = download_list[pos][0]
    file_path = "{}".format(path_name)
    print("{}/{} - {}.pdf - Downloading pdfs.".format(path_name, path_name, download_list[pos][1]))
    Path(file_path).mkdir(parents=True, exist_ok=True)
    r = requests.get(download_list[pos][2], allow_redirects=True)
    open('./{}/{} - {}.pdf'.format(path_name, path_name, download_list[pos][1]), 'wb').write(r.content)


def pdf_download_list(df, min_year="2015", max_year="2018"):

    df = df[df["year"] >= min_year]
    df = df[df["year"] <= max_year]

    print("Downloading pdfs...")
    list_of_download = []
    for index, data in enumerate(df.values):
        form_number = data[0]
        year = data[2]
        url = data[3]
        list_of_download.append((form_number, year, url))
    return list_of_download


if __name__ == "__main__":
    arg_list = sys.argv

    if arg_list[1] == GET_JSON:
        try:
            value = arg_list[2]
            payload["value"] = arg_list[2]
        except Exception as e:
            command_error_msg(e.__str__())
            exit()
    elif arg_list[1] == DOWNLOAD:
        try:
            rex = re.compile("^[0-9]{4}-[0-9]{4}")
            value = arg_list[2]
            payload["value"] = arg_list[2]
            if rex.match(arg_list[3]):
                min_year, max_year = arg_list[3].split("-")
                if min_year > max_year:
                    raise Exception("The minimum year is greater than the maximum year")
            else:
                command_error_msg()
                exit()
        except Exception as e:
            command_error_msg(e.__str__())
            exit()
    else:
        command_error_msg("")
        exit()

    while indexOfFirstRow + resultsPerPage < extract_data(request_data(url, payload)):
        indexOfFirstRow = indexOfFirstRow + resultsPerPage
        payload = {
            "indexOfFirstRow": indexOfFirstRow,
            "sortColumn": "sortOrder",
            "value": value,
            "criteria": "formNumber",
            "resultsPerPage": resultsPerPage,
            "isDescending": "false"
        }

    df = pd.DataFrame(data)

    if arg_list[1] == DOWNLOAD:
        download_list = pdf_download_list(df, min_year, max_year)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(download, range(len(download_list)))
    elif arg_list[1] == GET_JSON:
        json_format(df)
    else:
        command_error_msg()