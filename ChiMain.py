#!/usr/bin/env python
# Basic
import sys
import os
import shutil
import pdb
import yaml
import argparse
# Analysis
import re
from ChiParams import ChiParam, ChiSim
from ChiLib import *
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# from math import *

'''
Name: ChiMain.py
Description: Main control program for xi(chi)-launcher. Runs all newagebob code.
Input: To view type ChiMain.py -h
Output:
'''



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=10,
            help='Number of different parameter sets used.')
    parser.add_argument('-l','--log', default=False, action='store_true',
            help='Create a log file of all arguments specified.')
    parser.add_argument('files', nargs='*',
            help='Files that will be used to create the simulations.')
    parser.add_argument('-r','--replace', default=False, action='store_true',
            help='Replace simulation file instead of throwing and error if file already exists.')
    parser.add_argument('--fluid_config', default='',
            help='Will add fluid.config file to seed directories when creating directory structure. Used with bulk simulations when all fluids start with the same configuration.')

    opts = parser.parse_args()
    return opts


##Class definition
class ChiMain(object):
    def __init__(self, opts):
        self.cwd = os.getcwd()
        self.opts = opts
        self.yml_files_dict = {} # combined dictionary of all yaml files
        self.ChiParams = []
        self.ReadOpts()

    def ReadOpts(self):
        # Read all the file names given in options and combine into main yaml dict
        for f_name in self.opts.files:
            if os.path.isfile(f_name):
                with open(f_name) as f:
                    self.yml_files_dict[f_name] = yaml.load(f)

        a = list(find_str_values(self.yml_files_dict))

        self.MakeChiParams(a)

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
    x = ChiMain(opts)
    x.MakeDirectoryStruct()



