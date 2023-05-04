from pyrser import grammar, meta
from pyrser.directives import ignore


STATES_SET = set()


class FSMDOT(grammar.Grammar):
    """Pyrser DOT parser"""
    entry = "dot"
    grammar = """
    dot = [ graph:>_ eof ]

    graph = [ @ignore("C/C++") "digraph" ID:n #add_graph(_, n) '{' stmt_list:l '}']
    
    stmt_list = [ stmt stmt_list? ]
    
    stmt = [ node_stmt ]
    
    node_stmt = [ ID:n #add_state(_, n)]
    
    
    ID = [ @ignore("null") [ letter_ [letter_ | digit]* ] ]
    
    letter_ = [ letter | '_' ]
    
    letter = [ 'A'..'Z' | 'a'..'z' ]
    digit = [ '0'..'9' ]
    
    """


"""
line_comment = [ "//" ANY* '\n' ]
multiline_comment = [ "/*" ANY* "*/" ]
"""


@meta.hook(FSMDOT)
def add_state(self, ast, state_name):
    state = self.value(state_name)
    ast.node = state
    if state in STATES_SET:
        print('Duplicate state declaration')
        return False
    else:
        STATES_SET.add(state)
    print(ast)
    return True


@meta.hook(FSMDOT)
def add_graph(self, ast, graph_name):
    ast.node = self.value(graph_name)
    print('graph:', ast)
    return True


if __name__ == '__main__':
    dot = FSMDOT()
    res = dot.parse_file('sample.dot')

    print(STATES_SET)
    #print(res.node[0])
