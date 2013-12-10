import os
import re
import networkx as nx
import itertools


class Dependency_Graph(object):

    def __init__(self, path):
        self.G = nx.DiGraph()
        modules = set()
        files = [(os.path.join(dirpath, f), f)
                 for dirpath, dirnames, files in os.walk(path)
                 for f in files if f.endswith('.py')]

        for _, f_name in files:
            f_name = f_name[:-3]
            modules.add(f_name)
            # G.add_node(f_name)
        # print modules

        for path, f_name in files:
            try:
                f_name = f_name[:-3]
                pyfile = open(path)
                for line in pyfile.readlines():
                    self.__add_import_to_graph(line, f_name, modules)
                pyfile.close()
            except:
                raise
            finally:
                pyfile.close()
        # print self.G.edges()

    def __add_import_to_graph(self, line, origin, modules):
        line.strip()
        if line.startswith('import') or line.startswith('from'):
            if ',' in line:
                for m in re.findall(r'(?:(?!import\b)(\b[A-Za-z0-9_.]+\b),?)', line):
                    if '.' in m:
                        self.__add_edge(origin, m.split('.')[-1], modules)
                    else:
                        self.__add_edge(origin, m, modules)
            else:
                for tup in re.findall(r'(?:import (\b[A-Za-z0-9_.]+\b);?)|(?:from (\b[A-Za-z0-9_.]+\b) import \b[A-Za-z0-9_.]+\b;?)', line):
                    if tup[0]:
                        if '.' in tup[0]:
                            self.__add_edge(origin, tup[0].split('.')[-1], modules)
                        else:
                            self.__add_edge(origin, tup[0], modules)
                    elif tup[1]:
                        if '.' in tup[1]:
                            self.__add_edge(origin, tup[1].split('.')[-1], modules)
                        else:
                            self.__add_edge(origin, tup[1], modules)

    def __add_edge(self, origin, dest, modules):
        if dest in modules:
            self.G.add_edge(origin, dest)


    def get_independent_components(self):
        components = set()

        for node in self.G.nodes_iter():
            components.add(frozenset(nx.dfs_tree(self.G, node)))

        return components

    def get_independent_components_exp(self):
        components = set()

        for node in self.G.nodes_iter():
            components.update(self.__find_comps_from(node))

        return components

    def __find_comps_from(self, root):
        queue = [Component(self.G, root)]
        components = set()

        while queue:
            comp = queue.pop()
            if comp.is_independent():
                components.add(frozenset(comp.nodes))

            for i in range(1, comp.in_degree+1):
                for comb in itertools.combinations(comp.get_predecessors(), i):
                    n_comp = Component(self.G)
                    for n in comp.nodes:
                        n_comp.add_node(n)
                    for n in comb:
                        n_comp.add_node(n)
                    queue.append(n_comp)

        return frozenset(components)

    def get_knots(self):
        s_vs = self.__reachable_sets()
        print "svs:", s_vs
        knots = []
        for n in s_vs:
            if self.__is_knot(s_vs[n], s_vs):
                knots.append(s_vs[n])
        return knots

    def __is_knot(self, nodes, s_vs):
        for node in nodes:
            if nodes != s_vs[node]:
                return False
        return True

    def __reachable_sets(self):
        s_vs = {}
        for n in self.G.nodes_iter():
            successors = nx.bfs_successors(self.G, n)
            s_vs[n] = {rchbl for src in successors for rchbl in successors[src]}
            s_vs[n].add(n)
        return s_vs


class Component:

    def __init__(self, DiG, node=None):
        self.nodes = set()
        self.G = DiG
        self.out_degree = 0
        self.in_degree = 0
        if node:
            self.add_node(node)

    def add_node(self, node):
        if not node in self.nodes:
            self.nodes.add(node)
            for out in self.G.successors(node):
                if not out in self.nodes:
                    self.out_degree += 1

            for inc in self.G.predecessors(node):
                if not inc in self.nodes:
                    self.in_degree += 1

    def is_independent(self):
        return self.out_degree == 0

    def get_predecessors(self):
        return [pred for node in self.nodes for pred in self.G.predecessors(node)]


if __name__ == '__main__':
    dp = DependencyGraph(os.getcwd())
