# interpret.py
# author: Jakub Kontrik xkontr02
# Description: main module for interpretation
import sys
import xml.etree.ElementTree as ET
from error import ErrorNum
from arg_parse import ArgumentParser
from xmlvalidator import XMLValidator
from factory import Factory
from interpret_class import Interpret

if __name__ == '__main__':
    # parsing arguments
    arg = ArgumentParser()
    # checking arguments
    source = arg.get_source()
    input_file = arg.get_input()
    help = arg.get_help()
    if help is True:
        if source is not None or input_file is not None:
            sys.stderr.write("Error: Wrong arguments\n")
            sys.exit(ErrorNum.WRONG_PARAM)
        print("TODO: help")
        sys.exit(0)
    if (source is None and input is None):
        sys.stderr.write("Error: Expected source or input file\n")
        sys.exit(ErrorNum.WRONG_PARAM)
    # validating xml
    xml_in = XMLValidator(source)
    xml_in.validate()
    interpret = Interpret(input_file)
    # getting labels
    for i, child in enumerate(xml_in.root):
        if child.get('opcode').upper() == 'LABEL':
            if child[0].text in interpret.labels:
                sys.stderr.write("Error: Label already defined\n")
                sys.exit(ErrorNum.SEMANTIC_ERROR)
            interpret.labels[child[0].text] = i
    instruction = None
    # getting instructions from factory
    factory = Factory()
    for child in xml_in.root:
        instruction = factory.get_instruction(child.get('opcode'), interpret)
        for arg in child:
            instruction.set_arg(arg)
    # if there is at least one instruction run it
    if instruction is not None:
        interpret.run(instruction)
