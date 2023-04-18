class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        else:
            return self.items.pop()

    def top(self):
        if self.is_empty():
            return None
        else:
            return self.items[-1]

    def is_empty(self):
        return not self.items
