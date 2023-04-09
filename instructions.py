
class Instruction:
    instruction_list = []
    def __init__(self, opcode):
        self.opcode = opcode
        self.instruction_list.append(self)
        self.arguments = []
    def execute(self):
        pass
    def set_arg(self, arg):
        self.arguments.append(Argument(arg.attrib.get('type'), arg.text))

class Argument:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Move(Instruction):
    def __init__(self):
        super().__init__("MOVE")

    def execute(self):
        pass

class CreateFrame(Instruction):
    def __init__(self):
        super().__init__("CREATEFRAME")

    def execute(self):
        pass


class PushFrame(Instruction):
    def __init__(self):
        super().__init__("PUSHFRAME")

    def execute(self):
        pass

class PopFrame(Instruction):
    def __init__(self):
        super().__init__("POPFRAME")

    def execute(self):
        pass


class DefVar(Instruction):
    def __init__(self):
        super().__init__("DEFVAR")

    def execute(self):
        pass


class Call(Instruction):
    def __init__(self):
        super().__init__("CALL")

    def execute(self):
        pass


class Return(Instruction):
    def __init__(self):
        super().__init__("CALL")

    def execute(self):
        pass

class PushS(Instruction):
    def __init__(self):
        super().__init__("PUSHS")

    def execute(self):
        pass

class PopS(Instruction):
    def __init__(self):
        super().__init__("POPS")

    def execute(self):
        pass

class Add(Instruction):
    def __init__(self):
        super().__init__("ADD")

    def execute(self):
        pass

class Sub(Instruction):
    def __init__(self):
        super().__init__("SUB")

    def execute(self):
        pass

class Mul(Instruction):
    def __init__(self):
        super().__init__("MUL")

    def execute(self):
        pass

class IDiv(Instruction):
    def __init__(self):
        super().__init__("IDIV")

    def execute(self):
        pass

class Lt(Instruction):
    def __init__(self):
        super().__init__("LT")

    def execute(self):
        pass

class Gt(Instruction):
    def __init__(self):
        super().__init__("GT")

    def execute(self):
        pass

class Eq(Instruction):
    def __init__(self):
        super().__init__("EQ")

    def execute(self):
        pass

class And(Instruction):
    def __init__(self):
        super().__init__("AND")

    def execute(self):
        pass

class Or(Instruction):
    def __init__(self):
        super().__init__("OR")

    def execute(self):
        pass

class Not(Instruction):
    def __init__(self):
        super().__init__("NOT")

    def execute(self):
        pass

class Int2Char(Instruction):
    def __init__(self):
        super().__init__("INT2CHAR")

    def execute(self):
        pass

class Stri2Int(Instruction):
    def __init__(self):
        super().__init__("STRI2INT")

    def execute(self):
        pass

class Read(Instruction):
    def __init__(self):
        super().__init__("READ")

    def execute(self):
        pass

class Write(Instruction):
    def __init__(self):
        super().__init__("WRITE")

    def execute(self):
        pass

class Concat(Instruction):
    def __init__(self):
        super().__init__("CONCAT")

    def execute(self):
        pass

class Strlen(Instruction):
    def __init__(self):
        super().__init__("STRLEN")

    def execute(self):
        pass

class GetChar(Instruction):
    def __init__(self):
        super().__init__("GETCHAR")

    def execute(self):
        pass

class SetChar(Instruction):
    def __init__(self):
        super().__init__("SETCHAR")

    def execute(self):
        pass

class Type(Instruction):
    def __init__(self):
        super().__init__("TYPE")

    def execute(self):
        pass

class Label(Instruction):
    def __init__(self):
        super().__init__("LABEL")
    def execute(self):
        pass

class Jump(Instruction):
    def __init__(self):
        super().__init__("JUMP")

    def execute(self):
        pass

class JumpIfEq(Instruction):
    def __init__(self):
        super().__init__("JUMPIFEQ")

    def execute(self):
        pass

class JumpIfNeq(Instruction):
    def __init__(self):
        super().__init__("JUMPIFNEQ")

    def execute(self):
        pass

class DPrint(Instruction):
    def __init__(self):
        super().__init__("DPRINT")

    def execute(self):
        pass

class Break(Instruction):
    def __init__(self):
        super().__init__("BREAK")

    def execute(self):
        pass

class Exit(Instruction):
    def __init__(self):
        super().__init__("EXIT")

    def execute(self):
        pass
