from frame import Frame
from error import ErrorNum
import sys


class Instruction:
    instruction_list = []

    def __init__(self, opcode, interpret):
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


class Argument:
    def __init__(self, type, value):
        self.type = type
        if type == "bool":
            if value == "true":
                self.value = True
            if value == "false":
                self.value = False
        elif type == "int":
            self.value = int(value)
        elif type == "string":
            self.value = str(value)  # TODO
        elif type == "var":
            self.value = value
        elif type == "nil" and value == "nil":
            self.value = value
        elif type == "label":
            self.value = value
        else:
            sys.stderr.write("TODO ERROR\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)


class Move(Instruction):
    def __init__(self, interpret):
        super().__init__("MOVE", interpret)

    def execute(self):
        if self.arguments[0].type != "var":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if self.arguments[1].type in ["type", "label"]:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(self.arguments) != 2:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

        frame, name = self.arguments[0].value.split('@', 1)
        self.check_var(frame, name)
        value = 0
        if self.arguments[1].type == "var":
            frame_2, name_2 = self.arguments[1].value.split('@', 1)
            self.check_var(frame_2, name_2)
            value = self.get_var(frame_2, name_2)
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
        if self.arguments[0].type != "var": 
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(self.arguments) != 1:
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
        pass


class Return(Instruction):
    def __init__(self, interpret):
        super().__init__("RETURN", interpret)

    def execute(self):
        pass


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
        if self.arguments[0].type != "var": 
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(self.arguments) != 3:
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
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        self.set_var(frame, name, numbers[0] + numbers[1])


class Sub(Instruction):
    def __init__(self, interpret):
        super().__init__("SUB", interpret)

    def execute(self):
        if self.arguments[0].type != "var": 
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(self.arguments) != 3:
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
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        self.set_var(frame, name, numbers[0] - numbers[1])


class Mul(Instruction):
    def __init__(self, interpret):
        super().__init__("MUL", interpret)

    def execute(self):
        if self.arguments[0].type != "var": 
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(self.arguments) != 3:
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
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        self.set_var(frame, name, numbers[0] * numbers[1])


class IDiv(Instruction):
    def __init__(self, interpret):
        super().__init__("IDIV", interpret)

    def execute(self):
        if self.arguments[0].type != "var": 
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(self.arguments) != 3:
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
                if type(numbers[i]) != int:
                    sys.stderr.write("Error: Wrong type\n")
                    sys.exit(ErrorNum.TYPE_ERROR)
                if numbers[i] is None:
                    sys.stderr.write("Error: Variable not set\n")
                    sys.exit(ErrorNum.MISSING_VALUE)
            elif var.type == "int":
                numbers[i] = var.value
            else:
                sys.stderr.write("Error: Wrong XML structure\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        try:
            self.set_var(frame, name, int(numbers[0] / numbers[1]))
        except ZeroDivisionError:
            sys.stderr.write("Error: Division by zero\n")
            sys.exit(ErrorNum.WRONG_OPERAND_VALUE)


class Lt(Instruction):
    def __init__(self, interpret):
        super().__init__("LT", interpret)

    def execute(self):
        pass


class Gt(Instruction):
    def __init__(self, interpret):
        super().__init__("GT", interpret)

    def execute(self):
        pass


class Eq(Instruction):
    def __init__(self, interpret):
        super().__init__("EQ", interpret)

    def execute(self):
        pass


class And(Instruction):
    def __init__(self, interpret):
        super().__init__("AND", interpret)

    def execute(self):
        pass


class Or(Instruction):
    def __init__(self, interpret):
        super().__init__("OR", interpret)

    def execute(self):
        pass


class Not(Instruction):
    def __init__(self, interpret):
        super().__init__("NOT", interpret)

    def execute(self):
        pass


class Int2Char(Instruction):
    def __init__(self, interpret):
        super().__init__("INT2CHAR", interpret)

    def execute(self):
        pass


class Stri2Int(Instruction):
    def __init__(self, interpret):
        super().__init__("STRI2INT", interpret)

    def execute(self):
        pass


class Read(Instruction):
    def __init__(self, interpret):
        super().__init__("READ", interpret)

    def execute(self):
        pass


class Write(Instruction):
    def __init__(self, interpret):
        super().__init__("WRITE", interpret)

    def execute(self):
        pass


class Concat(Instruction):
    def __init__(self, interpret):
        super().__init__("CONCAT", interpret)

    def execute(self):
        pass


class Strlen(Instruction):
    def __init__(self, interpret):
        super().__init__("STRLEN", interpret)

    def execute(self):
        pass


class GetChar(Instruction):
    def __init__(self, interpret):
        super().__init__("GETCHAR", interpret)

    def execute(self):
        pass


class SetChar(Instruction):
    def __init__(self, interpret):
        super().__init__("SETCHAR", interpret)

    def execute(self):
        pass


class Type(Instruction):
    def __init__(self, interpret):
        super().__init__("TYPE", interpret)

    def execute(self):
        pass


class Label(Instruction):
    def __init__(self, interpret):
        super().__init__("LABEL", interpret)

    def execute(self):
        if self.arguments[0].type != "label":
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        if len(self.arguments) != 1:
            sys.stderr.write("Error: Wrong XML structure\n")
            sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
        


class Jump(Instruction):
    def __init__(self, interpret):
        super().__init__("JUMP", interpret)

    def execute(self):
        pass


class JumpIfEq(Instruction):
    def __init__(self, interpret):
        super().__init__("JUMPIFEQ", interpret)

    def execute(self):
        pass


class JumpIfNeq(Instruction):
    def __init__(self, interpret):
        super().__init__("JUMPIFNEQ", interpret)

    def execute(self):
        pass


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
        pass
