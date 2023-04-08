import argparse
import sys
import re
import xml.etree.ElementTree as ET
from error import ErrorNum
from arg_parse import ArgumentParser
from xmlvalidator import XMLValidator


if __name__ == '__main__':
    arg = ArgumentParser()
    source = arg.get_source()
    input = arg.get_input()
    help = arg.get_help()
    if help is True:
        if source is not None or input is not None:
            sys.stderr.write("Error: Wrong arguments\n")
            sys.exit(ErrorNum.WRONG_PARAM)
        print("TODO: help")
        sys.exit(0)
    if (source is None and input is None):
        sys.stderr.write("Error: Expected source or input file\n")
        sys.exit(ErrorNum.WRONG_PARAM)
    xml_in = XMLValidator(source)
    print(list(xml_in.tree.getroot()))
    for element in xml_in.tree.iter():
        print(element)
    xml_in.validate()
