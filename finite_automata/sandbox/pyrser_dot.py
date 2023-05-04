from pyrser import grammar, meta
from pyrser.directives import ignore


class FSMDOT(grammar.Grammar):
    """Pyrser DOT parser"""
    entry = "dot"
    grammar = """
    dot = [ graph:>_ eof ]

    graph = [ "digraph" ID '{' stmt_list '}' ]
    
    stmt_list = [ stmt stmt_list? ]
    
    stmt = [ ID ]
    
    
    ID = [ letter_ [letter_ | digit]* ]
    
    letter_ = [ letter | '_' ]
    
    letter = [ 'A'..'Z' | 'a'..'z' ]
    digit = [ '0'..'9' ]
    
    """


"""
line_comment = [ "//" ANY* '\n' ]
multiline_comment = [ "/*" ANY* "*/" ]
"""


#@meta.hook(FSMDOT)
def is_bool(self, ast, b):
    bval = self.value(b)
    if bval == "true":
        ast.node = True
    if bval == "false":
        ast.node = False
    return True


if __name__ == '__main__':
    dot = FSMDOT()
    res = dot.parse_file('sample.dot')
