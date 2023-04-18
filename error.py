# error.py
# author: Jakub Kontrik xkontr02
# Description: module with error numbers class
from enum import IntEnum


class ErrorNum(IntEnum):
    WRONG_PARAM = 10
    INPUT_FILE_ERR = 11
    OUTPUT_FILE_ERR = 12
    WRONG_XML_FORMAT = 31
    WRONG_XML_STRUCTURE = 32
    SEMANTIC_ERROR = 52
    TYPE_ERROR = 53
    UNDEFINED_VARIABLE = 54
    MISSING_FRAME = 55
    MISSING_VALUE = 56
    WRONG_OPERAND_VALUE = 57
    STRING_ERROR = 58
    INTERNAL_ERR = 99
