from pyrser import grammar, meta
from pyrser.directives import ignore


class JSON(grammar.Grammar):
    """Pyrser JSON parser"""
    entry = "json"
    grammar = """
    json =[ object:>_ eof ]

    object =
    [
        '{' #is_dict(_) [pair:p #add_kv(_, p) [',' pair:p #add_kv(_, p) ]*]? '}'
    ]

    pair = [ string:s ':' value:v #is_pair(_, s, v) ]

    value =
    [

        [number | object | array]:>_
        | [
            string:s #is_str(_, s)
            | "true":t #is_bool(_, t)
            | "false":f #is_bool(_, f)
            | "null" #is_none(_)
        ]

    ]

    array =
    [
        '[' #is_array(_) [value:v #add_item(_, v) [',' value:v #add_item(_, v)] *]? ']'
    ]

    number = [ @ignore("null") [int frac? exp?]:n #is_num(_, n) ]

    int =
    [
        '-'?
        [
            digit1_9s
            | digit
        ]
    ]

    frac = [ '.' digits ]

    exp = [ e digits ]

    digit = [ '0'..'9' ]

    digit1_9 = [ '1'..'9' ]

    digits = [ digit+ ]

    digit1_9s = [ digit1_9 digits]

    e = [ ['e'|'E'] ['+'|'-']? ]

    """


@meta.hook(JSON)
def is_num(self, ast, n):
    ast.node = float(self.value(n))
    return True


@meta.hook(JSON)
def is_str(self, ast, s):
    ast.node = self.value(s).strip('"')
    return True


@meta.hook(JSON)
def is_bool(self, ast, b):
    bval = self.value(b)
    if bval == "true":
        ast.node = True
    if bval == "false":
        ast.node = False
    return True


@meta.hook(JSON)
def is_none(self, ast):
    ast.node = None
    return True


@meta.hook(JSON)
def is_pair(self, ast, s, v):
    ast.node = (self.value(s).strip('"'), v.node)
    return True


@meta.hook(JSON)
def is_array(self, ast):
    ast.node = []
    return True


@meta.hook(JSON)
def add_item(self, ast, item):
    ast.node.append(item.node)
    return True


@meta.hook(JSON)
def is_dict(self, ast):
    ast.node = {}
    return True


@meta.hook(JSON)
def add_kv(self, ast, item):
    ast.node[item.node[0]] = item.node[1]
    return True


if __name__ == '__main__':
    json = JSON()
    res = json.parse("""
        {"test" : 12,"puf" : [1, 2, 3],"hello": {
                "world": "yes",
                "mir": "da",
                "value": 1337,
                "list": ["oppa", "na"]
                }
        }
    """)
    if res.node['hello']['world'] == 'yes':
        print("OK")
