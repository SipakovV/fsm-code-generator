
class CodeGeneratorBackend:
    def begin(self, tab="\t"):
        self.code = []
        self.tab = tab
        self.level = 0

    def end(self) -> str:
        res = '\n'.join(self.code)
        return res + '\n'

    def write(self, string):
        self.code.append(self.tab * self.level + string)

    def indent(self):
        self.level += 1

    def dedent(self):
        if self.level == 0:
            raise SyntaxError('internal error in code generator')
        self.level -= 1
