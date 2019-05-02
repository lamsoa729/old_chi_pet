#!/usr/bin/env python
# In case of poor (Sh***y) commenting contact adam.lamson@colorado.edu
# Basic
import sys
import os
# Testing
# import pdb
# import time, timeit
# import line_profiler
# Analysis
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# import pandas as pd
# import yaml
# from math import *
# Speed
# from numba import jit
# Other importing
# sys.path.append(os.path.join(os.path.dirname(__file__), '[PATH]'))


"""@package docstring
File:
Author: Adam Lamson
Email: adam.lamson@colorado.edu
Description:
"""


class ChiSeed(ChiParam):
    def __init__(self, bounds=[]):
        ChiParam.__init__(self, values=list(
            range(bounds[0], bounds[-1])), paramtype=int)

    def CreateSeedList(self):
        self.sd_names = ['s{}'.format(i) for i in self.values]

    def MakeSeedDirectories(self, sim_dir, yml_file_dict, opts):
        for sn, s in zip(self.sd_names, self.values):
            sd_dir = os.path.join(sim_dir, sn)
            os.mkdir(sd_dir)
            self.obj_r.Set(s)
            CreateYamlFilesFromDict(sd_dir, yml_file_dict)
            if opts.fluid_config:  # TODO depricate this for one below
                cp(opts.fluid_config, sd_dir)
            for f in opts.non_yaml:
                cp(f, sd_dir)
            if opts.states:
                for s in opts.states:
                    open(os.path.join(sd_dir, 'sim.{}'.format(s)), 'a')


##########################################
if __name__ == "__main__":
    print "Not implemented yet"
