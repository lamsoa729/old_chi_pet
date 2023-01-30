#!/usr/bin/env python
import sys
import os
import yaml
import argparse
import re
import fnmatch

from pathlib import Path
from subprocess import Popen, PIPE, run


def create_disbatch_job(seedpaths, statelist,
                        job_name="ChiRun",
                        walltime="1:00",
                        ntasks="40",
                        tasks_per_node="40",
                        cpus_per_task="1",
                        constraint="rome",
                        partition="ccb",
                        task_name="tasks.txt",
                        args_file="args.yaml",
                        env_sh='~/SetCGlassEnv.sh',
                        **kwargs):
    print("creating jobs for:")
    for i, sd_path in enumerate(seedpaths):
        print("sim: {0} with states: {1}".format(
            sd_path, ", ".join(statelist[i])))
    print("")

    if walltime.count(':') == 3:
        walltime = walltime.replace(':', '-', 1)

    seedlaunchpath = Path(__file__).resolve().parent / 'ChiRun.py'

    job_string = """# DisBatch task file made with chi-Pet
#DISBATCH PREFIX  cd {0} ; source {1} ; \n
""".format(Path.cwd(), env_sh)

    for i, sd_path in enumerate(seedpaths):
        sd_path = Path(sd_path).resolve()
        command = "{0} -d {1} -a {2} -s {3}".format(
            seedlaunchpath, sd_path, args_file, " ".join(statelist[i]))
        log = sd_path / 'sim.log'
        errlog = sd_path / 'sim.err'
        job_string += "{0} 1> {1} 2> {2} \n".format(command, log, errlog)
    with open(task_name, 'w') as task_file:
        task_file.write(job_string)

    with open('submit.slurm', 'w') as submit_file:
        sub_str = """#!/bin/bash
module load disBatch

sbatch --job-name {0} \\
        --time {1} \\
        --ntasks {2} \\
        --ntasks-per-node {3} \\
        -o {5} -e {6} \\
        --constraint {7} \\
        --partition {8} \\
        disBatch -c {4} {9}
        """.format(job_name,
                   walltime,
                   ntasks,
                   tasks_per_node,
                   cpus_per_task,
                   '/dev/null',
                   '/dev/null',
                   constraint,
                   partition,
                   task_name)
        submit_file.write(sub_str)

# Create the slurm submissions directly and execute them
def create_longleaf_job(seedpaths, statelist,
                        job_name="ChiRun",
                        partition="general",
                        gres="gres:1",
                        qos="gpu_access",
                        ntasks="1",
                        cpus_per_task="1",
                        mem="8G",
                        walltime="1:00",
                        args_file="args.yaml",
                        **kwargs):
                        
    print("creating jobs for:")
    for i, sd_path in enumerate(seedpaths):
        print("sim: {0} with states: {1}".format(
            sd_path, ", ".join(statelist[i])))
    print("")
    
    if walltime.count(':') == 3:
        walltime = walltime.replace(':', '-', 1)

    # Write everythign to shell script, then execute the shell script
    for i, sd_path in enumerate(seedpaths):
        sd_path = Path(sd_path).resolve()
        run_script = sd_path / 'run_hoomd.sh'
        args_file = sd_path / args_file
        outlog = sd_path / 'sim.log'

        # Peek inside the args file to see what we are running
        with open(args_file, 'r') as stream: yaml_dict = yaml.safe_load(stream)
        python_file = yaml_dict['start'][1]
        default_file = yaml_dict['start'][3]
        analysis_file = yaml_dict['analysis'][1]

        # Create the job script directly
        with open(run_script, 'w') as fname:
            job_string = """#!/bin/bash

#SBATCH --job-name={0}
#SBATCH --partition={1}
#SBATCH --gres={2}
#SBATCH --qos={3}
#SBATCH --ntasks={4}
#SBATCH --cpus-per-task={5}
#SBATCH --mem={6}
#SBATCH --time={7}
#SBATCH --output={8}

unset OMP_NUM_THREADS
module load git
module load cmake
module load python/3.9.6
module load gcc/9.1.0
module load cuda/11.4

source /nas/longleaf/home/edelmaie/virtual_envs/hoomd300beta13/bin/activate

echo $PWD
cd {9}
echo $PWD

start=`date +%s`

python3 {10} --yaml {11} \n

end=`date +%s`
runtime=$((end-start))
echo $runtime

python3 {12} -sd --yaml {11} -A -F -G\n
            """.format(job_name,
                       partition,
                       gres,
                       qos,
                       ntasks,
                       cpus_per_task,
                       mem,
                       walltime,
                       outlog,
                       sd_path,
                       python_file,
                       default_file,
                       analysis_file)
            fname.write(job_string)

        # Execute the script
        run(["sbatch", run_script])

# Create a longleaf job for LAMMPS (sets up later runs)
def create_lammps_snp_job(seedpaths, statelist,
                          job_name="ChiRun",
                          partition="general",
                          ntasks="1",
                          cpus_per_task="1",
                          mem="8G",
                          walltime="1:00",
                          args_file="args.yaml",
                          **kwargs):
    print(f"creating jobs for:")
    for i, sd_path in enumerate(seedpaths):
        print("sim: {0} with states: {1}".format(
            sd_path, ", ".join(statelist[i])))
    print("")

    if walltime.count(':') == 3:
        walltime = walltime.replace(":", "-", 1)

    # Write everything to a shell script, then execute the shell script
    for i, sd_path in enumerate(seedpaths):
        sd_path = Path(sd_path).resolve()
        run_script = sd_path / 'run_lammps.sh'
        args_file = sd_path / args_file
        outlog = sd_path / 'sim_lammps_setup.log'

        # Peek inside the args file to see what we are running
        with open(args_file, 'r') as stream: yaml_dict = yaml.safe_load(stream)
        python_file = yaml_dict['start'][1]
        default_file = yaml_dict['start'][3]
        analysis_file = yaml_dict['analysis'][1]

        # Create the uob script directly
        with open(run_script, 'w') as fname:
            job_string = """#!/bin/bash

#SBATCH --job-name={0}
#SBATCH --partition={1}
#SBATCH --ntasks={2}
#SBATCH --cpus-per-task={3}
#SBATCH --mem={4}
#SBATCH --time={5}
#SBATCH --output={6}

unset OMP_NUM_THREADS
module load git
module load cmake
module load python/3.9.6
module load gcc/9.1.0
module load cuda/11.4

source /nas/longleaf/home/edelmaie/virtual_envs/hoomd340/bin/activate

echo $PWD
cd {7}
echo $PWD

start=`date +%s`

python3 {8} --yaml {9} \n

end=`date +%s`
runtime=$((end-start))
echo $runtime

sbatch run_equilibrate.sh

            """.format(job_name,
                       partition,
                       ntasks,
                       cpus_per_task,
                       mem,
                       walltime,
                       outlog,
                       sd_path,
                       python_file,
                       default_file)
            fname.write(job_string)

        # Execute the script
        run(["sbatch", run_script])

# Create a dogwood job for slurm
def create_lammps_dogwood_job(seedpaths, statelist,
                          job_name="ChiRun",
                          partition="debug_queue",
                          ntasks="1",
                          cpus_per_task="1",
                          mem="8G",
                          walltime="1:00",
                          args_file="args.yaml",
                          **kwargs):
    print(f"creating jobs for:")
    for i, sd_path in enumerate(seedpaths):
        print("sim: {0} with states: {1}".format(
            sd_path, ", ".join(statelist[i])))
    print("")

    if walltime.count(':') == 3:
        walltime = walltime.replace(":", "-", 1)

    # Write everything to a shell script, then execute the shell script
    for i, sd_path in enumerate(seedpaths):
        sd_path = Path(sd_path).resolve()
        run_script = sd_path / 'run_lammps.sh'
        args_file = sd_path / args_file
        outlog = sd_path / 'sim_lammps_setup.log'

        # Peek inside the args file to see what we are running
        with open(args_file, 'r') as stream: yaml_dict = yaml.safe_load(stream)
        python_file = yaml_dict['start'][1]
        default_file = yaml_dict['start'][3]
        analysis_file = yaml_dict['analysis'][1]

        # Create the uob script directly
        with open(run_script, 'w') as fname:
            job_string = """#!/bin/bash

#SBATCH --job-name={0}
#SBATCH --partition={1}
#SBATCH --nodes=1
#SBATCH --mem={2}
#SBATCH --time={3}
#SBATCH --output={4}

unset OMP_NUM_THREADS
module load git
module load cmake
module load python/3.9.6
module load gcc/9.1.0
module load cuda/11.4

source /nas/longleaf/home/edelmaie/virtual_envs/hoomd340/bin/activate

echo $PWD
cd {5}
echo $PWD

start=`date +%s`

python3 {6} --yaml {7} \n

end=`date +%s`
runtime=$((end-start))
echo $runtime

sbatch run_equilibrate.sh

            """.format(job_name,
                       partition,
                       mem,
                       walltime,
                       outlog,
                       sd_path,
                       python_file,
                       default_file)
            fname.write(job_string)

        # Execute the script
        run(["sbatch", run_script])

def get_state(path):
    state = []
    # Find all sim.* (excluding sim.err and sim.log)
    file_pat = re.compile(r'sim\.(?!err)(?!log).+')
    for f in os.listdir(path):
        if file_pat.match(f):
            # WARNING states may not have a '.' in the name.
            state.append(f.split('.')[-1])
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
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
    return


def string_query(msg, kword, dft_dict):
    """TODO: Docstring for string_query.
    @return: TODO

    """
    ans = input('{0} (default {1}): '.format(msg, dft_dict[kword])).strip()
    if ans != '':
        dft_dict[kword] = ans
    return


def ChiLaunch(simdirs, opts=''):
    # List of all the seeds that will be run
    seeddirs = []

    if opts and opts.args_file:
        args_file = opts.args_file
    else:
        args_file = "args.yaml"

    for simd in simdirs:
        print("Searching for path {0}".format(simd))

        if fnmatch.fnmatch(simd, '*.txt'):
            print("Ignoring text file {}".format(simd))
            continue
        if os.path.exists(simd):
            print("path exists, checking for seeds...")
            seeddirs = seeddirs + [os.path.join(simd, f) for f in os.listdir(simd)
                                   if os.path.isdir(os.path.join(simd, f))
                                   and not f.startswith('.')]
            if not seeddirs:
                print("no seeds found in sim directory")
                return 1
        else:
            print("sim does not exist")
            return 1

    # Determines the programs that will be run on seed directories
    runstates = input(
        "List space separated states you wish to run (leave blank for all): ").split(' ')
    if runstates[0] == '':
        runstates = ['all']

    seeds = []  # Seed directories to be run
    states = []  # States of seed directories

    # Go through all seed directories and see if they are capable of running
    # ei. No .error file and no .running file
    for sdd in seeddirs:
        if not is_running(sdd) and not is_error(sdd):
            state = get_state(sdd)
            if runstates != ['all']:
                state = list(set(state).intersection(set(runstates)))
            if state:
                seeds.append(sdd)
                states.append(state)
    print("Jobs found: {0}".format(len(seeds)))

    # defaults
    dft_dict = {"supercomputer_name": "disBatch",
                "job_name": "ChiRun",
                "walltime": "48:00:00",
                "ntasks": "128",
                "tasks_per_node": "128",
                "cpus_per_task": "1",
                "constraint": "rome",
                "partition": "ccb",
                "task_name": "tasks.txt",
                "args_file": "args.yaml",
                "env_sh": '~/SetCGlassEnv.sh'
                }

    string_query('Input supercomputer name', 'supercomputer_name', dft_dict)

    if dft_dict['supercomputer_name'] == 'disBatch':
        string_query('Input job name', 'job_name', dft_dict)
        string_query('Input node type', 'constraint', dft_dict)
        string_query('Input partition', 'partition', dft_dict)
        string_query('Input the number of tasks at a time', 'ntasks', dft_dict)
        string_query('Input how many tasks per node', 'tasks_per_node', dft_dict)
        string_query('Input how many cpus per task', 'cpus_per_task', dft_dict)
        string_query('Input walltime (dd:hh:mm:ss)', 'walltime', dft_dict)
        string_query('Input environment script name', 'env_sh', dft_dict)
        check_info_string = ("Generating ({}) disBatch job for ({}) concurrent tasks "
                             "using a total of ({}) cpus per tasks "
                             "with states ({}) "
                             "run for ({}) "
                             "in partition ({}) "
                             "on ({}) nodes "
                             "with environment from ({})."
                             ).format(dft_dict['job_name'],
                                      dft_dict['ntasks'],
                                      (int(dft_dict['ntasks']) *
                                       int(dft_dict['cpus_per_task'])),
                                      " ".join(runstates),
                                      dft_dict['walltime'],
                                      dft_dict['partition'],
                                      dft_dict['constraint'],
                                      dft_dict['env_sh'],
                                      )
        if not query_yes_no(check_info_string):
            return 1

        create_disbatch_job(seeds, states, **dft_dict)

    elif dft_dict['supercomputer_name'] == 'longleaf':
        # Change some of the default behaviors
        dft_dict['job_name'] = "hoomd_membrane"
        dft_dict['partition'] = "volta-gpu"
        dft_dict['gres'] = "gpu:1"
        dft_dict['qos'] = "gpu_access"
        dft_dict['ntasks'] = "1"
        dft_dict['cpus_per_task'] = "8"
        dft_dict['mem'] = "8G"
        dft_dict['walltime'] = "08:00:00"

        string_query('Input job name', 'job_name', dft_dict)
        string_query('Input partition', 'partition', dft_dict)
        string_query('Input gres (number of gpus)', 'gres', dft_dict)
        string_query('Input the number of tasks at a time', 'ntasks', dft_dict)
        string_query('Input how many cpus per task', 'cpus_per_task', dft_dict)
        string_query('Input how much memory', 'mem', dft_dict)
        string_query('Input walltime (dd:hh:mm:ss)', 'walltime', dft_dict)

        check_info_string = ("Generating ({}) longleaf job for ({}) concurrent tasks "
                             "using graphics ({}) "
                             "and qos ({}) "
                             "using a total of ({}) cpus per tasks "
                             "with ({}) memory "
                             "with states ({}) "
                             "run for ({}) "
                             "in partition ({})."
                             ).format(dft_dict['job_name'],
                                      dft_dict['ntasks'],
                                      dft_dict['gres'],
                                      dft_dict['qos'],
                                      (int(dft_dict['ntasks']) *
                                       int(dft_dict['cpus_per_task'])),
                                      " ".join(runstates),
                                      dft_dict['mem'],
                                      dft_dict['walltime'],
                                      dft_dict['partition'],
                                      )

        if not query_yes_no(check_info_string):
            return 1

        create_longleaf_job(seeds, states, **dft_dict)

    elif dft_dict['supercomputer_name'] == 'snp':
        # Set up an SNP job on longleaf
        # This is done through the normal general queue to set everything up
        dft_dict['job_name'] = "lammps_snp"
        dft_dict['partition'] = "general"
        dft_dict['ntasks'] = "1"
        dft_dict['cpus_per_task'] = "8"
        dft_dict['mem'] = "8G"
        dft_dict['walltime'] = "01:00:00"

        string_query('Input job name', 'job_name', dft_dict)
        string_query('Input partition', 'partition', dft_dict)
        string_query('Input the number of tasks at a time', 'ntasks', dft_dict)
        string_query('Input how many cpus per task', 'cpus_per_task', dft_dict)
        string_query('Input how much memory', 'mem', dft_dict)
        string_query('Input walltime (dd:hh:mm:ss)', 'walltime', dft_dict)

        check_info_string = ("Generating ({}) longleaf LAMMPS job for ({}) concurrent tasks "
                             "using a total of ({}) cpus per tasks "
                             "with ({}) memory "
                             "with states ({}) "
                             "run for ({}) "
                             "in partition ({})."
                             ).format(dft_dict['job_name'],
                                      dft_dict['ntasks'],
                                      dft_dict['cpus_per_task'],
                                      dft_dict['mem'],
                                      " ".join(runstates),
                                      dft_dict['walltime'],
                                      dft_dict['partition'],
                                      )
        if not query_yes_no(check_info_string):
            return 1

        create_lammps_snp_job(seeds, states, **dft_dict)

    elif dft_dict['supercomputer_name'] == 'dogwood':
        # Set up a dogwood submission script to go through the debug queue
        dft_dict['job_name'] = "lammps_dog"
        dft_dict['partition'] = "debug_queue"
        #dft_dict['ntasks'] = "1"
        #dft_dict['cpus_per_task'] = "8"
        dft_dict['mem'] = "8G"
        dft_dict['walltime'] = "01:00:00"

        string_query('Input job name', 'job_name', dft_dict)
        string_query('Input partition', 'partition', dft_dict)
        #string_query('Input the number of tasks at a time', 'ntasks', dft_dict)
        #string_query('Input how many cpus per task', 'cpus_per_task', dft_dict)
        string_query('Input how much memory', 'mem', dft_dict)
        string_query('Input walltime (dd:hh:mm:ss)', 'walltime', dft_dict)

        check_info_string = ("Generating ({}) dogwood LAMMPS job "
                             "with ({}) memory "
                             "with states ({}) "
                             "run for ({}) "
                             "in partition ({})."
                             ).format(dft_dict['job_name'],
                                      dft_dict['mem'],
                                      " ".join(runstates),
                                      dft_dict['walltime'],
                                      dft_dict['partition'],
                                      )
        if not query_yes_no(check_info_string):
            return 1

        create_lammps_dogwood_job(seeds, states, **dft_dict)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Arguments are the simulation directories to be run
        ChiLaunch(simdirs=sys.argv[1:], opts='')
    else:
        print("must supply directory argument")
