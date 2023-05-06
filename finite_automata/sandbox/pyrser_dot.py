from pyrser import grammar, meta
from pyrser.directives import ignore


STATES_SET = set()
ALPHABET = set()
INSTRUCTIONS_SET = set()
INITIAL_STATE: str
INITIAL_ISTRUCTIONS = []
TRANSITION_MAP = {}
GRAPH_NAME = 'sample_graph'


class FSMDOT(grammar.Grammar):
    """Pyrser DOT parser"""
    entry = "dot"
    grammar = """
    dot = [ graph:>_ eof ]

    graph = [ @ignore("C/C++") "digraph" ID:n #add_graph(_, n) '{' stmt_list:l '}']
    
    stmt_list = [ stmt stmt_list? ]
    stmt = [ edge_stmt | node_stmt ]
    
    node_stmt = [ ID:n [ '[' -> ']' ]? #add_state(_, n) ]
    edge_stmt = [ ID:from "->" ID:to [ '[' edge_attrs ']' ] #debug_print('from', from) #debug_print('to', to) ]
    
    edge_attrs = [ label_attr [ ',' attr ]*  ]
    label_attr = [ "label" '=' transition_spec ]
    attr = [ ID '=' ID ]
    
    transition_spec = [ '<' html_tag* events html_tag* [ ':' html_tag* instructions html_tag* ]? '>' ]
    
    events = [ event [ html_tag* ',' html_tag* event ]* ]
    event = [ ID ]
    instructions = [ instruction [ html_tag* ',' html_tag* instruction ]* ]
    instruction = [ ID ]
    
    html_tag = [ "<br/>" | "<i>" | "</i>" | "<b>" | "</b>" | "<u>" | "</u>" ]
    
    ID = [ @ignore("null") [ letter_ [letter_ | digit]* ] ]
    
    letter_ = [ letter | '_' ]
    letter = [ 'A'..'Z' | 'a'..'z' ]
    digit = [ '0'..'9' ]
    
    """


"""
node_attrs = [ attr [ ',' attr ]* ]

line_comment = [ "//" ANY* '\n' ]
multiline_comment = [ "/*" ANY* "*/" ]
"""


@meta.hook(FSMDOT)
def debug_print(self, test_var: str, arg):
    print(f'{test_var} = {self.value(arg)}')
    return True


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
    graphname = self.value(graph_name)
    ast.node = graphname
    global GRAPH_NAME
    GRAPH_NAME = graphname
    return True


@meta.hook(FSMDOT)
def add_transition(self, ast, graph_name):
    graphname = self.value(graph_name)
    ast.node = graphname
    global GRAPH_NAME
    GRAPH_NAME = graphname
    return True


if __name__ == '__main__':
    dot = FSMDOT()
    res = dot.parse_file('sample.dot')

    print('graph:', GRAPH_NAME)
    print(STATES_SET)
    #print(res.node[0])
