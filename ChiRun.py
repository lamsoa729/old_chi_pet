#!/usr/bin/env python
import sys
import os
from subprocess import call
import shutil

def run_start(workdir, program="spindle_bd_mp", prefix="spindle_bd_mp"):
    print "starting sim in {0}".format(workdir)
    sys.stdout.flush()
    if os.path.exists(workdir):
        os.chdir(workdir)
        open('.running', 'a').close()
        args = [program, prefix+".default", prefix+".equil"]
        status = call(args)
        os.remove('.running')
        return status
    else:
        return 1

def run_analyze(workdir, prefix="spindle_bd_mp"):
    print "starting sim in {0}".format(workdir)
    sys.stdout.flush()
    if os.path.exists(workdir):
        os.chdir(workdir)
        open('.running', 'a').close()
        args = ["spindle_analysis", prefix+".default", prefix+".equil", prefix+".initial_config", prefix+".posit"]
        status = call(args)
        os.remove('.running')
        return status
    else:
        return 1
    

if __name__ == '__main__':
    print sys.argv
    workdir = sys.argv[1]
    program = sys.argv[2]
    states = sys.argv[3:]
    print workdir
    print states

    if 'start' in states:
        if run_start(workdir, program):
            print "run failed"
            open('.error', 'a').close()
        else:
            os.remove('sim.start')
    if 'analyze' in states:
        if run_analyze(workdir):
            print "run failed"
            open('.error', 'a').close()
        else:
            os.remove('sim.analyze')
