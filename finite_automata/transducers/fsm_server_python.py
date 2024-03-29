import argparse

from python_server import fsm_server


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='FSM server')
    arg_parser.add_argument('--visual', default=False, action='store_true', help='Publish state changes (for dynamic visualization)')
    # TODO: Make cache cleaning parameter
    arg_parser.add_argument('fsm_code_file', help='Python source file generated by the translator')
    args = arg_parser.parse_args()
    fsm_server.run(args.fsm_code_file, args.visual)
