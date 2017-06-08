#!/usr/bin/env python
import sys
import os
import yaml
import argparse
import re

from popen2 import popen2

# Creates multithreaded processor jobs. 
def create_multiprocessor_job(seedpaths, statelist, job_name="ChiRun", walltime="1:00",
        nnodes= "1", ntasks = "1", nprocs = "24", queue="shas", args_file="args.yaml",
        qos="condo", allocation="ucb-summit-smr", qmgr='slurm'):
    print "creating jobs for:"
    for i, sd_path in enumerate(seedpaths):
        print "sim: {0} with states: {1}".format(sd_path, ", ".join(statelist[i]))
    print ""

    # Customize your options here
    job_name = 'ChiRunBatch'
    seedlaunchpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ChiRun.py')
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
#SBATCH --ntasks-per-node {3}
#SBATCH --cpus-per-task {4}
#SBATCH -o {5}
#SBATCH -e {6}
#SBATCH -A {7}
#SBATCH --qos={8}
#SBATCH --partition={9}

cd $SLURM_SUBMIT_DIR


""".format(job_name, walltime, nnodes, ntasks, nprocs, log, errlog, allocation, qos, queue)
        for i, sd_path in enumerate(seedpaths):
            sd_path = os.path.abspath(sd_path)
            command = "{0} -d {1} -a {2} -s {3}".format(seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
            log = os.path.join(sd_path, 'sim.log')
            errlog = os.path.join(sd_path, 'sim.err')
            job_string = job_string + "srun -n1 --exclusive {0} 1> {1} 2> {2} &\n".format(command, log, errlog)
        job_string = job_string + "wait\n"
        
# FIXME: Needs to be tested on pando before run
    elif qmgr == 'torque':
        log = 'sim.log'
        errlog = 'sim.err'
        # Open a pipe to the qsub command.
        output, input = popen2('qsub')
        job_string = """#!/bin/bash
#PBS -N {0}
#PBS -l walltime={1}
#PBS -l nodes={2}:ppn={3}
#PBS -o {4}
#PBS -e {5}
#PBS -q {6}
#PBS -V
cd $PBS_O_WORKDIR

""".format(job_name, walltime, nnodes, nprocs, log, errlog, queue)
        for i, sd_path in enumerate(seedpaths):
            sd_path = os.path.abspath(sd_path)
            command = "{0} -d {1} -a {2} -s {3}".format(seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
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

# Create parallel job submissions to be run on the same node(Depricated)
# def create_parallel_job(seedpaths, statelist, job_name="ChiRun", walltime="1:00", 
#         nnodes="1", ntasks ="1", nprocs="24", queue="janus-long", args_file="args.yaml",
#         allocation="ucb-summit-smr", qmgr='slurm'):
#         # program="spb_dynamics", prefix="spindle_bd_mp"):
#     print "creating jobs for:"
#     for i, sd_path in enumerate(seedpaths):
#         print "sim: {0} with states: {1}".format(sd_path, ", ".join(statelist[i]))
#     print ""

#     # Customize your options here
#     job_name = 'ChiRunBatch'
#     seedlaunchpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ChiRun.py')
#     print "nnodes: " + str(nnodes)
#     print "nprocs: " + str(nprocs)
#     log = '/dev/null'
#     errlog = '/dev/null'

#     # Slurm submission code
#     if qmgr == 'slurm':
#         # Open a pipe to the sbatch command.
#         output, input = popen2('sbatch')
#         if walltime.count(':') == 3:
#             walltime = walltime.replace(':','-',1)
#         job_string = """#!/bin/bash
# #SBATCH --job-name={0}
# #SBATCH -t {1}
# #SBATCH -N {2}
# #SBATCH --ntasks-per-node {3}
# #SBATCH -o {4}
# #SBATCH -e {5}
# #SBATCH -A {6}
# #SBATCH --qos={7}
# #SBATCH --partition={8}

# cd $SLURM_SUBMIT_DIR


# """.format(job_name, walltime, nnodes, nprocs, log, errlog, allocation, "condo", queue)
#         for i, sd_path in enumerate(seedpaths):
#             sd_path = os.path.abspath(sd_path)
#             # command = "{0} {1} {2} {3} {4}".format(seedlaunchpath, sd_path, program, prefix, " ".join(statelist[i]))
#             command = "{0} -d {1} -a {2} -s {3}".format(seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
#             log = os.path.join(sd_path, 'sim.log')
#             errlog = os.path.join(sd_path, 'sim.err')
#             job_string = job_string + "srun -n1 --exclusive {0} 1> {1} 2> {2} &\n".format(command, log, errlog)
#         job_string = job_string + "wait\n"

#     # Torque submission code
#     elif qmgr == 'torque':
#         # Open a pipe to the qsub command.
#         output, input = popen2('qsub')
#         job_string = """#!/bin/bash
# #PBS -N {0}
# #PBS -l walltime={1}
# #PBS -l {2}
# #PBS -o {3}
# #PBS -e {4}
# #PBS -q {5}
# #PBS -V
# cd $PBS_O_WORKDIR

# """.format(job_name, walltime, "nodes={0}:ppn={1}".format(nnodes, int(nprocs)), log, errlog, queue)
#         for i, sd_path in enumerate(seedpaths):
#             sd_path = os.path.abspath(sd_path)
#             # command = "{0} {1} {2} {3} {4}".format(seedlaunchpath, sd_path, program, prefix, " ".join(statelist[i]))
#             command = "{0} -d {1} -a {2} -s {3}".format(seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
#             log = os.path.join(sd_path, 'sim.log')
#             errlog = os.path.join(sd_path, 'sim.err')

#             job_string = job_string + command + " 1> {0} 2> {1}&\n".format(log, errlog);

#         job_string = job_string + "wait\n"
        
#     # A valid scheduler was not specified
#     else:
#         print "Invalid qmgr: {0}".format(qmgr)
#         return

#     # Send job_string to qsub
#     input.write(job_string)
#     input.close()

#     # Print your job and the response to the screen
#     print job_string
#     print output.read()


def get_state(path):
    state = []
    # Find all sim.* (excluding sim.err and sim.log)
    file_pat = re.compile('sim\.(?!err)(?!log).+')
    for f in os.listdir(path):
        if file_pat.match(f):
            state.append(f.split('.')[-1]) # WARNING states may not have a '.' in the name.
            # TODO In future use look ahead function in re.match to 
            # to find correct state with list comprehension
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
    
    if opts and opts.args_file:
        args_file = opts.args_file
    else:
        args_file = "args.yaml"
    
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
    if runstates[0] == '': runstates = 'all'

    seeds = [] # Seed directories to be run
    states = [] # States of seed directories

    # Go through all seed directories and see if they are capable of running
    # ei. No .error file and no .running file
    for sdd in seeddirs:
        if not is_running(sdd) and not is_error(sdd):
            state = get_state(sdd)
            # print state
            if runstates != 'all':
                state = list(set(state).intersection(set(runstates)))
            if state:
                seeds.append(sdd)
                states.append(state)
    print "Jobs found: {0}".format(len(seeds))

    n_jobs = raw_input('Input number of jobs to run, (default {0}): '.format(len(seeds))).strip()
    if n_jobs == '': n_jobs = len(seeds)
    else: n_jobs = int(n_jobs)

    scheduler = raw_input('Input scheduler (default slurm): ').strip()
    if scheduler == '' or scheduler == 'slurm': scheduler, queue, nprocs = ("slurm", "shas", "1")
    #FIXME doesn't work for torque at the moment but shouldn't require too much to fix up
    elif scheduler == 'torque': queue, nprocs = ("short2gb", "16") 
    else: 
        print "Chi-pet is not programmed for scheduler '{}'.".format(scheduler)
        sys.exit(1)

    allocation = raw_input('Input allocation (default ucb-summit-smr): ').strip()
    if allocation == '': allocation, qos = ("ucb-summit-smr", "condo")
    else: qos = "normal"

    qos_switch = raw_input('Input qos aka quality of service (default {}): '.format(qos)).strip()
    if qos_switch != '': qos = qos_switch

    queue_switch = raw_input('Input job queue (default {}): '.format(queue)).strip()
    if queue_switch != '': queue = queue_switch

    walltime = raw_input('Input walltime (dd:hh:mm:ss), (default 23:59:00): ' ).strip()
    if walltime == '': walltime = "23:59:00"

    nodes = raw_input('Input number of nodes (default 1): ').strip()
    if nodes == '': nodes = "1"

    ntasks = raw_input('Input number of tasks per node (default 24): ').strip()
    if ntasks == '': ntasks = "24"

    nprocs_switch = raw_input('Input number of processors per task (default {}): '.format(nprocs)).strip() 
    if nprocs_switch != '': nprocs = nprocs_switch

    if not query_yes_no("Generating job for states ({0}) with walltime ({1}) on queue ({2}) in allocation ({3}) and QOS ({4}) with scheduler ({5}).".format(" ".join(runstates), walltime, queue, allocation, qos, scheduler)):
        return 1

    # processors = "nodes={0}:ppn={1}".format(nodes,ppn)
    
    for i_block in range(0, int(n_jobs/int(ntasks))+1):
        # Find the index range of the seeds that you are running
        starti = i_block * int(ntasks)
        endi = starti + int(ntasks)
        # If end index is greater the number of seeds make end the last seed run
        if endi > len(seeds):
            endi = len(seeds)
        if endi > starti:
            create_multiprocessor_job(seeds[starti:endi], states[starti:endi], walltime=walltime, 
                    nnodes=nodes, ntasks=ntasks, nprocs=nprocs, queue=queue, qos=qos,
                    allocation=allocation, qmgr=scheduler)
        # Torque scheduler has a 10 second update time 
        # make sure you wait before adding another
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
