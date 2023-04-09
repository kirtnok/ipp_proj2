import xml.etree.ElementTree as ET
import sys
import re
from error import ErrorNum


class XMLValidator:
    def __init__(self, source):
        try:
            if source is None:
                self.tree = ET.parse(sys.stdin)
            else:
                self.tree = ET.parse(source)
        except FileNotFoundError:
            sys.stderr.write("Error: File not found\n")
            sys.exit(ErrorNum.SOURCE_FILE_ERR)
        except ET.ParseError:
            sys.stderr.write("Error: XML parse error\n")
            sys.exit(ErrorNum.WRONG_XML_FORMAT)

        self.tree = ET.parse(source)
        self.root = self.tree.getroot()
        try:
            self.root[:] = sorted(self.root, key=lambda child: int(child.get('order')) if int(child.get('order')) >= 0 else 0/0)
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
    #TODO UPRAVIT REGEXY
    def validate_arg(self, child):
        match child.attrib.get('type'):
            case 'int':
                if not re.match(r'^[-+]?[0-9]+$', child.text) or child.text is None:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'bool':
                if not re.match(r'^(true|false)$', child.text) or child.text is None:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'string':
                try:
                    if not re.match(r'^[^\s#\\\\]*$', child.text):
                        sys.stderr.write("Error: Wrong XML structure\n")
                        sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
                except TypeError:
                    pass
            case 'nil':
                if child.attrib.get('type') == 'nil':
                    if not re.match(r'^nil$', child.text) or child.text is None:
                        sys.stderr.write("Error: Wrong XML structure\n")
                        sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'label':
                if child.attrib.get('type') == 'label':
                    if not re.match(r'^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', child.text) or child.text is None:
                        sys.stderr.write("Error: Wrong XML structure\n")
                        sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'type':
                if child.attrib.get('type') == 'type':
                    if not re.match(r'^(int|string|bool)$', child.text) or child.text is None:
                        sys.stderr.write("Error: Wrong XML structure\n")
                        sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
            case 'var':
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
