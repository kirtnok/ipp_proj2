# factory.py
# author: Jakub Kontrik xkontr02
# Description: factory desing pattern module
import sys
from instructions import *
from error import ErrorNum

# factory class that creates instruction objects


class Factory:
    @classmethod
    def get_instruction(cls, string: str, interpret):
        match string.upper():
            case 'MOVE':
                return Move(interpret)
            case 'CREATEFRAME':
                return CreateFrame(interpret)
            case 'PUSHFRAME':
                return PushFrame(interpret)
            case 'POPFRAME':
                return PopFrame(interpret)
            case 'DEFVAR':
                return DefVar(interpret)
            case 'CALL':
                return Call(interpret)
            case 'RETURN':
                return Return(interpret)
            case 'PUSHS':
                return PushS(interpret)
            case 'POPS':
                return PopS(interpret)
            case 'ADD':
                return Add(interpret)
            case 'SUB':
                return Sub(interpret)
            case 'MUL':
                return Mul(interpret)
            case 'IDIV':
                return IDiv(interpret)
            case 'LT':
                return Lt(interpret)
            case 'GT':
                return Gt(interpret)
            case 'EQ':
                return Eq(interpret)
            case 'AND':
                return And(interpret)
            case 'OR':
                return Or(interpret)
            case 'NOT':
                return Not(interpret)
            case 'INT2CHAR':
                return Int2Char(interpret)
            case 'STRI2INT':
                return Stri2Int(interpret)
            case 'READ':
                return Read(interpret)
            case 'WRITE':
                return Write(interpret)
            case 'CONCAT':
                return Concat(interpret)
            case 'STRLEN':
                return Strlen(interpret)
            case 'GETCHAR':
                return GetChar(interpret)
            case 'SETCHAR':
                return SetChar(interpret)
            case 'TYPE':
                return Type(interpret)
            case 'LABEL':
                return Label(interpret)
            case 'JUMP':
                return Jump(interpret)
            case 'JUMPIFEQ':
                return JumpIfEq(interpret)
            case 'JUMPIFNEQ':
                return JumpIfNeq(interpret)
            case 'EXIT':
                return Exit(interpret)
            case 'DPRINT':
                return DPrint(interpret)
            case 'BREAK':
                return Break(interpret)
            case _:
                sys.stderr.write("Error: Unknown instruction\n")
                sys.exit(ErrorNum.WRONG_XML_STRUCTURE)
