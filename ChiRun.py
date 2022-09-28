#!/usr/bin/env python
import sys
import os
from subprocess import call
import shutil
import yaml
from ChiLib import *
from collections import OrderedDict
import argparse

'''
Name: ChiMain.py
Description: Main control program for xi(chi)-launcher. Runs all newagebob code.
Input: To view type ChiRun.py -h
Output: Runs seed (singular) simulations
'''

# Dictionary of commands used for spindle_bd_mp.
# This is the default commands when using ChiRun.
default_args = OrderedDict([('run', ['spindle_bd_mp',
                                     'spindle_bd_mp.default',
                                     'spindle_bd_mp.equil',
                                     'spindle_bd_mp.yaml',
                                     'crosslink_params.yaml']),
                            ('analyze', ['spindle_analsysis',
                                         'spindle_bd_mp.default',
                                         'spindle_bd_mp.equil',
                                         'spindle_bd_mp.initial_config',
                                         'spindle_bd_mp.posit'])
                            ])
# TODO Future args.yaml file so order is preserved.
# default_args = { [{'run': [ 'spindle_bd_mp',
# 'spindle_bd_mp.default',
# 'spindle_bd_mp.equil',
# 'spindle_bd_mp.yaml',
# 'crosslink_params.yaml'}],
# {'analyze': [ 'spindle_analsysis',
# 'spindle_bd_mp.default',
# 'spindle_bd_mp.equil',
# 'spindle_bd_mp.initial_config',
# 'spindle_bd_mp.posit']}
# ] }


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


def run_start(workdir, args):  # , prefix="spindle_bd_mp"):
    print("starting sim in {0}".format(workdir))
    sys.stdout.flush()
    if os.path.exists(workdir):
        os.chdir(workdir)
        print(args)
        open('.running', 'a').close()
        # args = [program, prefix+".default", prefix+".equil"]
        status = call(args)
        os.remove('.running')
        return status
    else:
        return 1


def run_analyze(workdir, args):
    print("starting sim in {0}".format(workdir))
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


def run_args(workdir, state, args):
    action = state + '-ing'
    print("Started {} sim in {}".format(action, args))
    sys.stdout.flush()
    if os.path.exists(workdir):
        os.chdir(workdir)
        open('.' + action, 'a').close()
        status = call(args)
        os.remove('.' + action)
        return status
    else:
        return 1


class ChiRun(object):
    def __init__(self, opts):
        self.opts = opts

    def Run(self, opts):
        args_dict = {}
        if not os.path.exists(opts.workdir):
            print(
                "Run failed. Directory {} does not exists".format(
                    opts.workdir))

        else:
            if (opts.args_file and
                    os.path.exists(os.path.join(opts.workdir, opts.args_file))):
                af = CreateDictFromYamlFile(
                    os.path.join(opts.workdir, opts.args_file))
            # with open(os.path.join(opts.workdir, opts.args_file), 'r') as f:
            else:
                af = default_args

        print(OrderedYamlDump(af, default_flow_style=False))
        for k, l in af.items():
            print("File= {}, Dictionary= {}".format(k, " ".join(l)))

            if k in opts.states:
                if run_args(opts.workdir, k, l):
                    print("run failed")
                    open('.error', 'a').close()
                elif os.path.exists('sim.{}'.format(k)):
                    os.remove('sim.{}'.format(k))


if __name__ == '__main__':

    opts = run_parse_args()

    c = ChiRun(opts)
    c.Run(opts)
