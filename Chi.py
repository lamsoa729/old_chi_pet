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
from ChiLaunch import ChiLaunch
from ChiCreate import ChiCreate
from ChiLib import *

'''
Name: Chi.py
Description: Main control program for xi(chi)-launcher. Runs all newagebob code.
Input: To view type Chi.py -h
Output:
'''



def parse_args():
    # TODO Figure out how to make a choose functionality
    parser = argparse.ArgumentParser(prog='Chi.py')
    parser.add_argument('-n', type=int, default=10,
            help='Number of different parameter sets used.')
    parser.add_argument('-l','--log', default=False, action='store_true',
            help='Create a log file of all arguments specified.')
    # parser.add_argument('files', nargs='*',
            # help='Files that will be used to create the simulations.')
    parser.add_argument('-r','--replace', default=False, action='store_true',
            help='Replace simulation file instead of throwing and error if file already exists.')
    parser.add_argument('--fluid_config', default='',
            help='Will add fluid.config file to seed directories when creating directory structure. Used with bulk simulations when all fluids start with the same configuration.')
    parser.add_argument('-L', '--launch', nargs='+', type=str, metavar='DIRS',
            help='Launches all the seed directories in DIRS list.')
    parser.add_argument('--prog_options', metavar='PROG_OPT_FILE',
            help='If launching a program, PROG_OPT_FILE is a yaml file with all the program inputs in a simple list. (See ChiLaunch.py)')
    parser.add_argument('-C', '--create', metavar='PARAM_FILE', 
            nargs='+', type=str,
            help='Creates seed directories with simulation structure that can be launched with ChiLaunch.py.')

    # parser.add_argument('-p', '--prep', metavar='PREP_FILES', nargs='+',
    #         # TODO Need to create custom action here I think
    #         const=['sim.start', 'sim.analyze'], type=str, default=[],
    #         help='Prepares sims to run with PREP_FILES. Can be used with builder or on its own. If used on its own you must be in the "simulations" directory.')

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
        if self.opts.launch:
            ChiLaunch(simdirs=self.opts.launch, opts=self.opts)
            
        elif self.opts.create:
            c = ChiCreate(self.opts, self.cwd)
            c.Create()

##########################################
if __name__ == "__main__":
    opts = parse_args()
    x = ChiMain(opts)
    # x.MakeDirectoryStruct()



