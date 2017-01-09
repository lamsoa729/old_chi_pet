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
from ChiRun import ChiRun
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
    parser.add_argument('-a', '--args_file', type=str,
            help='Name file that holds the program argument list. (Used with --create option and --launch option)')
    parser.add_argument('-d', '--workdir', type=str,
            help='Name of the working directory where simulation will be run. Used with --run option only)')
    parser.add_argument('-s', '--states', nargs='+', type=str,
            help='Name of all the states the simulation will run eg. start, build, analyze, etc.')
    # parser.add_argument('-p', '--prep', metavar='PREP_FILES', nargs='+',
    #         # TODO Need to create custom action here I think
    #         const=['sim.start', 'sim.analyze'], type=str, default=[],
    #         help='Prepares sims to run with PREP_FILES. Can be used with builder or on its own. If used on its own you must be in the "simulations" directory.')

    # LAUNCH options only
    parser.add_argument('-L', '--launch', nargs='+', type=str, metavar='DIRS',
            help='Launches all the seed directories in DIRS list.')

    # CREATE options only
    parser.add_argument('-C', '--create', metavar='PARAM_FILE', 
            nargs='+', type=str,
            help='Creates seed directories with simulation structure that can be launched with ChiLaunch.py.')
    parser.add_argument('-r','--replace', default=False, action='store_true',
            help='Replace simulation file instead of throwing and error if file already exists.(Used with --create option only)')
    parser.add_argument('--fluid_config', default='',
            help='Will add fluid.config file to seed directories when creating directory structure. Used with bulk simulations when all fluids start with the same configuration. (Used with --create option only)')

    # RUN options only
    parser.add_argument('-R', '--run', action="store_true",
            help='Runs a singular seed directory. Need --args_file.')

    opts = parser.parse_args()
    return opts


##Class definition
class ChiMain(object):
    def __init__(self, opts):

        self.opts = opts
        self.yml_files_dict = {} # combined dictionary of all yaml files
        self.cwd = os.getcwd()
        self.ChiParams = []
        self.ReadOpts()
        self.ProgOpts()

    def ReadOpts()
        # TODO This might not be fully integrated just yet
        if not self.opts.workdir:
            self.opts.workdir = self.cwd

        if not self.opts.states and self.opts.args_file:
            yd = CreateDictFromYamlFile(self.opts.args_file)
            self.opts.states = yd.keys()

    def ProgOpts(self):
        # Read all the file names given in options and combine into main yaml dict
        if self.opts.launch:
            ChiLaunch(simdirs=self.opts.launch, opts=self.opts)
            
        elif self.opts.create:
            c = ChiCreate(self.opts, self.cwd)
            c.Create()

        elif self.opts.run:
            c = ChiRun(self.opts)
            c.Run(self.opts)


##########################################
if __name__ == "__main__":
    opts = parse_args()
    x = ChiMain(opts)
    # x.MakeDirectoryStruct()



