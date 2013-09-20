import os
from . import dep_graph as dp


def run_test(id, path, repo_db):
    DiG = dp.Dependency_Graph(path)

    knots = DiG.get_independent_components()
    return reusability_index(DiG, knots)


def reusability_index(DiG, knots):
    return 1 - (len(knots) / len(DiG.G.nodes()))


if __name__ == '__main__':
    run_test(None, os.path.dirname(__file__), None)
