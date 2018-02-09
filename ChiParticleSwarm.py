#!/usr/bin/env python
## Basic
import sys
import os
import pdb
import shutil
import yaml
import argparse
import re
import pickle
## Analysis
from ChiCreate import ChiCreate
from ChiParams import ChiParam, ChiSim
from collections import OrderedDict
from ChiLib import *
import pandas as pd

from copy import deepcopy

'''
Name: ChiParticleSwarm.py
Description: Creates simulations for a particle swarm optimization run(s)
'''

class ChiParticleSwarm(ChiCreate):
    def __init__(self, opts, cwd, generation):
        self.generation = generation
        ChiCreate.__init__(self, opts=opts, cwd=cwd)

    ### Fun save/load hacks
    def savestate(self, sim_dir):
        filename = os.path.join(sim_dir, "sim_data_swarm_{}.pickle".format(self.generation))
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

    # Create has to have an additional step from ChiCreate
    def Create(self, file_list):
        # Make master yaml dictionary
        self.MakeYmlDict(file_list)

        # Get a list of all the ChiParam dictionsarys with key 
        # and value (ChiParam string) and put into a list
        a = list(find_str_values(self.yml_files_dict))

        # Turn list of dictionaries in to ChiParam objects
        self.MakeChiParams(a)
        self.CreateParticleSwarmData()
        self.MakeDirectoryStruct()

    # Directory creation, does work with updating generation
    def MakeDirectoryStruct(self):
        sim_dir_name = "generations/gen{0}".format(self.generation)
        sim_dir = os.path.join(self.opts.workdir, sim_dir_name)

        # Make run directory
        if self.opts.replace and os.path.exists(sim_dir_name):
            shutil.rmtree(sim_dir)
        if not os.path.exists(sim_dir_name):
            os.makedirs(sim_dir)

        # Always a shotgun type creation of directory struct
        l = []
        for i in range(self.opts.n):
            l += [ [i]*len(self.ChiParams) ]

        # Create a master list of the particular parameter points and the Sim name in an
        # index/database to lookup later!
        # Loop through the sim stuff, it should handle writing out the hash to the database file
        print " -- Making Particle Swarm Generation {} -- ".format(self.generation)
        for il in l:
            self.Sim.MakeSimDirectoryDatabase(sim_dir_name, self.generation, il)

        # Save myself off to the directory
        self.savestate("generations")

    ### Print functionality
    def PrintSwarm(self):
        print "Swarm Generation: {}".format(self.generation)
        print "   n particles: {}".format(self.Sim.nparticles)

    ### Particle Swarm specifics
    def CreateParticleSwarmData(self):
        self.Sim.CreateParticleSwarm()
        sim_dir_name = "generations/gen{0}".format(self.generation)
        sim_dir = os.path.join(self.opts.workdir, sim_dir_name)
        self.Sim.CreateParticleSwarmDatabase(sim_dir, self.generation)

    def GenerateFitnessInformation(self, dotest=False):
        # We have to look up the fitness information based on the driectory names and correlate this
        # with the proper sim, otherwise, is useless
        sim_dir_name = "generations/gen{0}".format(self.generation)
        sim_dir = os.path.join(self.opts.workdir, sim_dir_name)

        # Always a shotgun type creation of directory struct
        self.Sim.UpdateFitness(sim_dir, dotest)

    # Procreate Functionality
    def Procreate(self, dotest=False):
        # Load self
        generations = [dirname for dirname in os.listdir('generations') if dirname.startswith('gen')]
        generationints = [int(filter(str.isdigit, str1)) for str1 in generations]
        maxgen = max(generationints)

        # Save off the information about the opts, path, etc
        cur_cwd = self.cwd

        filename = os.path.join('generations', 'sim_data_swarm_{}.pickle'.format(maxgen))
        self.load(filename)

        # have to reset the generation and generationints
        generations = [dirname for dirname in os.listdir('generations') if dirname.startswith('gen')]
        generationints = [int(filter(str.isdigit, str1)) for str1 in generations]
        self.maxgen = max(generationints)
        self.nextgen = self.maxgen + 1
        self.cwd = cur_cwd

        self.PrintSwarm()
        print " -- Particle Swarm Procreating from max generation {}".format(self.maxgen)
        self.GenerateFitnessInformation(dotest)
        #self.Sim.UpdateFitness()
        print " -- Input Parameters -- "
        self.Sim.PrintSwarmCurrent()
        print " -- Best Parameters -- "
        self.Sim.UpdateBest()
        self.Sim.PrintSwarmBest()
        print " -- Updating Parameter Values -- "
        self.Sim.UpdatePositions()
        print " -- Output Parameters -- "
        self.Sim.PrintSwarmCurrent()

        # Write the new information
        self.generation = self.nextgen
        self.MakeDirectoryStruct()

    def Bias(self, opts):
        # Load self like in procreate
        generations = [dirname for dirname in os.listdir('generations') if dirname.startswith('gen')]
        generationints = [int(filter(str.isdigit, str1)) for str1 in generations]
        maxgen = max(generationints)

        filename = os.path.join('generations', 'sim_data_swarm_{}.pickle'.format(maxgen))
        self.load(filename)

        # have to reset the generation and generationints
        generations = [dirname for dirname in os.listdir('generations') if dirname.startswith('gen')]
        generationints = [int(filter(str.isdigit, str1)) for str1 in generations]
        self.maxgen = max(generationints)
        self.nextgen = self.maxgen + 1

        # Print ourselves
        self.PrintSwarm()
        # Bias the first entry to the updated value
        print " -- Particle Swarm Introducing Bias -- "
        print " -- Input Parameters -- "
        self.Sim.PrintSwarmCurrent()
        print " -- Bias Swarm {} -- ".format(opts.bias)
        # Read in the file specified into a dataframe or something
        df = pd.read_csv(opts.bias[0], delim_whitespace = True, header = None)
        self.Sim.BiasSwarm(df)
        print " -- Output Parameters -- "
        self.Sim.PrintSwarmCurrent()

        # Write the new information
        self.generation = self.nextgen
        self.MakeDirectoryStruct()


def parse_args():
    parser = argparse.ArgumentParser(prog='ChiParticleSwarm.py')

    parser.add_argument('-P', '--procreate', nargs='+', type=str, metavar='DIRS',
            help='Procreates based on most recent generation in DIRS list.')

    parser.add_argument('-B', '--bias', nargs='+', type=str, metavar='DIRS',
            help='Biases current generation by directly implementing the values found in the file passed')

    parser.add_argument('-T', '--test', action='store_true',
            help='Test the particle swarm optimization')

    opts = parser.parse_args()
    return opts

### Main function to test stuff?
if __name__ == "__main__":
    opts = parse_args()
    c = ChiParticleSwarm(opts, os.getcwd(), 0)
    if opts.procreate:
        c.Procreate(opts.test)
    elif opts.bias:
        c.Bias(opts)
