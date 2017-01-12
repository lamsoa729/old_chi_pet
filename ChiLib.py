#!/usr/bin/env python
import sys
import os
import pdb
import re
import numpy as np 
import shutil
import yaml
from collections import OrderedDict
from math import *

'''
Name: ChiLib.py
Description: Library of used functions for Chi-Launcher
'''

def CreateYamlFilesFromDict(seed_dir, yml_file_dict):
    for f, d in yml_file_dict.iteritems():
        # print "File= {}, Dictionary= {}".format(f, d)
        path = os.path.join(seed_dir, f)
        with open(path, 'w') as of:
            OrderedYamlDump(d, of, default_flow_style=False)
            # yaml.dump(d, of, default_flow_style=False)

def CreateDictFromYamlFile(path): 
    with open(path, 'r') as f:
        # ydict = yaml.open(f)
        ydict = OrderedYamlLoad(f)
        return ydict

# Taken from http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts/21048064#21048064
# Usage: yaml_dict = OrderedYamlLoad(istream)
def OrderedYamlLoad(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

# Usage: OrderedYamlDump(yaml_dictionary, ostream)
def OrderedYamlDump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

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

def find_seed_dirs(path):
    is_seed = re.compile('s\d+$')
    for current, dirnames, filenames in os.walk(path):
        if is_seed.search(current):
            yield  os.path.abspath(current)

def touch(filename):
    with open(filename, 'a') as f:
        f.close()

# map(touch, find_xml_tests('path/to/files'))

##########################################
if __name__ == "__main__":
    print "Not implemented because this is strictly a library"




