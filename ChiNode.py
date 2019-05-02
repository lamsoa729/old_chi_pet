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
import yaml
# from math import *
# Speed
# from numba import jit
# Other importing


"""@package docstring
File:
Author: Adam Lamson
Email: adam.lamson@colorado.edu
Description:
"""


class ChiNode(object):
    def __init__(self, chiparams, yml_file_dict, level=0):
        self.chiparams = chiparams
        self.yml_file_dict = yml_file_dict

    # def UpdateParamValues(self):
    #     for cparam in self.chiparams:
    #         cparam.UpdateValues()

    # def UpdateShotgunParamValues(self, N):
    #     for cparam in self.chiparams:
    #         if cparam.values:
    #             continue
    #         else:
    #             for i in range(N):
    #                 cparam.AddValue()

    def MakeYamlFiles(self):
        pass

    def MakeSubnodes(self):
        pass

    def MakeNodeDirectory(self):
        pass

    def MakeDataDirectory(self, run_dir, gen, ind_lst=[]):
        pass

    def DumpData(self):
        pass


##########################################
if __name__ == "__main__":
    print "Not implemented yet"
