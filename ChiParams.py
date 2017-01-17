#!/usr/bin/env python
# Basic
import sys
import os
import pdb
import re
import numpy as np 
import random
from shutil import copy as cp
from math import *
import yaml
from collections import OrderedDict
from ChiLib import *
from copy import copy

'''
Name:ChiParams.py
Description: Class used to hold parameter values for ChiLauncher module
'''


# Creates a linear spacing of n_vars between bounds[0] and bounds[-1]
def LinearSlice(bounds, n_vars=10):
    return np.linspace(bounds[0], bounds[-1], n_vars)

# Creates a log spacing of n_vars between bounds[0] and bounds[-1]
def LogSlice(n_vars, bounds, base=2):
    ex_start = log(bounds[0], base)
    ex_end = log(bounds[-1], base)
    # print np.logspace(ex_start, ex_end, n_copies, base=base, endpoint=True)[index]
    return np.logspace(ex_start, ex_end, n_vars, base=base, endpoint=True)

def UniformRandom(bounds):
    return random.uniform(bounds[0], bounds[-1])

# Class that holds all the values for a single parameter in a run
class ChiParam(object):
    def __init__(self, format_str="", exec_str="", paramtype=float, values=[]):
        self.format_str = format_str
        self.exec_str = exec_str
        self.paramtype = paramtype
        self.values = copy(values)
        # self.UpdateValues()

        self.obj_r = None # Object reference class will be set here (see ChiLib)

    def SetObjRef(self, obj_r):
        self.obj_r = obj_r

    def GetValues(self):
        return self.values

    def GetNValues(self):
        return len(self.values)

    def UpdateValues(self):
        if self.values:
            self.values = map(self.paramtype, self.values)
        elif self.exec_str:
            self.values = map(self.paramtype, eval(self.exec_str))
        else:
            raise StandardError("ChiParam {} did not contain necessary inputs".format(self.format_str))

    def AddValue(self):
        # Used mostly with Shotgun Param function
        self.values += [ self.paramtype(eval(self.exec_str)) ]

    def DirRepresentation(self, index):
        if not self.format_str:
            return ""
        else:
            if "{0:d}" in self.format_str:
                self.paramtype = int
                self.UpdateValues()
                # self.SetValue(self.value)
            return self.format_str.format(self.values[index])

    def format(self, v):
        return self.format_str.format(v)

    def GetParamType(self):
        return self.paramtype.__name__

    def UpdateParamValue(self, i):
        self.obj_r.Set(self.values[i])

    def __getitem__(self, index):
        return self.values[index]

    def __repr__(self, i=None):
        return self.format_str

class ChiSim(object):
    def __init__(self, chiparams, yml_file_dict, opts):
        self.chiparams = chiparams
        self.yml_file_dict = yml_file_dict
        self.opts = opts

    def UpdateParamValues(self):
        for cparam in self.chiparams:
            cparam.UpdateValues()

    def UpdateShotgunParamValues(self, nvars):
        for i in range(nvars):
            for cparam in self.chiparams:
                cparam.AddValue()

    def MakeSeeds(self):
        sd_obj = find_str_values(self.yml_file_dict, 
                        pattern='^ChiSeed\(.*\)').next()
        self.seeds = eval(sd_obj.GetValue())
        self.seeds.SetObjRef(sd_obj)
        self.seeds.CreateSeedList()

    def MakeSimDirectory(self, run_dir, ind_lst=[]):
        sim_name = ""
        for i,p in zip(ind_lst, self.chiparams):
            # dir_name += "{}_".format(p.format(p[i]))
            p.UpdateParamValue(i)
            sim_name += p.format(p[i]) + "_"

        sim_dir = os.path.join(run_dir, sim_name[:-1])
        os.mkdir(sim_dir)
        print "   {}".format(sim_dir)
        self.seeds.MakeSeedDirectories(sim_dir, self.yml_file_dict, self.opts)

# Class to fill Sim directories with seed directories
class ChiSeed(ChiParam):
    def __init__(self, bounds=[]):
        ChiParam.__init__(self, values=list(range(bounds[0],bounds[-1])), paramtype=int)

    def CreateSeedList(self): 
        self.sd_names = ['s{}'.format(i) for i in self.values]

    def MakeSeedDirectories(self, sim_dir, yml_file_dict, opts):
        for sn, s in zip(self.sd_names, self.values):
            sd_dir = os.path.join(sim_dir, sn)
            os.mkdir(sd_dir)
            self.obj_r.Set(s)
            CreateYamlFilesFromDict(sd_dir, yml_file_dict)
            if opts.fluid_config:
                cp(opts.fluid_config, sd_dir)
            if opts.states:
                for s in opts.states:
                    open(os.path.join(sd_dir, 'sim.{}'.format(s)), 'a')
                

##########################################
if __name__ == "__main__":
    print "Not implemented. This is strictly a library."




