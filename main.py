from irs_parser import IrsParser, IrsParseValidator
import constants
import irs_application
import sys


if __name__ == "__main__":
    parser = IrsParser(sys.argv[2])
    parsed_args = vars(parser.get_parser().parse_args())
    irs_validator = IrsParseValidator(parsed_args['action'])

    if irs_validator.validate(parsed_args):
        if parsed_args['action'] == constants.DOWNLOAD:
            min_year, max_year = parsed_args['year_range'].split('-')
            irs_application.action_download(parsed_args['form_number'], int(min_year), int(max_year))
        elif parsed_args['action'] == constants.GET_JSON:
            irs_application.action_get_json(parsed_args['form_numbers'])
