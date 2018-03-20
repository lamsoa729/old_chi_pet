#!/usr/bin/env python
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

'''
Name:ChiParams.py
Description: Class used to hold parameter values for ChiLauncher module
'''


# Creates a linear spacing of n_vars between bounds[0] and bounds[-1]
def LinearSlice(bounds, n_vars=10):
    return np.linspace(bounds[0], bounds[-1], n_vars)

# Creates a log spacing of n_vars between bounds[0] and bounds[-1]
def LogSlice(bounds, n_vars=10, base=2):
    ex_start = log(bounds[0], base)
    ex_end = log(bounds[-1], base)
    # print np.logspace(ex_start, ex_end, n_copies, base=base, endpoint=True)[index]
    return np.logspace(ex_start, ex_end, n_vars, base=base, endpoint=True)

def Replicate(item_str, bounds=[], n_vars=None):
    param_val_list = []
    step = 1
    if n_vars:
        step = (int(bounds[-1]) - int(bounds[0]))/n_vars
    for i in range(int(bounds[0]),int(bounds[-1]+1), step):
        param_val_list +=[ [ eval(item_str) for _ in range(i) ] ]
        # l = [ eval(item_str) for _ in range(i) ] 
        # param_val_list +=  [l]

    # print param_val_list
    return param_val_list

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
            self.values = map(self.paramtype, self.values)
        elif self.exec_str:
            self.values = map(self.paramtype, eval(self.exec_str))
            # print self.values
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
        if type(v) is list:
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

class ChiSim(object):
    def __init__(self, chiparams, yml_file_dict, opts):
        self.chiparams = chiparams
        self.yml_file_dict = yml_file_dict
        self.opts = opts

    def UpdateParamValues(self):
        for cparam in self.chiparams:
            cparam.UpdateValues()

    def UpdateShotgunParamValues(self):
        for cparam in self.chiparams:
            if cparam.values:
                #TODO If two param value lists are different, 
                #     choose the smaller one.
                if self.opts.n != cparam.GetNValues():
                    print "## Number of values of in {0}({1}) \
                    does not match nvars given({2}). Setting nvars to {1}.".format(
                            cparam.format_str.format(0), cparam.GetNValues(),
                            self.opts.n)
                    self.opts.n = cparam.GetNValues()
                continue
            else:
                for i in range(self.opts.n):
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
            # print p[i]
            sim_name += p.format(p[i]) + "_"

        sim_dir = os.path.join(run_dir, sim_name[:-1])
        os.mkdir(sim_dir)
        print "   {}".format(sim_dir)
        self.seeds.MakeSeedDirectories(sim_dir, self.yml_file_dict, self.opts)

    def MakeSimDirectoryDatabase(self, run_dir, gen, ind_lst=[]):
        # Update the parameter values the same as the last type of sim directory sturcture
        sim_values = ""
        sim_name = ""
        for i,p in zip(ind_lst, self.chiparams):
            p.UpdateParamValue(i)
            sim_values += str(p[i]) + " "
            sim_name += p.format(p[i]) + "_"

        #sim_name = sim_name[:-1] + str(random.uniform(0.0, 1.0))
        sim_name = sim_name[:-1]
        sim_values = sim_values[:-1]
        #print "sim_values: {}".format(sim_values)
        #print "sim_name: {}".format(sim_name)
        hash_object = hashlib.md5(sim_name.encode())
        #print "hash: {}".format(hash_object.hexdigest())

        with open(os.path.join(run_dir, "gen{}_database.txt".format(gen)), "a") as stream:
            stream.write(sim_values)
            stream.write(" ")
            stream.write(hash_object.hexdigest())
            stream.write("\n")

        # Create the hashed sim directory
        sim_dir = os.path.join(run_dir, hash_object.hexdigest())
        os.mkdir(sim_dir)
        print "   {} (from {})".format(sim_dir, sim_name)
        self.seeds.MakeSeedDirectories(sim_dir, self.yml_file_dict, self.opts)
        
    def DumpPickle(self, sim_dir):
        pkl_filename = os.path.join(sim_dir, 'sim_data.pickle')
        with open(pkl_filename, 'w') as pkl_file:
            import pickle
            pickle.dump(self, pkl_file)

    ### Just some utility stuff
    def FakeGaussianSignal(self, x, mu, sigma):
        #return (1.0 / sigma / np.sqrt(2*np.pi)) * np.exp(-np.power(x - mu, 2.) / (2 * np.power(sigma, 2.)))
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sigma, 2.)))

    ### ParticleSwarm specific information
    def CreateParticleSwarm(self):
        self.nparticles = self.opts.n
        self.pbest = [np.float(-100.0) for i in xrange(self.nparticles)]
        self.pbestid = [np.int(i) for i in xrange(self.nparticles)]
        self.pbestx = [deepcopy(self.chiparams) for i in xrange(self.nparticles)]
        self.pbest_better = [' ' for i in xrange(self.nparticles)]
        self.gbest = np.float(-100.0)
        self.gbestid = np.int(0)
        self.gbestx = None
        self.gbest_better = ' '
        self.fitness = [np.float(-100.0) for i in xrange(self.nparticles)]
        self.velocity = np.zeros((self.nparticles, len(self.chiparams)))
        # For each chiparam, create a velocity based on the vmax for each particle and each chiparam
        for ichi in xrange(len(self.chiparams)):
            vmax = self.chiparams[ichi].bounds[1] - self.chiparams[ichi].bounds[0]
            #print "chiparam{} vmax {}".format(ichi, vmax)
            for idx in xrange(self.nparticles):
                self.velocity[idx][ichi] = random.uniform(-vmax, vmax)
        #print "velocity: {}".format(self.velocity)

    # Create the genetic algorithm for everything
    def CreateGeneticAlgorithm(self):
        self.nparticles = self.opts.n
        # Maintain the top 5 elite genetic sequences
        self.nelite = 5
        self.pelite = [np.float(-100) for i in xrange(self.nelite)]
        self.peliteid = [np.int(i) for i in xrange(self.nelite)]
        self.pelitex = [deepcopy(self.chiparams) for i in xrange(self.nelite)]
        self.plastx = [deepcopy(self.chiparams) for i in xrange(self.nparticles)]
        self.pelite_better = [' ' for i in xrange(self.nelite)]
        # Maintain the current fitness of the different phenotypes 
        self.fitness = [np.float(-100) for i in xrange(self.nparticles)]
        self.parents = [[-1,-1] for i in xrange(self.nparticles)]

    def CreateParticleSwarmDatabase(self, sim_dir, gen):
        # Create a database of the parameters, write them out to start with
        os.makedirs(sim_dir)

        # Space separated parameter values
        param_str = ""
        for ichi in xrange(len(self.chiparams)):
            param_str += "{} ".format(self.chiparams[ichi])
        param_str += "hash"
        with open(os.path.join(sim_dir, "gen{}_database.txt".format(gen)), "w") as stream:
            stream.write("{}\n".format(param_str))

    # Update the fitness of myself for all the subsims
    def UpdateFitness(self, sim_dir, dotest=False):
        print " -- Simulations Checking and Updating Fitness -- "
        if dotest:
            print " WARNING ERROR Using fake fitness function!!!!!"
            for idx in xrange(self.nparticles):
                x = self.chiparams[0].values[idx]
                sx = self.chiparams[1].values[idx]
                y = self.chiparams[2].values[idx]
                sy = self.chiparams[3].values[idx]
                z = self.chiparams[4].values[idx]
                sz = self.chiparams[5].values[idx]
                #print "(x,y,z) = ({}, {}, {})".format(x, y, z)
                self.fitness[idx] = self.FakeGaussianSignal(x, 184, 20) * self.FakeGaussianSignal(y, 80, 80) * self.FakeGaussianSignal(z, 110, 40) + self.FakeGaussianSignal(sx, 0.0, 0.1) + self.FakeGaussianSignal(sy, 0.0, 0.1) + self.FakeGaussianSignal(sz, 0.0, 0.1)
            return

        # Look for the fitness file in the data directory for each particle
        for idx in xrange(self.nparticles):
            print "Sim {} looking for fitness.yaml".format(idx)
            # Rebuild the name of the sim
            sim_name = ''
            for ichi in xrange(len(self.chiparams)):
                p = self.chiparams[ichi]
                sim_name += p.format(p[idx]) + "_"

            sim_name = sim_name[:-1]
            hash_object = hashlib.md5(sim_name.encode())
            sim_full_path = os.path.join(sim_dir, hash_object.hexdigest())

            # Generate the sim fitness data!
            status = call(['SpindleAnalysis', '--sim', '-R', '-F', '-d', sim_full_path])

            # Check that the data directory and fitness file exist...
            data_file_path = os.path.join(sim_full_path, 'data', 'fitness_final.yaml')
            with open(data_file_path, 'r') as stream:
                fitness_yaml = yaml.load(stream)
                ## Compile fitness information
                #em_fitness = 0.0
                #length_correlation_avg = 0.0
                #fbiorientation = 0.0
                #kinetochore_fitness = 0.0

                ## Get the EM and length correlation fitness information
                #em_fitness = (fitness_yaml['short'] + fitness_yaml['med'] + fitness_yaml['long'])/3.
                #length_correlation_avg = fitness_yaml['length_correlation_avg']

                ## Get the chromosome fitness information, base it off chromosome seconds fraction key
                #if 'chromosome_seconds_fraction' in fitness_yaml:
                #    fbiorientation = fitness_yaml['fbiorientation']
                #    kinetochore_fitness = np.mean([fitness_yaml['chromosome_kc_spb_distance'], fitness_yaml['chromosome_kc_spindle1d']])

                ## Combine total fitness in our special way
                #total_fitness = em_fitness + 2.0*length_correlation_avg + 2.0*fbiorientation + kinetochore_fitness
                #self.fitness[idx] = total_fitness

                # Get what SpindleAnalysis thinks is the total fitness
                total_fitness = fitness_yaml['FINAL_FITNESS']
                self.fitness[idx] = total_fitness

    # Update the best position of the swarm variables
    def UpdateBest(self):
        pcurr = [np.float(-100.0) for i in xrange(self.nparticles)]
        self.pbest_better = [' ' for i in xrange(self.nparticles)]
        self.gbest_better = ' '
        for i in xrange(self.nparticles):
            pcurr[i] = self.fitness[i]
            if pcurr[i] > self.pbest[i]:
                self.pbest[i] = pcurr[i]
                self.pbestx[i] = deepcopy(self.chiparams)
                self.pbestid[i] = np.int(i)
                self.pbest_better[i] = '*'
            if pcurr[i] > self.gbest:
                self.gbest = pcurr[i]
                self.gbestx = deepcopy(self.chiparams)
                self.gbestid = np.int(i)
                self.gbest_better = '*'

    # Update the current elites for the genetic algorithm
    def UpdateBestGenetics(self):
        self.pelite_better = [' ' for i in xrange(self.nelite)]
        for i in xrange(self.nparticles):
            # Test each fitness of the 'best' particles, and figure out which one is best
            lowest_fitness = np.argmin(self.pelite)
            self.plastx[i] = deepcopy(self.chiparams)
            if self.pelite[lowest_fitness] < self.fitness[i]:
                self.pelite[lowest_fitness] = self.fitness[i]
                self.pelitex[lowest_fitness] = deepcopy(self.chiparams)
                self.peliteid[lowest_fitness] = np.int(i)
                self.pelite_better[lowest_fitness] = '*'

    # Update the positions and velocities of the particles in the sytem
    def UpdatePositions(self):
        for idx in xrange(self.nparticles):
            c1 = 2 * random.random()
            c2 = 2 * random.random()
            for ichi in xrange(len(self.chiparams)):
                oldval = self.chiparams[ichi].values[idx]
                upperb = self.chiparams[ichi].bounds[1]
                lowerb = self.chiparams[ichi].bounds[0]
                vmax = (upperb - lowerb) / 2.0
                pbestval = self.pbestx[idx][ichi].values[self.pbestid[idx]]
                gbestval = self.gbestx[ichi].values[self.gbestid]
                #print "oldval: {}".format(oldval)
                #print "vmax:   {}".format(vmax)
                #print "pbestval: {}".format(pbestval)
                #print "gbestval: {}".format(gbestval)
                # Update velocity
                newvel = self.velocity[idx][ichi] * 0.6 + \
                         c1 * (pbestval - oldval) + \
                         c2 * (gbestval - oldval)
                #print "newvel: {}".format(newvel)
                if newvel > vmax:
                    newvel = vmax
                elif newvel < -vmax:
                    newvel = -vmax

                newpos = oldval + newvel
                if newpos > upperb:
                    newpos = 2*upperb - newpos
                    newvel = -newvel
                if newpos < lowerb:
                    newpos = 2*lowerb - newpos
                    newvel = -newvel

                # Set the new variables
                self.velocity[idx][ichi] = newvel
                self.chiparams[ichi].values[idx] = self.chiparams[ichi].paramtype(newpos)
            self.fitness[idx] = float('nan')

    # Update genetics based on tournament selection
    def UpdateGeneticsTournament(self):
        self.crossover_rate = 0.5
        self.mutation_rate = 0.1
        self.ntournament = 5

        for ichild in xrange(self.nparticles/2):
            cidx1 = 2*ichild
            cidx2 = 2*ichild + 1

            tournament = np.random.choice(self.nparticles, self.ntournament, replace=False)  
            
            # Take the 2 best from tournament
            pbest1 = -1000000.0
            pbest2 = -1000000.0
            parent1_idx = -1
            parent2_idx = -1
            for idx in tournament:
                if self.fitness[idx] > pbest1:
                    pbest1 = self.fitness[idx]
                    parent1_idx = idx

            for idx in tournament:
                if idx == parent1_idx:
                    continue
                if self.fitness[idx] > pbest2:
                    pbest2 = self.fitness[idx]
                    parent2_idx = idx

            # Now that we have the two genetics in hand, let us use the crossover points and determine the new genome for the resulting children
            # Iterate along the genome of the chromosomes and pick when we either do a crossover, or a mutation
            for ichi in xrange(len(self.chiparams)):
                # Crossover using random chance of inheriting from parent 1 or 2
                self.parents[cidx1] = [parent1_idx, parent2_idx]
                self.parents[cidx2] = [parent1_idx, parent2_idx]
                rand = random.uniform(0.0, 1.0)
                if (rand <= self.crossover_rate):
                    self.chiparams[ichi].values[cidx1] = self.plastx[parent1_idx][ichi].paramtype(self.plastx[parent1_idx][ichi].values[parent1_idx])
                    self.chiparams[ichi].values[cidx2] = self.plastx[parent2_idx][ichi].paramtype(self.plastx[parent2_idx][ichi].values[parent2_idx])
                else:
                    self.chiparams[ichi].values[cidx2] = self.plastx[parent1_idx][ichi].paramtype(self.plastx[parent1_idx][ichi].values[parent1_idx])
                    self.chiparams[ichi].values[cidx1] = self.plastx[parent2_idx][ichi].paramtype(self.plastx[parent2_idx][ichi].values[parent2_idx])

                # Now check the mutation rate
                rand_mut1 = random.uniform(0.0, 1.0)
                if rand_mut1 <= self.mutation_rate:
                    newval = random.uniform(self.chiparams[ichi].bounds[0], self.chiparams[ichi].bounds[1])
                    self.chiparams[ichi].values[cidx1] = self.chiparams[ichi].paramtype(newval)
                rand_mut2 = random.uniform(0.0, 1.0)
                if rand_mut2 <= self.mutation_rate:
                    newval = random.uniform(self.chiparams[ichi].bounds[0], self.chiparams[ichi].bounds[1])
                    self.chiparams[ichi].values[cidx2] = self.chiparams[ichi].paramtype(newval)

        for i in xrange(self.nparticles):
            self.fitness[i] = float('nan')


    # Update the genetics information for the swarm!
    def UpdateGeneticsRoulette(self):
        self.min_genetics = 0.0

        self.crossover_rate = 0.5
        self.mutation_rate = 0.1
        # Load the current fitness/genetics into a roulette wheel selection@
        # Generate the two parents together, making sure that they are not the same parent (inbreeding is bad)
        for ichild in xrange(self.nparticles/2):
            cidx1 = 2*ichild
            cidx2 = 2*ichild+1

            # go through and move all the fitness to be above 0 (subtract off min)
            self.weight_sum1 = 0.0
            for i in xrange(self.nparticles):
                self.weight_sum1 += self.fitness[i] - self.min_genetics

            # Roulette wheel selection of the available parameters
            value1 = random.uniform(0.0, 1.0) * self.weight_sum1
            parent1_idx = -1
            #cur_value1 = self.min_fitness
            for i in xrange(self.nparticles):
                value1 -= (self.fitness[i] - self.min_genetics)
                if value1 <= 0.0:
                    parent1_idx = i
                    break

            i#print "Choose parent1 idx {} ({})".format(parent1_idx, self.fitness[parent1_idx] - self.min_genetics)

            # Roulette wheel of the resulting set for the next parent!
            self.weight_sum2= 0.0
            for i in xrange(self.nparticles):
                if i == parent1_idx:
                    continue
                self.weight_sum2 += self.fitness[i] - self.min_genetics

            # Roulette wheel selection of the available parameters
            value2 = random.uniform(0.0, 1.0) * self.weight_sum2
            parent2_idx = -1
            for i in xrange(self.nparticles):
                if i == parent1_idx:
                    continue
                value2 -= (self.fitness[i] - self.min_genetics)
                if value2 <= 0.0:
                    parent2_idx = i
                    break

            #print "Choose parent2 idx {} ({})".format(parent2_idx, self.fitness[parent2_idx] - self.min_genetics)

            ## Two point crossover
            ## Two point crossover
            #self.parents[cidx1] = [parent1_idx, parent2_idx]
            #self.parents[cidx2] = [parent1_idx, parent2_idx]
            #cp1 = int(random.uniform(0, len(self.chiparams)))
            #cp2 = int(random.uniform(0, len(self.chiparams)))
            #if cp2 < cp1:
            #    temp = cp1
            #    cp1 = cp2
            #    cp2 = temp
            #if cp1 == cp2:
            #    cp2 = cp1 + 1

            #for ichi in xrange(len(self.chiparams)):
            #    # Parent 1 for 1
            #    if ichi <= cp1:
            #        self.chiparams[ichi].values[cidx1] = self.plastx[parent1_idx][ichi].paramtype(self.plastx[parent1_idx][ichi].values[parent1_idx])
            #        self.chiparams[ichi].values[cidx2] = self.plastx[parent2_idx][ichi].paramtype(self.plastx[parent2_idx][ichi].values[parent2_idx])
            #    elif ichi <= cp2 and ichi > cp1:
            #        self.chiparams[ichi].values[cidx2] = self.plastx[parent1_idx][ichi].paramtype(self.plastx[parent1_idx][ichi].values[parent1_idx])
            #        self.chiparams[ichi].values[cidx1] = self.plastx[parent2_idx][ichi].paramtype(self.plastx[parent2_idx][ichi].values[parent2_idx])
            #    else:
            #        self.chiparams[ichi].values[cidx1] = self.plastx[parent1_idx][ichi].paramtype(self.plastx[parent1_idx][ichi].values[parent1_idx])
            #        self.chiparams[ichi].values[cidx2] = self.plastx[parent2_idx][ichi].paramtype(self.plastx[parent2_idx][ichi].values[parent2_idx])
            #    #Now check the mutation rate
            #    rand_mut1 = random.uniform(0.0, 1.0)
            #    if rand_mut1 <= self.mutation_rate:
            #        newval = random.uniform(self.chiparams[ichi].bounds[0], self.chiparams[ichi].bounds[1])
            #        self.chiparams[ichi].values[cidx1] = self.chiparams[ichi].paramtype(newval)
            #    rand_mut2 = random.uniform(0.0, 1.0)
            #    if rand_mut2 <= self.mutation_rate:
            #        newval = random.uniform(self.chiparams[ichi].bounds[0], self.chiparams[ichi].bounds[1])
            #        self.chiparams[ichi].values[cidx2] = self.chiparams[ichi].paramtype(newval)


            # Now that we have the two genetics in hand, let us use the crossover points and determine the new genome for the resulting children
            # Iterate along the genome of the chromosomes and pick when we either do a crossover, or a mutation
            for ichi in xrange(len(self.chiparams)):
                # Crossover using random chance of inheriting from parent 1 or 2
                # This crossover computation is a random choice of each parent...
                self.parents[cidx1] = [parent1_idx, parent2_idx]
                self.parents[cidx2] = [parent1_idx, parent2_idx]
                rand = random.uniform(0.0, 1.0)
                if (rand <= self.crossover_rate):
                    self.chiparams[ichi].values[cidx1] = self.plastx[parent1_idx][ichi].paramtype(self.plastx[parent1_idx][ichi].values[parent1_idx])
                    self.chiparams[ichi].values[cidx2] = self.plastx[parent2_idx][ichi].paramtype(self.plastx[parent2_idx][ichi].values[parent2_idx])
                else:
                    self.chiparams[ichi].values[cidx2] = self.plastx[parent1_idx][ichi].paramtype(self.plastx[parent1_idx][ichi].values[parent1_idx])
                    self.chiparams[ichi].values[cidx1] = self.plastx[parent2_idx][ichi].paramtype(self.plastx[parent2_idx][ichi].values[parent2_idx])
                
                #Now check the mutation rate
                rand_mut1 = random.uniform(0.0, 1.0)
                if rand_mut1 <= self.mutation_rate:
                    newval = random.uniform(self.chiparams[ichi].bounds[0], self.chiparams[ichi].bounds[1])
                    self.chiparams[ichi].values[cidx1] = self.chiparams[ichi].paramtype(newval)
                rand_mut2 = random.uniform(0.0, 1.0)
                if rand_mut2 <= self.mutation_rate:
                    newval = random.uniform(self.chiparams[ichi].bounds[0], self.chiparams[ichi].bounds[1])
                    self.chiparams[ichi].values[cidx2] = self.chiparams[ichi].paramtype(newval)

        for i in xrange(self.nparticles):
            self.fitness[i] = float('nan')

    # Bias the swarm variables at random
    def BiasSwarm(self, bias):
        # Do via the dataframe that we received
        for idx,row in bias.iterrows():
            # Get the particle id
            pid = np.int(row[0])
            # Loop over the chiparams and set them, note, this has to index by 1 further because of
            # the particle taking up a spot in the dataframe
            for ichi in xrange(len(self.chiparams)):
                self.chiparams[ichi].values[pid] = self.chiparams[ichi].paramtype(row[ichi+1])

    def PrintSwarmCurrent(self):
        str0 = "id  fitness "
        for ichi in xrange(len(self.chiparams)):
            str0 += "{:>12s}{:>12s}".format(self.chiparams[ichi], "vel")
        print str0
        for idx in xrange(self.nparticles):
            str1 = "{0:<3d}  {1:>6.3f} ".format(idx, self.fitness[idx])
            for ichi in xrange(len(self.chiparams)):
                str1 += "{0:>12.3f}".format(self.chiparams[ichi].values[idx])
                str1 += "{0:>12.3f}".format(self.velocity[idx][ichi])
            print str1

    def PrintSwarmBest(self):
        str0 = "id  bestfit  "
        for ichi in xrange(len(self.chiparams)):
            str0 += "{:>10s}    ".format(self.chiparams[ichi])
        print str0
        for idx in xrange(self.nparticles):
            str1 = "{0:<3d}  {1:>6.3f} ".format(idx, self.pbest[idx])
            for ichi in xrange(len(self.chiparams)):
                str1 += " {0:10.3f}   ".format(self.pbestx[idx][ichi].values[self.pbestid[idx]])
            str1 += " {} ".format(self.pbest_better[idx])
            print str1

        str2 = "{0:<3s}  {1:>6.3f} ".format("g", self.gbest)
        for ichi in xrange(len(self.chiparams)):
            str2 += " {0:10.3f}   ".format(self.gbestx[ichi].values[self.gbestid])
        str2 += " {} ".format(self.gbest_better)
        print str2

        #str3 = "{} {} ".format("gfull", self.gbest)
        #for ichi in xrange(len(self.chiparams)):
        #    str3 += " {} ".format(self.gbestx[ichi].values[self.gbestid])
        #print str3

    # Genetic algorithm print information
    def PrintCurrentGenetics(self):
        str0 = "id  fitness "
        for idx in xrange(self.nparticles):
            str1 = "{0:<3d}  {1:>6.3f} ".format(idx, self.fitness[idx])
            for ichi in xrange(len(self.chiparams)):
                str1 += "{0:>12.3f}".format(self.chiparams[ichi].values[idx])
            str1 += " [{}, {}]".format(self.parents[idx][0], self.parents[idx][1])
            print str1


    def PrintGeneticsBest(self):
        str0 = "id  bestfit  "
        for ichi in xrange(len(self.chiparams)):
            str0 += "{:>10s}    ".format(self.chiparams[ichi])
        print str0
        for idx in xrange(self.nelite):
            str1 = "{0:<3d}  {1:>6.3f} ".format(idx, self.pelite[idx])
            for ichi in xrange(len(self.chiparams)):
                str1 += " {0:10.3f}   ".format(self.pelitex[idx][ichi].values[self.peliteid[idx]])
            str1 += " {} ".format(self.pelite_better[idx])
            print str1

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
            if opts.fluid_config: #TODO depricate this for one below
                cp(opts.fluid_config, sd_dir)
            for f in opts.non_yaml:
                cp(f, sd_dir)
            if opts.states:
                for s in opts.states:
                    open(os.path.join(sd_dir, 'sim.{}'.format(s)), 'a')
                

##########################################
if __name__ == "__main__":
    print "Not implemented. This is strictly a library."




