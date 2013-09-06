import os
import re
import networkx as nx


def run_test(id, path, db):
    build_graph(path)


def add_import_to_graph(line, G, origin, modules):
    line.strip()
    if line.startswith('import'):
        if ',' in line:
            for m in re.findall(r'(?:(?!import\b)(\b\w+\b),?)', line):
                add_edge(G, origin, m, modules)
        else:
            for tup in re.findall(r'(?:import (\b\w+\b);?)|(?:from (\b\w+\b) import \b\w+\b;?)', line):
                if tup[0]:
                    add_edge(G, origin, tup[0], modules)
                elif tup[1]:
                    add_edge(G, origin, tup[1], modules)


def add_edge(G, origin, dest, modules):
    if dest in modules:
        G.add_edge(origin, dest)


def build_graph(path):
    G = nx.DiGraph()
    modules = set()
    files = [(os.path.join(dirpath, f), f)
             for dirpath, dirnames, files in os.walk(path)
             for f in files if f.endswith('.py')]

    for _, f_name in files:
        f_name = f_name[:-3]
        modules.add(f_name)
        G.add_node(f_name)

    print modules

    for path, f_name in files:
        f_name = f_name[:-3]
        f = open(path)
        for line in f.readlines():
            add_import_to_graph(line, G, f_name, modules)
        f.close()
    print G.edges()
    return G


if __name__ == '__main__':
    build_graph(os.getcwd())
