import sys
from stack import Stack
from frame import Frame
from error import ErrorNum

class Interpret:
    def __init__(self, input_file):
        self.labels = {}
        self.call_stack = Stack()
        self.data_stack = Stack()
        self.inst_index = 0
        self.tmp_frame = None
        self.global_frame = Frame()
        self.local_frames = Stack()
        
        try:
            input_file = open(input_file, 'r')
            self.input_data = input_file.read().splitlines()
            input_file.close()
        
        except FileNotFoundError:
            sys.stderr.write("Error: File not found\n")
            sys.exit(ErrorNum.INPUT_FILE_ERR)
        except TypeError:
            self.input_data = None

    def run(self, inst):
        while self.inst_index != len(inst.instruction_list):
            inst.instruction_list[self.inst_index].execute()
            self.inst_index += 1
