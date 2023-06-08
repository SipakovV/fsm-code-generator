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

    graph = [ @ignore("C/C++") "strict"? "digraph" ID? '{' stmt_list:>_ '}']

    stmt_list = [ #is_fsm_config(_) [ stmt:s #add_entry(_, s) ';'? ]+ ]

    stmt = 
    [ 
        ID '=' [ ID | num | string ]
        | attr_stmt
        | edge_stmt:>_
        | node_stmt:>_
    ]

    attr_stmt = [ ["graph" | "node" | "edge"] '[' -> ']' ]

    node_stmt =
    [ 
        start_tag [ '[' -> ']' ]?
        | node_id:n [ '[' -> ']' ]? #is_state_entry(_, n)
    ]

    edge_stmt = [ 
        start_tag "->" node_id:to '[' init_edge_attrs:spec ']' #is_init_transition(_, to, spec)
        | start_tag "->" node_id:to #is_init_transition(_, to)
        | node_id:from "->" node_id:to [ '[' edge_attrs:spec ']' ] #is_transition(_, from, to, spec)
    ]


    node_id = [ ID:>_ port? ]

    port = 
    [ 
        ':' compass_pt
        | ':' ID [ ':' compass_pt ]?
    ]

    compass_pt = [ @ignore("null") [ "nw" | "ne" | 'n' | 'e' | "se" | "sw" | 's' | 'w' | 'c' | '_' ] ]


    edge_attrs = [ label_attr:>_ [ ','? attr ]*  ]

    init_edge_attrs = [ init_label_attr:>_ [ ','? attr ]*  ]

    label_attr = 
    [
        "label" '=' transition_spec:>_ 
    ]

    init_label_attr = 
    [
        "label" '=' init_transition_spec:>_ 
    ]

    attr = [ ID '=' [ ID | num | string ] ]

    transition_spec = 
    [ 
        '<' html_tag* events:evts html_tag* ':' html_tag* instructions:ins html_tag*  '>' #is_transition_spec(_, evts, ins)
        | '<' html_tag* events:evts html_tag* '>' #is_transition_spec(_, evts)
        | '\"' events:evts ':' instructions:ins '\"' #is_transition_spec(_, evts, ins)
        | '\"' events:evts '\"' #is_transition_spec(_, evts)
    ]

    init_transition_spec = 
    [ 
        '<' html_tag* instructions:ins html_tag* '>' #is_init_transition_spec(_, ins)
        | '\"' instructions:ins '\"' #is_init_transition_spec(_, ins)
    ]


    events = 
    [
        #is_list(_) event:evt #add_item(_, evt) [ html_tag* ',' html_tag* event:evt #add_item(_, evt) ]* ','? 
    ]

    event = [ ID:>_ ]

    instructions = [ #is_list(_) instruction:ins #add_item(_, ins) [ html_tag* ',' html_tag* instruction:ins #add_item(_, ins)]* html_tag* ','? ]

    instruction = 
    [ 
        ID:ins int_num:val #is_instruction(_, ins, val) 
        | ID:ins #is_instruction(_, ins)
    ]


    html_tag = [ "<br/>" | "<i>" | "</i>" | "<b>" | "</b>" | "<u>" | "</u>" ]

    ID = 
    [ 
        @ignore("null") '\"' id_str:s '\"' #is_id(_, s)
        | id_str:s #is_id(_, s)
    ]
    start_tag = [ "START" | @ignore("null") '\"' "START" '\"' ]
    
    id_str = [ @ignore("null") letter_ [letter_ | digit]* ]

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
def print_config(self, ast):
    print('config:', ast.node)
    return True


@meta.hook(FSMDOT)
def debug_print(self, test_var: str, arg=None):
    if arg:
        print(f'{test_var} = {self.value(arg)}')
    else:
        print(f'{test_var}')
    return True


@meta.hook(FSMDOT)
def debug_var(self, test_var: str, arg=None):
    print(f'{test_var} = {arg.node}')
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
    # print(ast.node)
    return True


@meta.hook(FSMDOT)
def is_init_transition_spec(self, ast, ins=None):
    if ins:
        ast.node = ([], ins)
    else:
        ast.node = ([], [])
    # print('init spec:', ast.node)
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
    from_state = from_.node
    to_state = to.node
    # print(f'{events=}\n{instructions=}\n{from_state=}\n{to_state=}')
    '''
    if from_state not in TRANSITION_MAP:
        TRANSITION_MAP[from_state] = {}
    for instr in instructions:
        INSTRUCTIONS_SET.add(instr)
    for evt in events:
        TRANSITION_MAP[from_state][evt] = (to_state, instructions)
        ALPHABET.add(evt)
    '''
    # print(f'TRANSITION_MAP[{from_state}] = {TRANSITION_MAP[from_state]}')

    ast.node = {
        'type': 'transition',
        'from': from_state,
        'to': to_state,
        'events': events,
        'instructions': instructions,
    }

    return True


@meta.hook(FSMDOT)
def is_init_transition(self, ast, to, spec=None):
    if spec:
        # print(f'{spec=}')
        if hasattr(spec.node[0], 'node'):
            if spec.node[0].node:
                print('Initial transition must not contain events')
                return False
        if hasattr(spec.node[1], 'node'):
            instructions = spec.node[1].node
        else:
            instructions = []
    else:
        instructions = []
    to_state = to.node
    # print(f'{instructions=}\n{to_state=}')
    for instr in instructions:
        INSTRUCTIONS_SET.add(instr)

    global INITIAL_STATE, INITIAL_ISTRUCTIONS
    INITIAL_STATE = to_state
    INITIAL_ISTRUCTIONS = instructions

    ast.node = {
        'type': 'init_transition',
        'to': to_state,
        'instructions': instructions,
    }

    return True


@meta.hook(FSMDOT)
def is_list(self, ast):
    ast.node = []
    return True


@meta.hook(FSMDOT)
def add_item(self, ast, item):
    ast.node.append(item.node)
    # print('append:', ast.node)
    return True


@meta.hook(FSMDOT)
def is_id(self, ast, s):
    ast.node = self.value(s)
    #print('|', ast.node, '|')
    return True


@meta.hook(FSMDOT)
def is_quoted_id(self, ast, s):
    ast.node = self.value(s)
    #print(ast.node)
    return True


@meta.hook(FSMDOT)
def is_int(self, ast, s):
    ast.node = int(self.value(s))
    # print(ast.node)
    return True


@meta.hook(FSMDOT)
def is_float(self, ast, s):
    ast.node = float(self.value(s))
    # print(ast.node)
    return True


@meta.hook(FSMDOT)
def is_instruction(self, ast, ins, val=None):
    if val:
        # print('===========')
        ast.node = (ins.node, self.value(val))
    else:
        ast.node = ins.node

    #print('instruction', ast.node)
    return True


@meta.hook(FSMDOT)
def add_transition(self, ast, graph_name):
    graphname = self.value(graph_name)
    ast.node = graphname
    global GRAPH_NAME
    GRAPH_NAME = graphname
    return True


@meta.hook(FSMDOT)
def is_state_entry(self, ast, id_node):
    state = id_node.node
    ast.node = {
        'type': 'state',
        'name': state,
    }

    # STATES_SET.add(state)
    # print('added state', state)
    return True


@meta.hook(FSMDOT)
def add_graph_name(self, ast, graph_name):
    name = graph_name.node
    ast.node['name'] = name
    return True


@meta.hook(FSMDOT)
def add_entry(self, ast, entry_node):
    if hasattr(entry_node, 'node'):
        entry = entry_node.node
        # print('entry:', entry)
        entry_type = entry['type']
        if entry_type == 'state':
            # print(f'State entry added: {entry["name"]}')
            ast.node['state_set'].add(entry["name"])
        elif entry_type == 'transition':
            # print(f'Transition entry added: from {entry["from"]} to {entry["to"]}\n  '
            #      f'Events: {entry["events"]}\n  Instructions: {entry["instructions"]}')
            if entry['from'] not in ast.node['transition_map']:
                ast.node['transition_map'][entry['from']] = {}
            for event in entry['events']:
                ast.node['transition_map'][entry['from']][event] = (entry['to'], entry['instructions'])
                ast.node['alphabet'].add(event)
            for ins in entry['instructions']:
                if type(ins) is tuple:
                    ast.node['instructions_set'].add(ins[0])
                else:
                    ast.node['instructions_set'].add(ins)
        elif entry_type == 'init_transition':
            # print(f'Init transition entry added: {entry["to"]}:\n  '
            #      f'Instructions: {entry["instructions"]}')
            if ast.node['initial_state']:
                print(f'More than one initial state: {ast.node["initial_state"]} - {entry["to"]}')
                return False
            else:
                ast.node['initial_state'] = entry['to']
                ast.node['initial_instructions'] = entry['instructions']
            for ins in entry['instructions']:
                if type(ins) is tuple:
                    ast.node['instructions_set'].add(ins[0])
                else:
                    ast.node['instructions_set'].add(ins)
    return True


@meta.hook(FSMDOT)
def is_fsm_config(self, ast):
    ast.node = {
        'name': '',
        'state_set': set(),
        'alphabet': set(),
        'instructions_set': set(),
        'initial_state': None,
        'initial_instructions': [],
        'transition_map': {},
    }
    return True
