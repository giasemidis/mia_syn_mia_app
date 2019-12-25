import numpy as np
from . deco_path_valid import valid_file


@valid_file
def read_results(file):
    '''
    Reads results from txt file
    '''
    with open(file, 'r', newline='') as f:
        line = f.readline()
        results = np.array([int(s) for s in line if s.isdigit()])

    return results
