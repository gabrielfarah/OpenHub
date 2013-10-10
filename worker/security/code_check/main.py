import sys
import os
from pylint.lint import Run
from cStringIO import StringIO


def run_test(id, path, repo_db):
    """
    Counts number of pylint messages found of each type according to pylint docs:
    [R]efactor for a "good practice" metric violation
    [C]onvention for coding standard violation
    [W]arning for stylistic problems, or minor programming issues
    [E]rror for important programming issues (i.e. most probably bug)
    [F]atal for errors which prevented further processing
    """

    # Init counts
    results = {'R': 0, 'C': 0, 'W': 0, 'E': 0, 'F': 0}

    # Setup the environment
    backup = sys.stdout

    try:
        print "Inputting .py files to linter"
        for dirpath, dirnames, files in os.walk(path):
            for f in files:
                if f.endswith('.py'):
                    fpath = os.path.join(dirpath, f)

                    sys.stdout = StringIO()
                    Run(['--reports=n', fpath], exit=False)
                    out = sys.stdout.getvalue() # release output
                    sys.stdout.close()  # close the stream

                    for l in out.split('\n')[1:]:
                        if l.startswith('R'):
                            results['R'] += 1
                        if l.startswith('C'):
                            results['C'] += 1
                        if l.startswith('W'):
                            results['W'] += 1
                        if l.startswith('E'):
                            results['E'] += 1
                        if l.startswith('F'):
                            results['F'] += 1

        sys.stdout = backup # restore original stdout
        print "Done linting files for", repo_db['full_name']
        # print results
        return results
    except Exception as e:
        raise e
    finally:
        sys.stdout = backup # restore original stdout


if __name__ == '__main__':
    run_test(None, '.', {'full_name': 'test'})
