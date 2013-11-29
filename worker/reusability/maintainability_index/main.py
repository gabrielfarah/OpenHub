'''
Created on Sep 9, 2013

@author: gabo
'''
from radon.metrics import mi_visit, mi_parameters, mi_rank
from radon.raw import analyze
from radon.complexity import cc_visit
import os

#===============================================================================
# Maintainability Index is asoftware metric which measures how maintainable
# (easy to support and change) thesource code is. The maintainability index
# is calculated as a factored formula consisting of SLOC (Source Lines Of Code),
#  Cyclomatic Complexity and Halstead volume.
#===============================================================================
def get_maintenability_index(content):
    try:
        return  mi_visit(content,False)
    except:
        return 0

#===============================================================================
# Analyze the source code and return a namedtuple with the following fields:
#         loc: The number of lines of code (total)
#         lloc: The number of logical lines of code
#         sloc: The number of source lines of code (not necessarily corresponding to the LLOC)
#         comments: The number of Python comment lines
#         multi: The number of lines which represent multi-line strings
#         blank: The number of blank lines (or whitespace-only ones)
#===============================================================================
def get_code_metrics(content):
    try:
        var = analyze(content)
        return float(var[3]+var[4])/(var[1])
    except:
        return 0
#===============================================================================
# returns a list of blocks with respect to complexity. A block is a either Function object or a Class object.
#===============================================================================
def get_cyclomatic_complexity(content):
    try:
        return cc_visit(content)
    except:
        return 0 

def run_test(id, path, repo_db):
    num_files = 0
    avg_maintenability = 0
    avg_documentation = 0
    response = {}
    for root, subFolders, files in os.walk(path):
        for file in files:
            if (file.endswith('.py')):
                #print file
                with open(os.path.join(root, file), 'r') as content_file:
                    content = content_file.read()
                    avg_maintenability += get_maintenability_index(content)
                    try:
                        avg_documentation += get_code_metrics(content)
                    except:
                        pass
                    #print get_cyclomatic_complexity(content)
                    num_files += 1
                content_file.close()
    response["maintenability_index"] = (avg_maintenability/num_files)
    response["documentation_index"] = (avg_documentation/num_files)
    return response

if __name__ == '__main__':
    main(os.path.dirname(__file__))
