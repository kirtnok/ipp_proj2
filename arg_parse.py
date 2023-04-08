
import argparse
import sys
from error import ErrorNum
# TODO: vyriesit errory --source
class ArgumentParser:
    def __init__(self):
        self.parser = MyParse(add_help=False)
        self.parser.add_argument("--source", help="source file", metavar='FILE', dest="source_file")
        self.parser.add_argument("--input", help="input file", metavar='FILE', dest="input_file")
        self.parser.add_argument("--help", help="help", dest="help", action="store_true")
        self.args = self.parser.parse_args()
    
    def get_source(self):
        return self.args.source_file
    def get_input(self):
        return self.args.input_file
    def get_help(self):
        return self.args.help

class MyParse(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message)
        sys.exit(ErrorNum.WRONG_PARAM)
