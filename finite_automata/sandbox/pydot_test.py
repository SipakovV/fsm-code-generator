import logging

import pydot


graphs = pydot.graph_from_dot_file("microwave1.dot")
graph = graphs[0]

node_list = graph.get_node_list()

for node in node_list:
    node_name = node.get_name()
    if node_name == 'START':
        continue

    print(node_name)

    node.set_fillcolor('yellow')
    node.set_style('filled')
    graph.write_png(node_name + '.png')
    node.set_style('')
