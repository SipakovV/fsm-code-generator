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
    
    stmt_list = [ stmt ';'? stmt_list? ]
    stmt = [ attr_stmt | edge_stmt | node_stmt ]
    
    attr_stmt = [ ID '=' [ ID | num ] ]
    node_stmt = [ ID:n [ '[' -> ']' ]? #add_state(_, n) ]
    edge_stmt = [ ID:from "->" ID:to [ '[' edge_attrs:spec ']' ] #is_transition(_, from, to, spec) ]
    
    edge_attrs = [ label_attr:>_ [ ',' attr ]*  ]
    label_attr = [ "label" '=' transition_spec:>_ ]
    attr = [ ID '=' ID | num ]
    
    transition_spec = 
    [ 
        '<' html_tag* events:evts html_tag* ':' html_tag* instructions:ins html_tag*  '>' #is_transition_spec(_, evts, ins) |
        '<' html_tag* events:evts html_tag* '>' #is_transition_spec(_, evts)
    ]
    
    events = [ #is_list(_) event:evt #add_item(_, evt)  [ html_tag* ',' html_tag* event:evt #add_item(_, evt) ]* ','? ]
    event = [ ID:evt #is_id(_, evt) ]
    instructions = [ #is_list(_) instruction:ins #add_item(_, ins) [ html_tag* ',' html_tag* instruction:ins #add_item(_, ins)]* ','? ]
    instruction = [ ID:ins int_num:val #is_instruction(_, ins, val) | ID:ins #is_instruction(_, ins) ]
    
    html_tag = [ "<br/>" | "<i>" | "</i>" | "<b>" | "</b>" | "<u>" | "</u>" ]
    
    ID = [ @ignore("null") [ letter_ [letter_ | digit]* ] ]
    
    letter_ = [ letter | '_' ]
    letter = [ 'A'..'Z' | 'a'..'z' ]
    num = [ int_num [ '.' digits+ ]? | '.' digits+ ]
    int_num = [ @ignore("null") '-'? digit+ ]
    digit = [ '0'..'9' ]
    digits = [ digit+ ]
    digit1_9 = [ '1'..'9' ]
    digit1_9 = [ digit1_9 digit* ]
    
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
def debug_list(self, test_var: str, l):
    print(test_var, type(l), l)
    for el in l.node:
        print(el)
    return True


@meta.hook(FSMDOT)
def debug_spec(self, test_var: str, transition):
    print(test_var, type(transition), transition)
    if hasattr(transition, 'node'):
        print('evts:', transition.node[0])
        print('ins:', transition.node[1])
    return True


@meta.hook(FSMDOT)
def is_transition_spec(self, ast, evts, ins=None):
    if ins:
        ast.node = (evts, ins)
    else:
        ast.node = (evts, [])
    print(ast.node)
    return True


@meta.hook(FSMDOT)
def is_transition(self, ast, from_, to, spec):
    if hasattr(spec.node[0], 'node'):
        events = spec.node[0].node
    else:
        events = []
    if hasattr(spec.node[1], 'node'):
        instructions = spec.node[1].node
    else:
        instructions = []
    from_state = self.value(from_)
    to_state = self.value(to)
    print(f'{events=}\n{instructions=}\n{from_state=}\n{to_state=}')
    if from_state not in TRANSITION_MAP:
        TRANSITION_MAP[from_state] = {}
    for evt in events:
        TRANSITION_MAP[from_state][evt] = (to_state, instructions)
    print(f'TRANSITION_MAP[{from_state}] = {TRANSITION_MAP[from_state]}')
    return True


@meta.hook(FSMDOT)
def is_list(self, ast):
    ast.node = []
    return True


@meta.hook(FSMDOT)
def add_item(self, ast, item):
    ast.node.append(item.node)
    print('append:', ast.node)
    return True


@meta.hook(FSMDOT)
def is_id(self, ast, s):
    ast.node = self.value(s)
    print(ast.node)
    return True


@meta.hook(FSMDOT)
def is_int(self, ast, s):
    ast.node = self.value(s)
    print(ast.node)
    return True


@meta.hook(FSMDOT)
def is_instruction(self, ast, ins, val=None):
    if val:
        print('===========')
        ast.node = (self.value(ins), int(self.value(val)))
    else:
        ast.node = self.value(ins)

    print(ast.node)
    return True


@meta.hook(FSMDOT)
def add_transition(self, ast, graph_name):
    graphname = self.value(graph_name)
    ast.node = graphname
    global GRAPH_NAME
    GRAPH_NAME = graphname
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


if __name__ == '__main__':
    dot = FSMDOT()
    res = dot.parse_file('microwave1.dot')

    print('graph:', GRAPH_NAME)
    print(STATES_SET)
    print(TRANSITION_MAP)
    #print(res.node[0])
