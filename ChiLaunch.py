#!/usr/bin/env python
import sys
import os
import yaml
import argparse

from popen2 import popen2

# #Depricated####################################################################
# def create_job(simpath, statelist, job_name="ChiRun", walltime="1:00", processors = "nodes=1:ppn=1", queue="janus", allocation="UCB00000318", qmgr='slurm'):
#     print "creating job for {0} with states: {1}".format(simpath,statelist)

#     # Customize your options here
#     job_name = simpath
#     simpath = os.path.abspath(simpath)
#     seedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ChiRun.py')
#     command = "{0} {1} {2}".format(sacrunpath, simpath, " ".join(statelist))

#     errlog = os.path.join(simpath, 'sim.err')

#     if qmgr == 'torque':
#         # Open a pipe to the qsub command.
#         output, input = popen2('qsub')
#         job_string = """#!/bin/bash
# #PBS -N {0}
# #PBS -l walltime={1}
# #PBS -l {2}
# #PBS -o {3}
# #PBS -e {4}
# #PBS -A {5}
# #PBS -q {6}
# #PBS -V

# cd $PBS_O_WORKDIR
# {7}""".format(job_name, walltime, processors, log, errlog, allocation, queue, command)
#     elif qmgr == 'slurm':
#         # Open a pipe to the sbatch command.
#         output, input = popen2('sbatch')
#         if walltime.count(':') == 3:
#             walltime = walltime.replace(':','-',1)
#         nnodes = processors.split(':')[0].split('=')[1]
#         nprocs = processors.split(':')[1].split('=')[1]
#         job_string = """#!/bin/bash
# #SBATCH --job-name={0}
# #SBATCH -t {1}
# #SBATCH -N {2}
# #SBATCH -o {4}
# #SBATCH -e {5}
# #SBATCH -A {6}
# #SBATCH --qos={7}

# cd $SLURM_SUBMIT_DIR
# {8}""".format(job_name, walltime, nnodes, nprocs, log, errlog, allocation, queue, command)
#     else:
#         print "Invalid qmgr: {0}".format(qmgr)
#         return

#     # Send job_string to qsub
#     input.write(job_string)
#     input.close()

#     # Print your job and the response to the screen
#     print job_string
#     print output.read()
# #Depricated####################################################################

# Creates multithreaded processor jobs. 
def create_multiprocessor_job(seedpaths, statelist, 
        job_name="ChiRun", walltime="1:00", arg_file = "args.yaml",
        processors = "nodes=1:ppn=12", queue="janus", 
        allocation="UCB00000513", qmgr='slurm'):

    print "creating jobs for:"
    for i, sd_path in enumerate(seedpaths):
        print "sim: {0} with states: {1}".format(sd_path, ", ".join(statelist[i]))
    print ""

    # Customize your options here
    job_name = 'ChiRunBatch'
    seedlaunchpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ChiRun.py')
    log = '/dev/null'
    errlog = '/dev/null'
    if qmgr == 'slurm':
        # Open a pipe to the sbatch command.
        output, input = popen2('sbatch')
        if walltime.count(':') == 3:
            walltime = walltime.replace(':','-',1)
        nnodes = processors.split(':')[0].split('=')[1]
        nprocs = processors.split(':')[1].split('=')[1]
        job_string = """#!/bin/bash
#SBATCH --job-name={0}
#SBATCH -t {1}
#SBATCH -N {2}
#SBATCH -o {3}
#SBATCH -e {4}
#SBATCH -A {5}
#SBATCH --qos={6}

cd $SLURM_SUBMIT_DIR

""".format(job_name, walltime, nnodes, log, errlog, allocation, queue)
        for i, sd_path in enumerate(seedpaths):
            sd_path = os.path.abspath(sd_path)
            command = "{0} -d {1} -a {2} -s {3}".format(seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
            log = os.path.join(sd_path, 'sim.log')
            errlog = os.path.join(sd_path, 'sim.err')
            
            job_string = job_string + "srun -n1 -c{0} {1} 1> {2} 2> {3} &\n".format(nprocs,
                                                                                    command,
                                                                                    log,
                                                                                    errlog)
        job_string = job_string + "wait\n"
        
    elif qmgr == 'torque':
        log = 'sim.log'
        errlog = 'sim.err'
        # Open a pipe to the qsub command.
        output, input = popen2('qsub')
        job_string = """#!/bin/bash
#PBS -N {0}
#PBS -l walltime={1}
#PBS -l {2}
#PBS -o {3}
#PBS -e {4}
#PBS -q {5}
#PBS -V
cd $PBS_O_WORKDIR

""".format(job_name, walltime, processors, log, errlog, queue)
        for i, sd_path in enumerate(seedpaths):
            sd_path = os.path.abspath(sd_path)
            command = "{0} -d {1} -a {2} -s {3}".format(seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
            # command = "{0} {1} {2} {3} {4}".format(seedlaunchpath, sd_path, program, prefix, " ".join(statelist[i]))
            log = os.path.join(sd_path, 'sim.log')
            errlog = os.path.join(sd_path, 'sim.err')

            job_string = job_string + command + " 1> {0} 2> {1}&\n".format(log, errlog);

        job_string = job_string + "wait\n"
        
    else:
        print "Invalid qmgr: {0}".format(qmgr)
        return

    # Send job_string to qsub
    input.write(job_string)
    input.close()

    # Print your job and the response to the screen
    print job_string
    print output.read()

# Create parallel job submissions to be run on the same node
def create_parallel_job(seedpaths, statelist, job_name="ChiRun", walltime="1:00", 
        processors = "nodes=1:ppn=1", queue="janus-long", 
        allocation="UCB00000513", qmgr='slurm', 
        # program="spb_dynamics", prefix="spindle_bd_mp"):
    print "creating jobs for:"
    for i, sd_path in enumerate(seedpaths):
        print "sim: {0} with states: {1}".format(sd_path, ", ".join(statelist[i]))
    print ""

    # Customize your options here
    job_name = 'ChiRunBatch'
    seedlaunchpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ChiRun.py')
    nnodes = processors.split(':')[0].split('=')[1]
    nprocs = processors.split(':')[1].split('=')[1]
    print "nnodes: " + str(nnodes)
    print "nprocs: " + str(nprocs)
    log = '/dev/null'
    errlog = '/dev/null'

    # Slurm submission code
    if qmgr == 'slurm':
        # Open a pipe to the sbatch command.
        output, input = popen2('sbatch')
        if walltime.count(':') == 3:
            walltime = walltime.replace(':','-',1)
        job_string = """#!/bin/bash
#SBATCH --job-name={0}
#SBATCH -t {1}
#SBATCH -N {2}
#SBATCH -o {3}
#SBATCH -e {4}
#SBATCH -A {5}
#SBATCH --qos={6}

cd $SLURM_SUBMIT_DIR


""".format(job_name, walltime, nnodes, log, errlog, allocation, queue)
        for i, sd_path in enumerate(seedpaths):
            sd_path = os.path.abspath(sd_path)
            # command = "{0} {1} {2} {3} {4}".format(seedlaunchpath, sd_path, program, prefix, " ".join(statelist[i]))
            command = "{0} -d {1} -a {2} -s {3}".format(seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
            log = os.path.join(sd_path, 'sim.log')
            errlog = os.path.join(sd_path, 'sim.err')
            job_string = job_string + "srun -n1 --exclusive {0} 1> {1} 2> {2} &\n".format(command, log, errlog)
        job_string = job_string + "wait\n"

    # Torque submission code
    elif qmgr == 'torque':
        # Open a pipe to the qsub command.
        output, input = popen2('qsub')
        job_string = """#!/bin/bash
#PBS -N {0}
#PBS -l walltime={1}
#PBS -l {2}
#PBS -o {3}
#PBS -e {4}
#PBS -q {5}
#PBS -V
cd $PBS_O_WORKDIR

""".format(job_name, walltime, "nodes={0}:ppn={1}".format(nnodes, int(nprocs)), log, errlog, queue)
        for i, sd_path in enumerate(seedpaths):
            sd_path = os.path.abspath(sd_path)
            # command = "{0} {1} {2} {3} {4}".format(seedlaunchpath, sd_path, program, prefix, " ".join(statelist[i]))
            command = "{0} -d {1} -a {2} -s {3}".format(seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
            log = os.path.join(sd_path, 'sim.log')
            errlog = os.path.join(sd_path, 'sim.err')

            job_string = job_string + command + " 1> {0} 2> {1}&\n".format(log, errlog);

        job_string = job_string + "wait\n"
        
    # A valid scheduler was not specified
    else:
        print "Invalid qmgr: {0}".format(qmgr)
        return

    # Send job_string to qsub
    input.write(job_string)
    input.close()

    # Print your job and the response to the screen
    print job_string
    print output.read()


def get_state(path):
    state = []
    if os.path.isfile(os.path.join(path, 'sim.build')): state.append('build') 
    if os.path.isfile(os.path.join(path, 'sim.start')): state.append('start')
    if os.path.isfile(os.path.join(path, 'sim.resume-overwrite')): state.append('resume-overwrite') 
    if os.path.isfile(os.path.join(path, 'sim.resume-append')): state.append('resume-append') 
    if os.path.isfile(os.path.join(path, 'sim.analyze')): state.append('analyze')
    return state

def is_running(path):
    return os.path.isfile(os.path.join(path, '.running'))

def is_error(path):
    return os.path.isfile(os.path.join(path, '.error'))

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def ChiLaunch(simdirs, opts=''):
    # List of all the seeds that will be run
    seeddirs = []

    if opts.prog_options:
        # Do yaml things
        print "prog_options not implemented yet."
    
    for simd in simdirs:
        print "Searching for path {0}".format(simd)

        if os.path.exists(simd):
            print "path exists, checking for seeds..."
            seeddirs = seeddirs + [os.path.join(simd, f) for f in os.listdir(simd)
                                if os.path.isdir(os.path.join(simd, f)) 
                                and not f.startswith('.')]
            if not seeddirs:
                print "no seeds found in sim directory"
                return 1
        else:
            print "sim does not exist"
            return 1
    
    # Determines the programs that will be run on seed directories
    runstates = raw_input("List space separated states you wish to run (leave blank for all): ").split(' ')
    if runstates[0] == '': runstates = ['build', 'start', 'resume-overwrite', 'resume-append', 'analyze']

    seeds = [] # Seed directories to be run
    states = [] # States of seed directories

    # Go through all seed directories and see if they are capable of running
    # ei. No .error file and no .running file
    for sdd in seeddirs:
        if not is_running(sdd) and not is_error(sdd):
            state = get_state(sdd)
            state = list(set(state).intersection(set(runstates)))
            if state:
                seeds.append(sdd)
                states.append(state)
    print "Jobs found: {0}".format(len(seeds))

    n_jobs = raw_input('Input number of jobs to run, (default {0}): '.format(len(seeds))).strip()
    if n_jobs == '': n_jobs = len(seeds)
    else: n_jobs = int(n_jobs)

    scheduler = raw_input('Input scheduler (default torque): ').strip()
    if scheduler == '': scheduler = "torque"

    walltime = raw_input('Input walltime (dd:hh:mm:ss), (default 23:59:00): ' ).strip()
    if walltime == '': walltime = "23:59:00"

    allocation = raw_input('Input allocation (default UCB00000513): ').strip()
    if allocation == '': allocation = "UCB00000513"

    mp = False if query_yes_no("Single processor job?") else True

    nodes = raw_input('Input number of nodes (default 1): ').strip()
    if nodes == '': nodes = "1"

    if scheduler == "torque":
        ppn = raw_input('Input number of processes per node (default 16): ').strip()
        if ppn == '': ppn = "16"
        queue = raw_input('Input job queue (default short2gb): ').strip()
        if queue == '': queue = "short2gb"

    elif scheduler == "slurm":
        ppn = raw_input('Input number of processes per node (default 12): ').strip()
        if ppn == '': ppn = "12"
        queue = raw_input('Input job queue (default janus): ').strip()
        if queue == '': queue = "janus"

    # program = ''
    # prefix = ''
    # if mp:
    #     program = raw_input('Input program you would like to run (default crosslink_sphero_bd_mp): ').strip()
    #     if program == '': program = "crosslink_sphero_bd_mp"
    #     prefix = raw_input('Input prefix to analysis files (default crosslink_sphero_bd_mp): ').strip()
    #     if prefix == '': prefix = "crosslink_sphero_bd_mp"
    # elif not mp:
    #     program = raw_input('Input program you would like to run (default spindle_bd_mp): ').strip()
    #     if program == '': program = "spindle_bd_mp"
    #     prefix = raw_input('Input prefix to analysis files (default spindle_bd_mp): ').strip()
    #     if prefix == '': prefix = "spindle_bd_mp"

    if not query_yes_no("Generating job ({0}) for states ({1}) with walltime ({2}) on queue ({3}) and allocation ({4}) with scheduler({5}).".format(program, ", ".join(runstates), walltime, queue, allocation, scheduler)):
        return 1

    processors = "nodes={0}:ppn={1}".format(nodes,ppn)
    
    if not mp:
        for i_block in range(0, int(n_jobs/int(ppn))+1):
            # Find the index range of the seeds that you are running
            starti = i_block * int(ppn)
            endi = starti + int(ppn)
            # If end index is greater the number of seeds make end the last seed run
            if endi > len(seeds):
                endi = len(seeds)
            if endi > starti:
                create_parallel_job(seeds[starti:endi], states[starti:endi], walltime=walltime, allocation=allocation, queue=queue, qmgr=scheduler, processors=processors, program=program, prefix=prefix)
            # Torque scheduler has a 10 second update time 
            # make sure you wait before adding another
            import time
            if scheduler == "torque":
                time.sleep(10)
            else:
                time.sleep(.1)
    else:
        for i_block in range(0, n_jobs):
            create_multiprocessor_job([seeds[i_block]], [states[i_block]], walltime=walltime, allocation=allocation, queue=queue, qmgr=scheduler, processors=processors)
            import time
            if scheduler == "torque":
                time.sleep(10)
            else:
                time.sleep(.1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Arguments are the simulation directories to be run
        ChiLaunch(simdirs=sys.argv[1:], opts='')
    else:
        print "must supply directory argument"
