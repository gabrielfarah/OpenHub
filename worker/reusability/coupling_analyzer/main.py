import os
from . import dep_graph as dp


def run_test(id, path, repo_db):
    print "Building dependency graph..."
    DiG = dp.Dependency_Graph(path)
    print "Done building dependency graph"

    print "Calculating independent components..."
    knots = DiG.get_independent_components()
    print "Done"
    return reusability_index(DiG, knots)


def reusability_index(DiG, knots):
    return 1 - (float(len(knots)) / len(DiG.G.nodes())) if len(DiG.G.nodes()) > 0 else 0


if __name__ == '__main__':
    run_test(None, os.path.dirname(__file__)+'/../../zFileTemp/django-mptt', None)
