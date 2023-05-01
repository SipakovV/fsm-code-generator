config = {'type': 'acceptor', 'title': 'Even ones FSM', 'description': 'FSM that accepts strings with even ones only'}
alphabet = {'0', '1'}


def parse(string: str) -> bool:
    state = '0'

    for ch in string:
        if ch not in alphabet:
            raise ValueError('Error: Invalid character')
        if state == '0':
            if ch == '0':
                state = '0'
            elif ch == '1':
                state = '1'
        elif state == '1':
            if ch == '0':
                state = '1'
            elif ch == '1':
                state = '0'

    if state in {'0'}:
        return True
    else:
        return False
