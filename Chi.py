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
from ChiParticleSwarm import ChiParticleSwarm
from ChiGeneticAlgorithm import ChiGeneticAlgorithm
from ChiRun import ChiRun
from ChiLib import *

'''
Name: Chi.py
Description: Main control program for xi(chi)-launcher. Runs all newagebob code.
Input: To view options type Chi.py -h
Output:
'''

def parse_args():
    # TODO Figure out how to make a choose functionality
    parser = argparse.ArgumentParser(prog='Chi.py')

    parser.add_argument('-n', type=int, default=10,
            help='Number of different parameter sets used.')
    parser.add_argument('-a', '--args_file', type=str,
            help='Name file that holds the program argument list. (Used with --create option and --launch option)')
    # TODO If multiple workdirs are specified then have Chi.py run multiple times with the same commmand but different options
    parser.add_argument('-d', '--workdir', type=str,
            help='Name of the working directory where simulation will be run. Used with --run option only)')
    parser.add_argument('-s', '--states', nargs='+', type=str,
            help='Name of all the states the simulation will run eg. start, build, analyze, etc.')

    # PREP options
    parser.add_argument('-P', '--prep', action='store_true',
            help='Prepares sims to run with either states specified with -s or all argument states in -a ARG_FILES')

    # REMOVE options
    parser.add_argument('-rm', '--remove', nargs='+', metavar='FILE', type=str,
            help='Removes FILEs from seed directories.')

    # LAUNCH options only
    parser.add_argument('-L', '--launch', nargs='*', default='NOLAUNCH', type=str, metavar='DIRS',
            help='Launches all the seed directories in DIRS list. If no list is\
                    given all sim directories in the "simulations" directory will be launched.')

    # CREATE options only
    parser.add_argument('-C', '--create', metavar='PARAM_FILE', 
            nargs='+', type=str,
            help='Creates seed directories with simulation structure that can be launched with ChiLaunch.py.')
    parser.add_argument('-r','--replace', default=False, action='store_true',
            help='Replace simulation file instead of throwing and error if file already exists.(Used with --create option only)')
    parser.add_argument('-ny', '--non_yaml', nargs='+', default=[], type=str,
            help='Will add non-yaml files to seed directories when creating directory structure. (Used with --create or --shotgun option only)')

    parser.add_argument('--fluid_config', default='',
            help='(DEPRICATED: use --non_yaml or -ny instead) Will add fluid.config file to seed directories when creating directory structure. Used with bulk simulations when all fluids start with the same configuration. (Used with --create or --shotgun option only)')

    parser.add_argument('-S', '--shotgun', metavar='PARAM_FILE', 
            nargs='+', type=str,
            help='Creates seed directories with simulation structure that can be launched with ChiLaunch.py. PARAM_FILEs are copied into seed directories with ChiParams chosen according to the random distribution specified. Need -n to specify the number of random variants (default=10).')

    parser.add_argument('-PSC', '--particleswarmcreate', metavar='PARAM_FILE', 
            nargs='+', type=str,
            help='Particle Swarm Optimization Creation. Creates seed directories with simulation structure that can be launched with ChiLaunch.py. PARAM_FILEs are copied into seed directories with ChiParams chosen according to the random distribution specified. Need -n to specify the number of random population members (default=10).')

    parser.add_argument('-GAC', '--geneticalgorithmcreate', metavar='PARAM_FILE', 
            nargs='+', type=str,
            help='Genetic Algorithm Optimization Creation. Creates seed directories with simulation structure that can be launched with ChiLaunch.py. PARAM_FILEs are copied into seed directories with ChiParams chosen according to the random distribution specified. Need -n to specify the number of random population members (default=10).')

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

    def ReadOpts(self):
        # TODO This might not be fully integrated just yet
        if not self.opts.workdir:
            self.opts.workdir = self.cwd

        if not self.opts.states and self.opts.args_file:
            yd = CreateDictFromYamlFile(self.opts.args_file)
            self.opts.states = list(yd.keys())

    def ProgOpts(self):
        wd = self.opts.workdir # Shortcut for work directory
        if self.opts.launch != "NOLAUNCH":
            # If no sim dirs are given find them all in simulations
            if self.opts.launch == []: 
                self.opts.launch = find_dirs(os.path.join(wd, "simulations"))
                # If no dirs were found return with warning
                if self.opts.launch == []:
                    print(" No sim directories were found our given. ")
                    return
            # Find run.not and delete
            try: os.remove(os.path.join(wd, "run.not"))
            except OSError: 
                print("run.not was not found in workdir. Might want to go searching for it.")
                pass
            # Create run.ing in workdir
            touch(os.path.join(wd, "run.ing"))
            ChiLaunch(simdirs=self.opts.launch, opts=self.opts)
            
        elif self.opts.create:
            touch(os.path.join(wd, "run.not"))
            c = ChiCreate(self.opts, self.opts.workdir)
            c.Create(self.opts.create)

        elif self.opts.shotgun:
            c = ChiCreate(self.opts, self.opts.workdir)
            c.Create(self.opts.shotgun)

        elif self.opts.particleswarmcreate:
            c = ChiParticleSwarm(self.opts, self.opts.workdir, 0)
            c.Create(self.opts.particleswarmcreate)

        elif self.opts.geneticalgorithmcreate:
            c = ChiGeneticAlgorithm(self.opts, self.opts.workdir, 0)
            c.Create(self.opts.geneticalgorithmcreate)

        elif self.opts.run:
            c = ChiRun(self.opts)
            c.Run(self.opts)

        elif self.opts.prep:
            seed_lst = find_seed_dirs(self.opts.workdir)
            for sd_dir in seed_lst:
                if self.opts.args_file: 
                    shutil.copy(self.opts.args_file, sd_dir)
                for s in self.opts.states:
                    touch(os.path.join(sd_dir, 'sim.{}'.format(s)))

        elif self.opts.remove:
            seed_lst = find_seed_dirs(self.opts.workdir)
            for sd_dir in seed_lst:
                for fn in self.opts.remove:
                    path = os.path.join(sd_dir, fn)
                    if os.path.exists(path): os.remove(path)

##########################################
if __name__ == "__main__":
    opts = parse_args()
    x = ChiMain(opts)
    # x.MakeDirectoryStruct()



