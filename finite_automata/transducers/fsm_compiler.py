import argparse

from fsm_core.dot_parser import FSMDOT
from fsm_core.transducer_fsm import TransducerFSM


def compile_fsm(filename, lang, visualize='full'):
    dot = FSMDOT()
    res = dot.parse_file(filename)

    print(res.node)

    fsm = TransducerFSM(**res.node)

    print()
    print(fsm)

    fsm.generate_code_python()
    fsm.visualize(all_states=True)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='FSM compiler. Generates Python/C source file from DOT file containing description of FSM')
    arg_parser.add_argument('--verbose', default=False, action='store_true', help='Comment all stages of compiling')
    #arg_parser.add_argument('--visualize', default=False, action='store_true',
    #                        help='Publish state changes (for dynamic visualization)')
    arg_parser.add_argument('language', help='Target language')
    arg_parser.add_argument('dot_file', help='DOT file name. It must match certain form (see DOT_restrictions.txt)')
    args = arg_parser.parse_args()

    compile_fsm(args.dot_file, lang=args.language)
