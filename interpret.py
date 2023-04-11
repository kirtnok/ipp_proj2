import sys
import xml.etree.ElementTree as ET
from error import ErrorNum
from arg_parse import ArgumentParser
from xmlvalidator import XMLValidator
from factory import Factory
from interpret_class import Interpret

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
    xml_in.validate()
    interpret=Interpret()
    for i,child in enumerate(xml_in.root):
        if child.get('opcode') == 'LABEL':
            interpret.labels[child[0].text] = i
    
    factory = Factory()
    for child in xml_in.root:
        instruction=factory.get_instruction(child.get('opcode'),interpret)
        for arg in child:
            instruction.set_arg(arg)
    interpret.run(instruction)
    #debug
    print("TF",interpret.tmp_frame.vars)
    print("GF",interpret.global_frame.vars)
    print("LABELS",interpret.labels)
