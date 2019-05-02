#!/usr/bin/env python
# In case of poor (Sh***y) commenting contact adam.lamson@colorado.edu
# Basic
import sys
import os
import pdb
import re
import numpy as np
import random
import hashlib
from shutil import copy as cp
from math import *
from subprocess import call
import yaml
from itertools import repeat
from collections import OrderedDict
from ChiLib import *
from copy import copy
from copy import deepcopy
import bisect
import pandas as pd


"""@package docstring
File:
Author: Adam Lamson
Email: adam.lamson@colorado.edu
Description:
"""


class ChiParam(object):
    def __init__(self, format_str="", exec_str="",
                 paramtype=float, values=[], level=0):
        self.format_str = format_str
        self.exec_str = exec_str
        self.paramtype = paramtype
        self.values = copy(values)
        self.level = level

        # Object reference class will be set here (see ChiLib)
        self.obj_r = None

        self.GetBounds()

    def SetObjRef(self, obj_r):
        self.obj_r = obj_r

    def GetValues(self):
        return self.values

    def GetNValues(self):
        return len(self.values)

    def GetBounds(self):
        # Parse the exec_str looking for bounds
        import re
        #print "exec_str: {}".format(self.exec_str)
        pattern = re.compile(r""".*
                              bounds=\[(?P<bound1>.*?),(?P<bound2>.*?)\]
                              .*""", re.VERBOSE)
        match = pattern.match(self.exec_str)
        if match:
            bound1 = float(match.group("bound1"))
            bound2 = float(match.group("bound2"))
            #print "[{}, {}]".format(bound1, bound2)
            self.bounds = [bound1, bound2]

    def UpdateValues(self):
        if self.values:
            self.values = list(map(self.paramtype, self.values))
        elif self.exec_str:
            self.values = list(map(self.paramtype, eval(self.exec_str)))
            # print self.values
        else:
            raise Exception(
                "ChiParam {} did not contain necessary inputs".format(
                    self.format_str))

    def AddValue(self):
        # Used mostly with Shotgun Param function
        self.values += [self.paramtype(eval(self.exec_str))]

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
        if isinstance(v, list):
            return self.format_str.format(len(v))
        else:
            return self.format_str.format(v)

    def GetParamType(self):
        return self.paramtype.__name__

    def UpdateParamValue(self, i):
        self.obj_r.Set(self.values[i])

    def __getitem__(self, index):
        return self.values[index]

    def __repr__(self, i=None):
        return self.format_str


##########################################
if __name__ == "__main__":
    print "Not implemented yet"
