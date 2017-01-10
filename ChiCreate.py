#!/usr/bin/env python
## Basic
import sys
import os
import pdb
import shutil
import yaml
import argparse
import re
## Analysis
from ChiParams import ChiParam, ChiSim
from collections import OrderedDict
from ChiLib import *

'''
Name: ChiCreate.py
Description: Creates simulation structure to run simulations with ChiLaunch
Input:
Output:
'''

##Class definition
class ChiCreate(object):
    def __init__(self, opts, cwd):
        # Owned parameters
        self.cwd = cwd
        self.opts = opts
        self.yml_files_dict = OrderedDict() # combined dictionary of all yaml files
        self.ChiParams = []
        self.Sim = None

    def Create(self):
        self.MakeYmlDict()

        a = list(find_str_values(self.yml_files_dict))
        self.MakeChiParams(a)
        self.MakeDirectoryStruct()

    def MakeYmlDict(self):
        # Take input yaml files and create master dictionary from them
        for f_name in self.opts.create:
            if os.path.isfile(f_name):
                self.yml_files_dict[f_name]=CreateDictFromYamlFile(f_name)
                # with open(f_name) as f:
                    # self.yml_files_dict[f_name] = yaml.load(f)
        # print self.yml_files_dict

    def MakeChiParams(self, xilist):
        for x in xilist:
            self.ChiParams += [eval(x.GetValue())]
            self.ChiParams[-1].SetObjRef(x)
        self.Sim = ChiSim(self.ChiParams, self.yml_files_dict, self.opts)
        self.Sim.MakeSeeds()

    def MakeDirectoryStruct(self):
        sim_dir_name = "simulations"
        sim_dir = os.path.join(self.cwd, sim_dir_name)

        # Make container directory
        if self.opts.replace and os.path.exists(sim_dir_name):
            shutil.rmtree(sim_dir)

        os.mkdir(sim_dir)
        # Get number of variations in each parameter set
        lst = [ x.GetNValues() for x in self.ChiParams ] 

        # Make a list of all the combinations of parameter indices
        l = ind_recurse(lst)
        # Loop through indices and make the new sim directories and place seeds in them
        print " -- Making simulations -- "
        for il in l:
            self.Sim.MakeSimDirectory(sim_dir_name, il)

##########################################
if __name__ == "__main__":
    opts = parse_args()
    x = ChiCreate(opts)




