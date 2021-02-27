import argparse
import constants
import re


class IrsParser:

    def __init__(self, action: str):
        self._action = action

    def get_parser(self):
        parser = None
        if self._action == constants.GET_JSON:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "--action",
                type=str,
                required=True,
                help="The action that will be performed Ex.: download or get_json")
            parser.add_argument(
                "--form_numbers",
                type=str,
                required=True,
                nargs="+",
                help="List of form numbers of taxes that will be searched")
        elif self._action == constants.DOWNLOAD:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "--action",
                type=str,
                required=True,
                help="The action that will be performed Ex.: download or get_json")
            parser.add_argument(
                "--form_number",
                type=str,
                required=True,
                help="Form number of tax that will be searched")
            parser.add_argument(
                "--year_range",
                type=str,
                required=True,
                help="The range of years that will be searched. Ex.: 2010-2020")
        return parser


class IrsParseValidator:

    def __init__(self, action: str):
        self._action = action

    @staticmethod
    def date_range_is_valid(date_range: str) -> bool:
        rex = re.compile("^[0-9]{4}-[0-9]{4}$")

        if rex.match(date_range):
            min_year, max_year = date_range.split("-")
            min_year = int(min_year)
            max_year = int(max_year)

            if min_year > max_year:
                print("The minimum year is greater than maximum year")
                return False
            if min_year < 1900 or max_year > 2050:
                print("The range year pattern must be between 1900 and 2050")
                return False
            return True
        else:
            print("The range year pattern must be DDDD-DDDD. Ex.: 1999-2000")
            return False

    def validate(self, parsed_args: dict) -> bool:
        is_valid = True
        if self._action == constants.GET_JSON:
            is_valid = parsed_args['action'] == constants.GET_JSON and isinstance(parsed_args['form_numbers'], list)
        if self._action == constants.DOWNLOAD:
            is_valid = \
                parsed_args['action'] == constants.DOWNLOAD and IrsParseValidator.date_range_is_valid(parsed_args['year_range'])

        return is_valid

