import sys
from stack import Stack
from frame import Frame
from error import ErrorNum

class Interpret:
    def __init__(self,):
        self.labels = {}
        self.call_stack = Stack()
        self.data_stack = Stack()
        self.inst_index = 0
        self.tmp_frame = None
        self.global_frame = Frame()
        self.local_frames = Stack()

    def run(self, inst):
        for i in range(len(inst.instruction_list)):
            if inst.instruction_list[i].opcode == "JUMP" or inst.instruction_list[i].opcode == "CALL":
                if not (inst.instruction_list[i].arguments[0].value in self.labels):
                    sys.stderr.write("Error: Missing label\n")
                    sys.exit(ErrorNum.SEMANTIC_ERROR)
                else:
                    self.labels[inst.instruction_list[i]] = i
        while self.inst_index != len(inst.instruction_list):
            inst.instruction_list[self.inst_index].execute()
            self.inst_index += 1
