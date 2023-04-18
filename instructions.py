from frame import Frame
from error import ErrorNum
import sys
from interpret_class import Interpret
import re


class Instruction:
    instruction_list = []

    def __init__(self, opcode, interpret: Interpret):
        self.opcode = opcode
        self.instruction_list.append(self)
        self.arguments = []
        self.interpret = interpret

    def execute(self):
        pass

    def set_arg(self, arg):
        self.arguments.append(Argument(arg.attrib.get('type'), arg.text))

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

    def get_var(self, frame, name):
        if frame == "GF":
            return self.interpret.global_frame.get_var(name)
        elif frame == "LF":
            return self.interpret.local_frames.top().get_var(name)
        elif frame == "TF":
            return self.interpret.tmp_frame.get_var(name)

    def set_var(self, frame, name, value):
        if frame == "GF":
            self.interpret.global_frame.set_var(name, value)
        elif frame == "LF":
            self.interpret.local_frames.top().set_var(name, value)
        elif frame == "TF":
            self.interpret.tmp_frame.set_var(name, value)


class Nil:
    def __init__(self):
        self.value = None


class Argument:
    def __init__(self, type, value: str):
        self.type = type
        if type == "bool":
            if value == "true":
                self.value = True
            if value == "false":
                self.value = False
        elif type == "int":
            try:
                self.value = int(value, 0)
            except ValueError:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
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


class Move(Instruction):
    def __init__(self, interpret):
        super().__init__("MOVE", interpret)

    def execute(self):
        if len(self.arguments) != 2:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[1].type in ["type", "label"]:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        value = 0
        if self.arguments[1].type == "var":
            frame_2, name_2 = self.arguments[1].value.split('@', 1)
            self.check_var(frame_2, name_2)
            value = self.get_var(frame_2, name_2)
            if value is None:
                sys.stderr.write("Error: Variable not defined\n")
                sys.exit(ErrorNum.MISSING_VALUE)
        else:
            value = self.arguments[1].value
        self.set_var(frame, name, value)


class CreateFrame(Instruction):
    def __init__(self, interpret):
        super().__init__("CREATEFRAME", interpret)

    def execute(self):
        if len(self.arguments) != 0:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        self.interpret.tmp_frame = Frame()


class PushFrame(Instruction):
    def __init__(self, interpret):
        super().__init__("PUSHFRAME", interpret)

    def execute(self):
        if len(self.arguments) != 0:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

        if self.interpret.tmp_frame is None:
            sys.stderr.write("Error: Temp frame does not exist\n")
            sys.exit(ErrorNum.MISSING_FRAME)

        self.interpret.local_frames.push(self.interpret.tmp_frame)
        self.interpret.tmp_frame = None


class PopFrame(Instruction):
    def __init__(self, interpret):
        super().__init__("POPFRAME", interpret)

    def execute(self):
        if len(self.arguments) != 0:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

        if self.interpret.local_frames.is_empty():
            sys.stderr.write("Error: Temp frame does not exist\n")
            sys.exit(ErrorNum.MISSING_FRAME)
        self.interpret.tmp_frame = self.interpret.local_frames.pop()


class DefVar(Instruction):
    def __init__(self, interpret):
        super().__init__("DEFVAR", interpret)

    def execute(self):
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        frame, name = self.arguments[0].value.split('@', 1)
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
        self.interpret.call_stack.push(self.interpret.inst_index)
        self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]


class Return(Instruction):
    def __init__(self, interpret):
        super().__init__("RETURN", interpret)

    def execute(self):
        if len(self.arguments) != 0:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.interpret.call_stack.is_empty():
            sys.stderr.write("Error: Call stack is empty\n")
            sys.exit(ErrorNum.MISSING_VALUE)
        self.interpret.inst_index = self.interpret.call_stack.pop()


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
        if self.arguments[0].type == "var":
            frame, name = self.arguments[0].value.split('@', 1)
            self.check_var(frame, name)
            if self.get_var(frame, name) is None:
                sys.stderr.write("Error: Empty var\n")
                sys.exit(ErrorNum.MISSING_VALUE)
            self.interpret.data_stack.push(self.get_var(frame, name))
        else:
            self.interpret.data_stack.push(self.arguments[0].value)


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
        self.check_var(frame, name)
        self.set_var(frame, name, self.interpret.data_stack.pop())


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
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] + numbers[1])


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
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] - numbers[1])


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
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] * numbers[1])


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
        for i, var in enumerate(self.arguments[1:]):
            if var.type == "var":
                frame_2, name_2 = var.value.split('@', 1)
                self.check_var(frame_2, name_2)
                numbers[i] = self.get_var(frame_2, name_2)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        try:
            self.set_var(frame, name, int(numbers[0] / numbers[1]))
        except ZeroDivisionError:
            sys.stderr.write("Error: Division by zero\n")
            sys.exit(ErrorNum.WRONG_OPERAND_VALUE)


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
        self.set_var(frame, name, numbers[0] < numbers[1])


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
                if type(numbers[i]) != int and type(numbers[i]) != bool and type(numbers[i]) != str and type(numbers[i]) != Nil:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "int" or var.type == "bool" or var.type == "string" or var.type == "nil":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        if Nil in [type(numbers[0]), type(numbers[1])]:
            self.set_var(frame, name, type(numbers[0]) == type(numbers[1]))
            return
        if type(numbers[0]) != type(numbers[1]):
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, numbers[0] == numbers[1])


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
        if index > len(string) - 1 or index < 0:
            sys.stderr.write("Error: Wrong value\n")
            sys.exit(ErrorNum.STRING_ERROR)
        self.set_var(frame, name, ord(string[index]))


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
            sys.stderr.write("Error: wrong opereeand value\n")
            sys.exit(ErrorNum.WRONG_OPERAND_VALUE)
        if self.interpret.input_data == None:
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
                try:
                    self.set_var(frame, name, int(value))
                except ValueError:
                    self.set_var(frame, name, Nil())
            else:
                self.set_var(frame, name, value)

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
                if strings[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
                if type(strings[i]) != str:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
            elif var.type == "string":
                strings[i] = var.value
            else:
                sys.stderr.write("Error: Wrong type\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, strings[0] + strings[1])


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
            if var is None:
                sys.stderr.write("Error: Variable not set\n")
                sys.exit(ErrorNum.MISSING_VALUE)
            if type(var) != str:
                sys.stderr.write("Error: Wrong type\n")
                sys.exit(ErrorNum.TYPE_ERROR)
        elif self.arguments[1].type == "string":
            var = self.arguments[1].value
        else:
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        self.set_var(frame, name, len(var))


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
        if index > len(string) - 1 or index < 0:
            sys.stderr.write("Error: Wrong value\n")
            sys.exit(ErrorNum.STRING_ERROR)
        self.set_var(frame, name, string[index])


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
        if index > len(string) - 1 or index < 0 or len(char) == 0:
            sys.stderr.write("Error: Wrong value\n")
            sys.exit(ErrorNum.STRING_ERROR)
        self.set_var(frame, name, string[:index] +
                     char[0] + string[index + 1:])


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
        self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]


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
        if Nil in [type(numbers[0]), type(numbers[1])]:
            if type(numbers[0]) == type(numbers[1]):
                self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]
            return
        if type(numbers[0]) != type(numbers[1]):
            sys.stderr.write("Error: Wrong type\n")
            sys.exit(ErrorNum.TYPE_ERROR)
        if numbers[0] == numbers[1]:
            self.interpret.inst_index = self.interpret.labels[self.arguments[0].value]


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
        if value < 0 or value > 49:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_OPERAND_VALUE)
        sys.exit(int(value))
