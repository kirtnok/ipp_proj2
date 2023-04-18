# instructions.py
# author: Jakub Kontrik xkontr02
# Description: module for instruction classes

from frame import Frame
from error import ErrorNum
import sys
from interpret_class import Interpret
import re

# parent class for all instructions


class Instruction:
    # shared list of all instructions
    instruction_list = []

    def __init__(self, opcode, interpret: Interpret):
        self.opcode = opcode
        self.instruction_list.append(self)
        self.arguments = []
        # interpret class for accessing global variables and runtime checking
        self.interpret = interpret

    def execute(self):
        pass

    def set_arg(self, arg):
        self.arguments.append(Argument(arg.attrib.get('type'), arg.text))
    # check if variable is defined in given frame

    def check_var(self, frame, name):
        if frame == "GF":
            if name not in self.interpret.global_frame.vars:
                sys.stderr.write("Error: Variable not defined\n")
                sys.exit(ErrorNum.UNDEFINED_VARIABLE)
        elif frame == "LF":
            if self.interpret.local_frames.is_empty():
                sys.stderr.write("Error: Frame does not exist\n")
                sys.exit(ErrorNum.MISSING_FRAME)
            if name not in self.interpret.local_frames.top().vars:
                sys.stderr.write("Error: Variable not defined\n")
                sys.exit(ErrorNum.UNDEFINED_VARIABLE)
        elif frame == "TF":
            if self.interpret.tmp_frame is None:
                sys.stderr.write("Error: Frame does not exist\n")
                sys.exit(ErrorNum.MISSING_FRAME)
            if name not in self.interpret.tmp_frame.vars:
                sys.stderr.write("Error: Variable not defined\n")
                sys.exit(ErrorNum.UNDEFINED_VARIABLE)
        else:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
    # get variable from given frame

    def get_var(self, frame, name):
        if frame == "GF":
            return self.interpret.global_frame.get_var(name)
        elif frame == "LF":
            return self.interpret.local_frames.top().get_var(name)
        elif frame == "TF":
            return self.interpret.tmp_frame.get_var(name)
    # set variable in given frame

    def set_var(self, frame, name, value):
        if frame == "GF":
            self.interpret.global_frame.set_var(name, value)
        elif frame == "LF":
            self.interpret.local_frames.top().set_var(name, value)
        elif frame == "TF":
            self.interpret.tmp_frame.set_var(name, value)

# class for nil type


class Nil:
    def __init__(self):
        self.value = None

# class for instruction arguments


class Argument:
    def __init__(self, type, value: str):
        self.type = type
        if type == "bool":
            if value == "true":
                self.value = True
            if value == "false":
                self.value = False
        elif type == "int":
            # convert string number to int
            # if number is in octal or hexa format, convert it to decimal
            # if string is not number, exit with error
            try:
                self.value = int(value, 0)
            except ValueError:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        # format escape sequences
        elif type == "string":
            self.value = str(value)
            self.value = re.sub(r'\\(\d{3})', lambda x: chr(
                int(x.group(1))), self.value)
        elif type == "var":
            self.value = value
        elif type == "nil" and value == "nil":
            self.value = Nil()
        elif type == "label":
            self.value = value
        elif type == "type":
            self.value = value
        else:
            sys.stderr.write("TODO ERROR\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

## INSTRUCTIONS ##
## MOVE <var> <symb> ##


class Move(Instruction):
    def __init__(self, interpret):
        super().__init__("MOVE", interpret)

    def execute(self):
        # validate arguments
        if len(self.arguments) != 2:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[1].type in ["type", "label"]:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        # get frame and name of variable
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        value = 0
        # if second argument is variable, get its value
        if self.arguments[1].type == "var":
            frame_2, name_2 = self.arguments[1].value.split('@', 1)
            self.check_var(frame_2, name_2)
            value = self.get_var(frame_2, name_2)
            # check if variable is initialized
            if value is None:
                sys.stderr.write("Error: Variable not defined\n")
                sys.exit(ErrorNum.MISSING_VALUE)
        # if second argument is not variable, get its value
        else:
            value = self.arguments[1].value
        self.set_var(frame, name, value)

## CREATEFRAME ##


class CreateFrame(Instruction):
    def __init__(self, interpret):
        super().__init__("CREATEFRAME", interpret)

    def execute(self):
        # validate arguments
        if len(self.arguments) != 0:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        # create new tmp frame
        self.interpret.tmp_frame = Frame()

## PUSHFRAME ##


class PushFrame(Instruction):
    def __init__(self, interpret):
        super().__init__("PUSHFRAME", interpret)

    def execute(self):
        # validate arguments
        if len(self.arguments) != 0:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        # if no tmp frame, exit with error
        if self.interpret.tmp_frame is None:
            sys.stderr.write("Error: Temp frame does not exist\n")
            sys.exit(ErrorNum.MISSING_FRAME)
        # push tmp frame to local frames stack
        self.interpret.local_frames.push(self.interpret.tmp_frame)
        self.interpret.tmp_frame = None

## POPFRAME ##


class PopFrame(Instruction):
    def __init__(self, interpret):
        super().__init__("POPFRAME", interpret)

    def execute(self):
        if len(self.arguments) != 0:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        # if no local frames, exit with error
        if self.interpret.local_frames.is_empty():
            sys.stderr.write("Error: Temp frame does not exist\n")
            sys.exit(ErrorNum.MISSING_FRAME)
        self.interpret.tmp_frame = self.interpret.local_frames.pop()

## DEFVAR <var> ##


class DefVar(Instruction):
    def __init__(self, interpret):
        super().__init__("DEFVAR", interpret)

    def execute(self):
        # validate arguments
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        # check if variable is already defined
        if frame == "GF":
            if name in self.interpret.global_frame.vars:
                sys.stderr.write("Error: Variable already defined\n")
                sys.exit(ErrorNum.SEMANTIC_ERROR)
            self.interpret.global_frame.set_var(name, None)
        elif frame == "LF":
            if self.interpret.local_frames.is_empty():
                sys.stderr.write("Error: Frame does not exist\n")
                sys.exit(ErrorNum.MISSING_FRAME)
            if name in self.interpret.local_frames.top().vars:
                sys.stderr.write("Error: Variable already defined\n")
                sys.exit(ErrorNum.SEMANTIC_ERROR)
            self.interpret.local_frames.top().set_var(name, None)
        elif frame == "TF":
            if self.interpret.tmp_frame is None:
                sys.stderr.write("Error: Frame does not exist\n")
                sys.exit(ErrorNum.MISSING_FRAME)
            if name in self.interpret.tmp_frame.vars:
                sys.stderr.write("Error: Variable already defined\n")
                sys.exit(ErrorNum.SEMANTIC_ERROR)
            self.interpret.tmp_frame.set_var(name, None)
        else:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

## Call <label> ##


class Call(Instruction):
    def __init__(self, interpret):
        super().__init__("CALL", interpret)

    def execute(self):
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "label":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].value not in self.interpret.labels:
            sys.stderr.write("Error: Label does not exist\n")
            sys.exit(ErrorNum.SEMANTIC_ERROR)
        # push current instruction index to call stack
        self.interpret.call_stack.push(self.interpret.inst_index)
        # set instruction index to label index
        self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]

## Return ##


class Return(Instruction):
    def __init__(self, interpret):
        super().__init__("RETURN", interpret)

    def execute(self):
        if len(self.arguments) != 0:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        # if call stack is empty, exit with error
        if self.interpret.call_stack.is_empty():
            sys.stderr.write("Error: Call stack is empty\n")
            sys.exit(ErrorNum.MISSING_VALUE)
        self.interpret.inst_index = self.interpret.call_stack.pop()

## PUSHS <symb> ##


class PushS(Instruction):
    def __init__(self, interpret):
        super().__init__("PUSHS", interpret)

    def execute(self):
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type in ["type", "label"]:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        # if variable, check if it is defined
        if self.arguments[0].type == "var":
            frame, name = self.arguments[0].value.split('@', 1)
            self.check_var(frame, name)
            # if variable is not defined, exit with error
            if self.get_var(frame, name) is None:
                sys.stderr.write("Error: Empty var\n")
                sys.exit(ErrorNum.MISSING_VALUE)
            self.interpret.data_stack.push(self.get_var(frame, name))
        else:
            self.interpret.data_stack.push(self.arguments[0].value)

## POPS <var> ##


class PopS(Instruction):
    def __init__(self, interpret):
        super().__init__("POPS", interpret)

    def execute(self):
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.interpret.data_stack.is_empty():
            sys.stderr.write("Error: EMPTY STACK\n")
            sys.exit(ErrorNum.MISSING_VALUE)
        frame, name = self.arguments[0].value.split('@', 1)
        # check if variable is defined
        self.check_var(frame, name)
        self.set_var(frame, name, self.interpret.data_stack.pop())

## ADD <var> <symb1> <symb2> ##


class Add(Instruction):
    def __init__(self, interpret):
        super().__init__("ADD", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        # loop through symb1 and symb2
        for i, var in enumerate(self.arguments[1:]):
            # if symb is variable check if it is defined
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                # check if variable is initialized
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                # dynamic type check
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] + numbers[1])

## SUB <var> <symb1> <symb2> ##


class Sub(Instruction):
    def __init__(self, interpret):
        super().__init__("SUB", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        # loop through symb1 and symb2
        for i, var in enumerate(self.arguments[1:]):
            # if symb is variable check if it is defined
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                # check if variable is initialized
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                # dynamic type check
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] - numbers[1])

## MUL <var> <symb1> <symb2> ##


class Mul(Instruction):
    def __init__(self, interpret):
        super().__init__("MUL", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        # loop through symb1 and symb2
        for i, var in enumerate(self.arguments[1:]):
            # if symb is variable check if it is defined
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                # dynamic type check
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] * numbers[1])

## DIV <var> <symb1> <symb2> ##


class IDiv(Instruction):
    def __init__(self, interpret):
        super().__init__("IDIV", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        # loop through symb1 and symb2
        for i, var in enumerate(self.arguments[1:]):
            # if symb is variable check if it is defined
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                # check if variable is initialized
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                # dynamic type check
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        # handle zero division exception
        try:
            self.set_var(frame, name, int(numbers[0] / numbers[1]))
        except ZeroDivisionError:
            sys.stderr.write("Error: Division by zero\n")
            sys.exit(ErrorNum.WRONG_OPERAND_VALUE)

## LT <var> <symb1> <symb2> ##


class Lt(Instruction):
    def __init__(self, interpret):
        super().__init__("LT", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        # loop through symb1 and symb2
        for i, var in enumerate(self.arguments[1:]):
            # if symb is variable check if it is defined
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                # check if variable is initialized
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                # dynamic type check
                if type(numbers[i]) != int and type(numbers[i]) != bool and type(numbers[i]) != str:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int" or var.type == "bool" or var.type == "string":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        # check if types are the same
        if type(numbers[0]) != type(numbers[1]):
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] < numbers[1])

## GT <var> <symb1> <symb2> ##


class Gt(Instruction):
    def __init__(self, interpret):
        super().__init__("GT", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                if type(numbers[i]) != int and type(numbers[i]) != bool and type(numbers[i]) != str:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int" or var.type == "bool" or var.type == "string":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        if type(numbers[0]) != type(numbers[1]):
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] > numbers[1])

## EQ <var> <symb1> <symb2> ##


class Eq(Instruction):
    def __init__(self, interpret):
        super().__init__("EQ", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                # dynamic type check
                if type(numbers[i]) != int and type(numbers[i]) != bool and type(numbers[i]) != str and type(numbers[i]) != Nil:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int" or var.type == "bool" or var.type == "string" or var.type == "nil":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        # if at least one is nil
        if Nil in [type(numbers[0]), type(numbers[1])]:
            self.set_var(frame, name, type(numbers[0]) == type(numbers[1]))
            return
        # check same type
        if type(numbers[0]) != type(numbers[1]):
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] == numbers[1])

## AND <var> <symb1> <symb2> ##


class And(Instruction):
    def __init__(self, interpret):
        super().__init__("AND", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                if type(numbers[i]) != bool:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "bool":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] and numbers[1])

## OR <var> <symb1> <symb2> ##


class Or(Instruction):
    def __init__(self, interpret):
        super().__init__("OR", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        numbers = [None, None]
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                if type(numbers[i]) != bool:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "bool":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] or numbers[1])

## NOT <var> <symb> ##


class Not(Instruction):
    def __init__(self, interpret):
        super().__init__("NOT", interpret)

    def execute(self):
        if len(self.arguments) != 2:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        value = None
        if self.arguments[1].type == "var":
            frame_2, name_2 = self.arguments[1].value.split('@', 1)
            self.check_var(frame_2, name_2)
            value = self.get_var(frame_2, name_2)
            if value is None:
                sys.stderr.write("Error: Variable not set\n")
                sys.exit(ErrorNum.MISSING_VALUE)
            if type(value) != bool:
                sys.stderr.write("Error: Wrong type\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        elif self.arguments[1].type == "bool":
            value = self.arguments[1].value
        else:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, not (value))

# INT2CHAR <var> <symb> #


class Int2Char(Instruction):
    def __init__(self, interpret):
        super().__init__("INT2CHAR", interpret)

    def execute(self):
        if len(self.arguments) != 2:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        value = None
        if self.arguments[1].type == "var":
            frame_2, name_2 = self.arguments[1].value.split('@', 1)
            self.check_var(frame_2, name_2)
            value = self.get_var(frame_2, name_2)
            if value is None:
                sys.stderr.write("Error: Variable not set\n")
                sys.exit(ErrorNum.MISSING_VALUE)
            if type(value) != int:
                sys.stderr.write("Error: Wrong type\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        elif self.arguments[1].type == "int":
            value = self.arguments[1].value
        try:
            result = chr(value)
            self.set_var(frame, name, result)
        except TypeError:
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        except ValueError:
            sys.stderr.write("Error: Wrong value\n")
            sys.exit(ErrorNum.STRING_ERROR)

## STRI2INT <var> <symb1> <symb2> ##


class Stri2Int(Instruction):
    def __init__(self, interpret):
        super().__init__("STRI2INT", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        string = None
        index = None
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                if i == 0:
                    string = self.get_var(frame_2, name_2)
                    if string is None:
                        sys.stderr.write("Error: Variable not set\n")
                        sys.exit(ErrorNum.MISSING_VALUE)
                    if type(string) != str:
                        sys.stderr.write("Error: Wrong type\n")
                        sys.exit(ErrorNum.TYPE_ERROR)
                else:
                    index = self.get_var(frame_2, name_2)
                    if index is None:
                        sys.stderr.write("Error: Variable not set\n")
                        sys.exit(ErrorNum.MISSING_VALUE)
                    if type(index) != int:
                        sys.stderr.write("Error: Wrong type\n")
                        sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "string":
                if i == 0:
                    string = var.value
                else:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                if i == 1:
                    index = var.value
                else:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        ## Check if index is in range ##
        if index > len(string) - 1 or index < 0:
            sys.stderr.write("Error: Wrong value\n")
            sys.exit(ErrorNum.STRING_ERROR)
        self.set_var(frame, name, ord(string[index]))

## READ <var> <type> ##


class Read(Instruction):
    def __init__(self, interpret):
        super().__init__("READ", interpret)

    def execute(self):
        if len(self.arguments) != 2:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        if self.arguments[1].type != "type":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[1].value not in ["int", "string", "bool"]:
            sys.stderr.write("Error: wrong opereand value\n")
            sys.exit(ErrorNum.WRONG_OPERAND_VALUE)
        ## decide if input is from stdin or from input_data ##
        if self.interpret.input_data == None:
            # if eof, set var to nil
            try:
                value = input()
            except EOFError:
                self.set_var(frame, name, Nil())
                return
            if self.arguments[1].value == "bool":
                if value.lower() == "true":
                    self.set_var(frame, name, True)
                else:
                    self.set_var(frame, name, False)
            elif self.arguments[1].value == "int":
                # if input is wrong number set var to nil
                try:
                    self.set_var(frame, name, int(value))
                except ValueError:
                    self.set_var(frame, name, Nil())
            else:
                self.set_var(frame, name, value)
        # wroking with saved input data
        else:
            if len(self.interpret.input_data) == 0:
                self.set_var(frame, name, Nil())
                return
            value = self.interpret.input_data.pop(0)
            if self.arguments[1].value == "bool":
                if value.lower() == "true":
                    self.set_var(frame, name, True)
                else:
                    self.set_var(frame, name, False)
            elif self.arguments[1].value == "int":
                try:
                    self.set_var(frame, name, int(value))
                except ValueError:
                    self.set_var(frame, name, Nil())
            else:
                self.set_var(frame, name, value)

## WRITE <symb> ##


class Write(Instruction):
    def __init__(self, interpret):
        super().__init__("WRITE", interpret)

    def execute(self):
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type in ["label", "type"]:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type == "var":
            frame, name = self.arguments[0].value.split('@', 1)
            self.check_var(frame, name)
            value = self.get_var(frame, name)
            # check if var is initialized
            if value is None:
                sys.stderr.write("Error: Variable not set\n")
                sys.exit(ErrorNum.MISSING_VALUE)
        else:
            value = self.arguments[0].value
        if type(value) == bool:
            if value == True:
                print("true", end="")
            else:
                print("false", end="")
        elif type(value) == Nil:
            print("", end="")
        else:
            print(value, end="")

## CONCAT <var> <symb> <symb> ##


class Concat(Instruction):
    def __init__(self, interpret):
        super().__init__("CONCAT", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        strings = [None, None]
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame2, name2 = var.value.split('@', 1)
                self.check_var(frame2, name2)
                strings[i] = self.get_var(frame2, name2)
                # check if var is initialized
                if strings[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                # check if var is string
                if type(strings[i]) != str:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "string":
                strings[i] = var.value
            else:
                sys.stderr.write("Error: Wrong type\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, strings[0] + strings[1])

## STRLEN <var> <symb> ##


class Strlen(Instruction):
    def __init__(self, interpret):
        super().__init__("STRLEN", interpret)

    def execute(self):
        if len(self.arguments) != 2:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        if self.arguments[1].type == "var":
            frame2, name2 = self.arguments[1].value.split('@', 1)
            self.check_var(frame2, name2)
            var = self.get_var(frame2, name2)
            # check if var is initialized
            if var is None:
                sys.stderr.write("Error: Variable not set\n")
                sys.exit(ErrorNum.MISSING_VALUE)
            # check if var is string
            if type(var) != str:
                sys.stderr.write("Error: Wrong type\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        elif self.arguments[1].type == "string":
            var = self.arguments[1].value
        else:
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, len(var))

## GETCHAR <var> <symb> <symb> ##


class GetChar(Instruction):
    def __init__(self, interpret):
        super().__init__("GETCHAR", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        string = None
        index = None
        # loop through arguments
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                if i == 0:
                    string = self.get_var(frame_2, name_2)
                    if string is None:
                        sys.stderr.write("Error: Variable not set\n")
                        sys.exit(ErrorNum.MISSING_VALUE)
                    if type(string) != str:
                        sys.stderr.write("Error: Wrong type\n")
                        sys.exit(ErrorNum.TYPE_ERROR)
                else:
                    index = self.get_var(frame_2, name_2)
                    if index is None:
                        sys.stderr.write("Error: Variable not set\n")
                        sys.exit(ErrorNum.MISSING_VALUE)
                    if type(index) != int:
                        sys.stderr.write("Error: Wrong type\n")
                        sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "string":
                if i == 0:
                    string = var.value
                else:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                if i == 1:
                    index = var.value
                else:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        # check if index is in string
        if index > len(string) - 1 or index < 0:
            sys.stderr.write("Error: Wrong value\n")
            sys.exit(ErrorNum.STRING_ERROR)
        self.set_var(frame, name, string[index])

## SETCHAR <var> <symb> <symb> ##


class SetChar(Instruction):
    def __init__(self, interpret):
        super().__init__("SETCHAR", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        string = self.get_var(frame, name)
        if string is None:
            sys.stderr.write("Error: Variable not set\n")
            sys.exit(ErrorNum.MISSING_VALUE)
        if type(string) != str:
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        index = None
        char = None
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                if i == 0:
                    index = self.get_var(frame_2, name_2)
                    if index is None:
                        sys.stderr.write("Error: Variable not set\n")
                        sys.exit(ErrorNum.MISSING_VALUE)
                    if type(index) != int:
                        sys.stderr.write("Error: Wrong type\n")
                        sys.exit(ErrorNum.TYPE_ERROR)
                else:
                    char = self.get_var(frame_2, name_2)
                    if char is None:
                        sys.stderr.write("Error: Variable not set\n")
                        sys.exit(ErrorNum.MISSING_VALUE)
                    if type(char) != str:
                        sys.stderr.write("Error: Wrong type\n")
                        sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                if i == 0:
                    index = var.value
                else:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "string":
                if i == 1:
                    char = var.value
                else:
                    sys.stderr.write("Error: Wrong XML structure\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        # check if index is in string and char is at least 1 char long
        if index > len(string) - 1 or index < 0 or len(char) == 0:
            sys.stderr.write("Error: Wrong value\n")
            sys.exit(ErrorNum.STRING_ERROR)
        self.set_var(frame, name, string[:index] +
                     char[0] + string[index + 1:])

## TYPE <var> <symb> ##


class Type(Instruction):
    def __init__(self, interpret):
        super().__init__("TYPE", interpret)

    def execute(self):
        if len(self.arguments) != 2:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        var = self.arguments[1]
        if var.type == "var":
            frame_2, name_2 = var.value.split('@', 1)
            self.check_var(frame_2, name_2)
            var = self.get_var(frame_2, name_2)
            if var is None:
                self.set_var(frame, name, "")
            else:
                match type(var).__name__:
                    case "int":
                        self.set_var(frame, name, "int")
                    case "str":
                        self.set_var(frame, name, "string")
                    case "bool":
                        self.set_var(frame, name, "bool")
                    case "Nil":
                        self.set_var(frame, name, "nil")
        else:
            self.set_var(frame, name, var.type)

## LABEL <label> ##


class Label(Instruction):
    def __init__(self, interpret):
        super().__init__("LABEL", interpret)

    def execute(self):
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "label":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

## JUMP <label> ##


class Jump(Instruction):
    def __init__(self, interpret):
        super().__init__("JUMP", interpret)

    def execute(self):
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "label":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if not (self.arguments[0].value in self.interpret.labels):
            sys.stderr.write("Error: Missing label\n")
            sys.exit(ErrorNum.SEMANTIC_ERROR)
        # set instruction index to label index
        self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]

## JUMPIFEQ <label> <symb1> <symb2> ##


class JumpIfEq(Instruction):
    def __init__(self, interpret):
        super().__init__("JUMPIFEQ", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "label":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if not (self.arguments[0].value in self.interpret.labels):
            sys.stderr.write("Error: Missing label\n")
            sys.exit(ErrorNum.SEMANTIC_ERROR)
        numbers = [None, None]
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
            elif var.type == "int" or var.type == "bool" or var.type == "string" or var.type == "nil":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        # check if one var is nil
        if Nil in [type(numbers[0]), type(numbers[1])]:
            if type(numbers[0]) == type(numbers[1]):
                self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]
            return
        if type(numbers[0]) != type(numbers[1]):
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        if numbers[0] == numbers[1]:
            self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]

## JUMPIFNEQ <label> <symb1> <symb2> ##


class JumpIfNeq(Instruction):
    def __init__(self, interpret):
        super().__init__("JUMPIFNEQ", interpret)

    def execute(self):
        if len(self.arguments) != 3:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "label":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if not (self.arguments[0].value in self.interpret.labels):
            sys.stderr.write("Error: Missing label\n")
            sys.exit(ErrorNum.SEMANTIC_ERROR)
        numbers = [None, None]
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
            elif var.type == "int" or var.type == "bool" or var.type == "string" or var.type == "nil":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        if Nil in [type(numbers[0]), type(numbers[1])]:
            if type(numbers[0]) != type(numbers[1]):
                self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]
            return
        if type(numbers[0]) != type(numbers[1]):
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        if numbers[0] != numbers[1]:
            self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]


class DPrint(Instruction):
    def __init__(self, interpret):
        super().__init__("DPRINT", interpret)

    def execute(self):
        pass


class Break(Instruction):
    def __init__(self, interpret):
        super().__init__("BREAK", interpret)

    def execute(self):
        pass

## EXIT <symb> ##


class Exit(Instruction):
    def __init__(self, interpret):
        super().__init__("EXIT", interpret)

    def execute(self):
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type == "var":
            frame_2, name_2 = self.arguments[0].value.split('@', 1)
            self.check_var(frame_2, name_2)
            if self.get_var(frame_2, name_2) is None:
                sys.stderr.write("Error: Variable not set\n")
                sys.exit(ErrorNum.MISSING_VALUE)
            if type(self.get_var(frame_2, name_2)) != int:
                sys.stderr.write("Error: Wrong type\n")
                sys.exit(ErrorNum.TYPE_ERROR)
            value = self.get_var(frame_2, name_2)
            sys.exit(self.get_var(frame_2, name_2))
        elif self.arguments[0].type == "int":
            value = self.arguments[0].value
        else:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        # check if value is not in range
        if value < 0 or value > 49:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_OPERAND_VALUE)
        sys.exit(int(value))
