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

    def Create(self, file_list):
        # Make master yaml dictionary
        self.MakeYmlDict(file_list)

        # Get a list of all the ChiParam dictionsarys with key 
        # and value (ChiParam string) and put into a list
        a = list(find_str_values(self.yml_files_dict))

        # Turn list of dictionaries in to ChiParam objects
        self.MakeChiParams(a)
        self.MakeDirectoryStruct()

    def MakeYmlDict(self, file_list):
        # Take input yaml files and create master dictionary from them
        for f_name in file_list:
            if os.path.isfile(f_name):
                self.yml_files_dict[f_name]=CreateDictFromYamlFile(f_name)

    def MakeChiParams(self, chilist):
        for x in chilist:
            # Self.ChiParams is a list of all ChiParam objects of the systme
            self.ChiParams += [eval(x.GetValue())]
            # Set reference in the master param file to change value later
            self.ChiParams[-1].SetObjRef(x)

        self.Sim = ChiSim(self.ChiParams, self.yml_files_dict, self.opts)

        # Make all parameter values for ChiParam objects
        if self.opts.create:
            self.Sim.UpdateParamValues()
        elif self.opts.shotgun:
            self.Sim.UpdateShotgunParamValues()
        elif self.opts.particleswarmcreate: # Duplicates the behavior of the shotgun approach
            self.Sim.UpdateShotgunParamValues()

        self.Sim.MakeSeeds()

    def MakeDirectoryStruct(self):
        sim_dir_name = "simulations"
        if self.opts.particleswarmcreate:
            sim_dir_name = "generations/gen0"
        sim_dir = os.path.join(self.opts.workdir, sim_dir_name)

        # Make run directory
        if self.opts.replace and os.path.exists(sim_dir_name):
            shutil.rmtree(sim_dir)
        #os.mkdir(sim_dir)
        os.makedirs(sim_dir)

        # Get all the permutations of values when running a slice
        if self.opts.create:
            # Get number of variations in each parameter set
            lst = [ x.GetNValues() for x in self.ChiParams ] 
            # Make a list of all the combinations of parameter indices
            l = ind_recurse(lst)

        # For shotgun runs no permutation is required
        elif self.opts.shotgun or self.opts.particleswarmcreate:
            l = []
            for i in range(self.opts.n):
                l += [ [i]*len(self.ChiParams) ]

        # Loop through indices and make the new sim directories 
        # and place seed directories in them
        print " -- Making simulations -- "
        for il in l:
            self.Sim.MakeSimDirectory(sim_dir_name, il)

    def TestPickleDump(self, sim_dir):
        # Test the dump functionality
        import pickle
        pkl_filename = os.path.join(sim_dir, 'sim_data.pickle')
        newsim = pickle.load(open(pkl_filename, 'rb'))
        print "newsim: {}".format(newsim)
        for chiparam in newsim.chiparams:
            print "newsim.chiparam: {}".format(chiparam)
            print "values: {}".format(chiparam.values)
            print "bounds: {}".format(chiparam.bounds)

##########################################
if __name__ == "__main__":
    opts = parse_args()
    x = ChiCreate(opts)




