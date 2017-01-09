#!/usr/bin/env python
import sys
import os
from subprocess import call
import shutil
import yaml
import argparse

'''
Name: ChiMain.py
Description: Main control program for xi(chi)-launcher. Runs all newagebob code.
Input: To view type ChiRun.py -h
Output: Runs seed (singular) simulations
'''

# Dictionary of commands used for spindle_bd_mp.
# This is the default commands when using ChiRun.
default_args = { 'run': [ 'spindle_bd_mp',
                          'spindle_bd_mp.default',
                          'spindle_bd_mp.equil',
                          'spindle_bd_mp.yaml',
                          'crosslink_params.yaml'],
                 'analyze': [ 'spindle_analsysis',
                              'spindle_bd_mp.default',
                              'spindle_bd_mp.equil',
                              'spindle_bd_mp.initial_config',
                              'spindle_bd_mp.posit']
                 }

def run_parse_args():
    parser = argparse.ArgumentParser(prog='Chi.py')
    parser.add_argument('-d', '--workdir', type=str, required=True,
            help='Name of the working directory where simulation will be run')
    parser.add_argument('-a', '--args_file', type=str,
            help='Name file that holds the program argument list.')
    # parser.add_argument('-p', '--program', type=str, required=True,
            # help='Name of program that will be run')
    parser.add_argument('-s', '--states', nargs='+', type=str, required=True,
            help='Name of all the states the simulation will run eg. start, build, analyze, etc.')

    opts = parser.parse_args()
    return opts


def run_start(workdir, args): #, prefix="spindle_bd_mp"):
    print "starting sim in {0}".format(workdir)
    sys.stdout.flush()
    if os.path.exists(workdir):
        os.chdir(workdir)
        print args
        open('.running', 'a').close()
        # args = [program, prefix+".default", prefix+".equil"]
        status = call(args)
        os.remove('.running')
        return status
    else:
        return 1

def run_analyze(workdir, args):
    print "starting sim in {0}".format(workdir)
    sys.stdout.flush()
    if os.path.exists(workdir):
        os.chdir(workdir)
        open('.running', 'a').close()
        # args = ["spindle_analysis", prefix+".default", prefix+".equil", prefix+".initial_config", prefix+".posit"]
        status = call(args)
        os.remove('.running')
        return status
    else:
        return 1
    

if __name__ == '__main__':

    opts = run_parse_args()

    #Check to see if seed directory exists
    args_dict = {}
    if not os.path.exists(opts.workdir):
        print "Run failed. Directory {} does not exists".format(opts.workdir)

    else:
        if (opts.args_file and 
                os.path.exists(os.path.join(opts.workdir, opts.args_file))):
            with open(os.path.join(opts.workdir, opts.args_file), 'r') as f:
                af = yaml.load(f)
        else:
            af = default_args

    if 'start' in opts.states:
        if run_start(opts.workdir, af['start']):
            print "run failed"
            open('.error', 'a').close()
        else:
            os.remove('sim.start')
    if 'analyze' in opts.states:
        if run_analyze(opts.workdir, af['analyze']):
            print "run failed"
            open('.error', 'a').close()
        else:
            os.remove('sim.analyze')
