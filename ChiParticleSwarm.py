#!/usr/bin/env python
## Basic
import sys
import os
import pickle
## Analysis
from ChiParams import ChiParam, ChiSim
from ChiLib import *

# Particle swarm generation class
class ChiParticleSwarmGeneration(object):
    def __init__(self, chisim, gen):
        self.chisim = chisim
        self.generation = gen

    # Fun hacks to load/save self to pickle
    def savestate(self, sim_dir):
        filename = os.path.join(sim_dir, 'sim_data_swarm.pickle')
        self.save(filename)

    def save(self, filename):
        f = open(filename, 'wb')
        pickle.dump(self.__dict__,f)
        f.close()

    def load(self, filename):
        f = open(filename, 'rb')
        tmp_dict = pickle.load(f)
        f.close()

        self.__dict__.update(tmp_dict)

if __name__ == "__main__":
    filename = sys.argv[1]
    c = ChiParticleSwarmGeneration(None, 0)
    c.load(filename)
    print "c.sim: {}".format(c.chisim)
    for chiparam in c.chisim.chiparams:
        print "newsim.chiparam: {}".format(chiparam)
        print "values: {}".format(chiparam.values)
        print "bounds: {}".format(chiparam.bounds)
