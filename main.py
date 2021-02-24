import sys
import irs_application

from constants import *


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    arg_list = irs_application.parse_args(sys.argv)
    if arg_list:
        if arg_list[0] == DOWNLOAD:
            irs_application.action_download(arg_list)
        elif arg_list[0] == GET_JSON:
            irs_application.action_get_json(arg_list)
