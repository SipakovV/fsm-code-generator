import argparse
import os

import graphviz
import pydot

from fsm_core.dot_parser import FSMDOT
from fsm_core.transducer_fsm import TransducerFSM


def visualize_base(filename: str, png_directory: str):
    if not filename.endswith('.dot'):
        raise ValueError('Invalid DOT file')

    fsm_name = os.path.basename(filename[:-4])

    print(fsm_name)

    try:
        os.mkdir(png_directory)
    except FileExistsError as exc:
        pass

    path = os.path.join(png_directory, fsm_name)
    # print(path)
    try:
        os.mkdir(path)
    except FileExistsError as exc:
        pass

    s = graphviz.Source.from_file(filename)
    s.render('_base', format='png', directory=path)
    #print('_base rendered')
    # fsm.visualize(all_states=True)


def visualize_all_states(filename: str, png_directory: str):
    if not filename.endswith('.dot'):
        raise ValueError('Invalid DOT file')

    fsm_name = os.path.basename(filename[:-4])

    try:
        os.mkdir(png_directory)
    except FileExistsError as exc:
        pass

    path = os.path.join(png_directory, fsm_name)
    # print(path)
    try:
        os.mkdir(path)
    except FileExistsError as exc:
        pass

    graphs = pydot.graph_from_dot_file(filename)
    graph = graphs[0]

    node_list = graph.get_node_list()

    for node in node_list:
        node_name = node.get_name()
        if node_name == 'START':
            continue

        node.set_fillcolor('yellow')
        node.set_style('filled')
        graph.write_png(os.path.join(path, node_name) + '.png')
        node.set_style('')

        #print(f'State {node_name} rendered')


def compile_fsm(filename, lang: str, visualize='full', png_directory='generated_graph_images'):

    # TODO: get fsm name from filename instead of graph name

    if visualize == 'full' or visualize == 'base':
        visualize_base(filename, png_directory)
        print('Graph base visualized')

    parser = FSMDOT()
    res = parser.parse_file(filename)

    print('DOT parsed')

    fsm = TransducerFSM(**res.node)

    print('FSM created')

    fsm.generate_code_python()
    
    print('Code generated')

    if visualize == 'full':
        visualize_all_states(filename, png_directory)
        print('All states highlight visualized')


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
