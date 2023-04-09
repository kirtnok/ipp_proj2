import sys
from instructions import *
from error import ErrorNum

class Factory:
    @classmethod
    def get_instruction(cls,string: str, ):
        match string.upper():
            case 'MOVE':
                return Move()
            case 'CREATEFRAME':
                return CreateFrame()
            case 'PUSHFRAME':
                return PushFrame()
            case 'POPFRAME':
                return PopFrame()
            case 'DEFVAR':
                return DefVar()
            case 'CALL':
                return Call()
            case 'RETURN':
                return Return()
            case 'PUSHS':
                return PushS()
            case 'POPS':
                return PopS()
            case 'ADD':
                return Add()
            case 'SUB':
                return Sub()
            case 'MUL':
                return Mul()
            case 'IDIV':
                return IDiv()
            case 'LT':
                return Lt()
            case 'GT':
                return Gt()
            case 'EQ':
                return Eq()
            case 'AND':
                return And()
            case 'OR':
                return Or()
            case 'NOT':
                return Not()
            case 'INT2CHAR':
                return Int2Char()
            case 'STRI2INT':
                return Stri2Int()
            case 'READ':
                return Read()
            case 'WRITE':
                return Write()
            case 'CONCAT':
                return Concat()
            case 'STRLEN':
                return Strlen()
            case 'GETCHAR':
                return GetChar()
            case 'SETCHAR':
                return SetChar()
            case 'TYPE':
                return Type()
            case 'LABEL':
                return Label()
            case 'JUMP':
                return Jump()
            case 'JUMPIFEQ':
                return JumpIfEq()
            case 'JUMPIFNEQ':
                return JumpIfNeq()
            case 'EXIT':
                return Exit()
            case 'DPRINT':
                return DPrint()
            case 'BREAK':
                return Break()
            case _:
                sys.stderr.write("Error: Unknown instruction\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)

