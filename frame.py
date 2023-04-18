class Frame:
    def __init__(self):
        self.vars = {}

    def get_var(self, name):
        return self.vars[name]

    def set_var(self, name, value):
        self.vars[name] = value

    def get_vars(self):
        return self.vars
