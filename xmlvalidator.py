# xmlvalidator.py
# author: Jakub Kontrik xkontr02
# Description: module for validating given xml file
import xml.etree.ElementTree as ET
import sys
import re
from error import ErrorNum

# class for validating xml file


class XMLValidator:
    def __init__(self, source):
        try:
            # if source is None read from stdin
            if source == None:
                self.root = ET.fromstring(sys.stdin.read())
            else:
                self.root = ET.parse(source).getroot()
        except FileNotFoundError:
            sys.stderr.write("Error: File not found\n")
            sys.exit(ErrorNum.INPUT_FILE_ERR)
        except ET.ParseError:
            sys.stderr.write("Error: XML parse error\n")
            sys.exit(ErrorNum.WRONG_XML_FORMAT)
        # reading xml and sorting it
        try:
            self.root[:] = sorted(self.root, key=lambda child: int(
                # if negative number is in order attribute forcing zero division exeption
                child.get('order')) if int(child.get('order')) > 0 else 0/0)
            for child in self.root:
                child[:] = sorted(child, key=lambda arg: arg.tag)
        except (TypeError, ValueError, ZeroDivisionError):
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

    def validate(self):
        opcode_num = set()
        self.validate_root()
        for child in self.root:
            if child.tag == 'instruction':
                self.validate_instruction(child, opcode_num)
                for arg in child:
                    self.validate_arg(arg)
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
    # checking instruction attributes

    def validate_instruction(self, child, opcode_num):
        if child.get('order') in opcode_num:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        else:
            opcode_num.add(child.get('order'))
        if child.get('opcode') is None:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if child.get('order') is None:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(child) > 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(child) == 1:
            if child[0].tag != 'arg1':
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(child) == 2:
            if child[0].tag != 'arg1' or child[1].tag != 'arg2':
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(child) == 3:
            if child[0].tag != 'arg1' or child[1].tag != 'arg2' or child[2].tag != 'arg3':
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
    # ccekcing arguments attributes

    def validate_arg(self, child):
        match child.attrib.get('type'):
            case 'int':
                child.text = child.text.strip()
                pass
            case 'bool':
                child.text = child.text.strip()
                if not re.match(r'^(true|false)$', child.text) or child.text is None:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'string':
                if child.text is not None:
                    child.text = child.text.strip()
                else:
                    child.text = ''
                pass
            case 'nil':
                child.text = child.text.strip()
                if child.attrib.get('type') == 'nil':
                    if not re.match(r'^nil$', child.text) or child.text is None:
                        sys.stderr.write("Error: Wrong XML structure\n")
                        sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'label':
                child.text = child.text.strip()
                if child.attrib.get('type') == 'label':
                    if not re.match(r'^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', child.text) or child.text is None:
                        sys.stderr.write("Error: Wrong XML structure\n")
                        sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'type':
                child.text = child.text.strip()
                if child.attrib.get('type') == 'type':
                    if not re.match(r'^(int|string|bool)$', child.text) or child.text is None:
                        sys.stderr.write("Error: Wrong XML structure\n")
                        sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'var':
                child.text = child.text.strip()
                if not re.match(r'^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', child.text) or child.text is None:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case _:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

    def validate_root(self):
        if self.root.tag != 'program':
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.root.attrib.get('language') != 'IPPcode23':
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
