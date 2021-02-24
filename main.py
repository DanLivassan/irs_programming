import irs_application
import re
import sys

from constants import *


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


if __name__ == "__main__":
    arg_list = parse_args(sys.argv)
    if arg_list:
        if arg_list[0] == DOWNLOAD:
            irs_application.action_download(arg_list[1], int(arg_list[2]), int(arg_list[3]))
        elif arg_list[0] == GET_JSON:
            irs_application.action_get_json(arg_list[1])
