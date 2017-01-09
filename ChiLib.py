#!/usr/bin/env python
import sys
import os
import pdb
import re
import numpy as np 
import shutil
import yaml
from math import *

'''
Name: ChiLib.py
Description: Library of used functions for Chi-Launcher
'''

def CreateYamlFilesFromDict(seed_dir, yml_file_dict):
    for f, d in yml_file_dict.iteritems():
        path = os.path.join(seed_dir, f)
        with open(path, 'w') as of:
            yaml.dump(d, of, default_flow_style=False)

def CreateDictFromYamlFile(path): 
    with open(path, 'r') as f:
        ydict = yaml.open(f)
        return ydict

# Function that creates a list of list of all possible parameter indices
def ind_recurse(pi_list, p_index=0):
    l = [] # return list
    # Cycle through possible value indices for parameter with param index, p_index
    for i in range(pi_list[p_index]):
        if p_index == len(pi_list)-1:
            # If at the last index (end of recursion) start constructing index list
            l += [[i]]
        else:
            # Prepend i value to front of sublists using recursion
            lst = ind_recurse(pi_list, p_index+1)
            for x in lst:
                l += [[i]+ x]
    return l

# Recursive function to find SACParams in program
def find_str_values(obj, pattern='^ChiParam\(.*\)'):
    if isinstance(obj, list):
        for k, v in enumerate(obj):
            if re.match(pattern, str(v)):
                yield ObjRef(obj, k)
            elif isinstance(v, (dict,list)):
                for result in find_str_values(v, pattern):
                    yield result

    elif isinstance(obj, dict):
        for k, v in obj.iteritems():
            if re.match(pattern, str(v)):
                yield ObjRef(obj, k)
            elif isinstance(v, (dict,list)):
                for result in find_str_values(v, pattern):
                    yield result
    else:
        return


class ObjRef(object):
    def __init__(self, obj, key):
        self.obj = obj
        self.key = key

    def Set(self, value):
        self.obj[self.key] = value

    def GetValue(self):
        return self.obj[self.key]

    def __repr__(self):
        return self.obj[self.key]


##########################################
if __name__ == "__main__":
    print "Not implemented because this is strictly a library"




