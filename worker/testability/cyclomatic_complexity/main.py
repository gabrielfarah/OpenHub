'''
Created on Sep 18, 2013

@author: gabo
'''
from radon.complexity import cc_visit, average_complexity
import os
def test_sfsd():
    print 'a'
#===============================================================================
# returns a list of blocks with respect to complexity. A block is a either Function object or a Class object. 
#===============================================================================
def get_cyclomatic_complexity(content):
    return cc_visit(content)

def main(rootdir):
    num_files = 0
    non_mantenible_files = 0
    total_cyclomatic_complexity = 0
    num_tests = 0
    response = {}
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            if (file.endswith('.py')):
                #print file
                with open(os.path.join(root, file), 'r') as content_file:
                    content = content_file.read()
                    cc = get_cyclomatic_complexity(content)
                    avg = average_complexity(cc)
                    if avg > 0:
                        total_cyclomatic_complexity += avg
                        num_files += 1
                        if avg > 7:
                            non_mantenible_files += 1
                content_file.close()
                with open(os.path.join(root, file), 'r') as content_file:
                    lines = [line.strip() for line in content_file]
                    for lines2 in lines:
                        if lines2.find("def ") != -1:
                            if lines2.find("test") != -1:
                                num_tests += 1
                content_file.close()
    response["avg_cc"] = total_cyclomatic_complexity/num_files
    response["non_mantenible_files"] = non_mantenible_files 
    response["test_coverage"] = num_tests - total_cyclomatic_complexity
    return response

if __name__ == '__main__':
    main(os.path.dirname(__file__))