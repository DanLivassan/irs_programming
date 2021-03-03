from irs_parser import IrsParseBuilder, IrsParseValidator, PARSERS
import irs_application
import sys

if __name__ == "__main__":
    try:
        parser = IrsParseBuilder.build(PARSERS[sys.argv[2]])
        if parser:
            parsed_args = vars(parser.parse_args())
            irs_validator = IrsParseValidator(parsed_args["action"])
            action = parsed_args["action"]
            if irs_validator.validate(parsed_args):
                kwargs = PARSERS[action].format_args_to_action(**parsed_args)
                irs_application.ACTIONS[action].perform_action(**kwargs)
        else:
            print("This action does not exist. See the valid actions and how to call them at README.md file")
    except IndexError:
        print("This action does not exist. See the valid actions and how to call them at README.md file")
