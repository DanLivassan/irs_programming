import argparse
import constants
import re


class IrsParser:
    @staticmethod
    def get_parser():
        pass


class IrsJsonParser(IrsParser):

    @staticmethod
    def get_parser():
        """
        Define and return the argument parser
        :return: argument parser
        """
        parser = None

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
        return parser


class IrsDownloadParser(IrsParser):
    @staticmethod
    def get_parser():
        """
        Define and return the argument parser
        :return: argument parser
        """
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


class IrsParseBuilder:
    @classmethod
    def build(cls, parser: IrsParser):
        return parser.get_parser()


class IrsParseValidator:

    def __init__(self, action: str):
        self._action = action

    @staticmethod
    def year_range_is_valid(year_range: str) -> bool:
        """
        Check if the year range format is valid
        :param year_range: year range string with format YYYY-YYYY
        :return: True if is valid
        """
        rex = re.compile("^[0-9]{4}-[0-9]{4}$")

        if rex.match(year_range):
            min_year, max_year = year_range.split("-")
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
        """
        Check if the parameters of actions are valids
        :param parsed_args:
        :return: is_valid
        """
        is_valid = True
        if self._action == constants.GET_JSON:
            is_valid = parsed_args["action"] == constants.GET_JSON and isinstance(parsed_args["form_numbers"], list)
        if self._action == constants.DOWNLOAD:
            is_valid = \
                parsed_args["action"] == constants.DOWNLOAD and IrsParseValidator.year_range_is_valid(
                    parsed_args["year_range"])

        return is_valid


PARSERS = {
    "download": IrsDownloadParser,
    "get_json": IrsJsonParser
}