Install Documentation

# Pando
PyYaml:
1. Make sure that you have the latest version of python 2.7 loaded in modules
    Module load python2.7.11
2. Create .local directory in $HOME to put site-package. (~/.local is the default local directory for python
    mkdir ~/.local
3. Install PyYaml in the user local directory ($HOME/.local/) with easy_install
    easy_install --prefix=$HOME/.local pyyaml

Numpy:
1. Use module command to load latest version of numpy (put this in your .my.bashrc file)
    module load numpy_1.11.0
2. Numpy might be upgraded so newer version could exist. View these using
    module avail numpy

# Janus
PyYaml:
1. Make sure that you have the latest version of python 2.7 loaded in modules
    Module load python2.7.10
2. Upgrade to the latest version of pip
    pip install --user --upgrade pip
3. Install PyYaml in the user local directory ($HOME/.local/) using the --user command 
    pip install --user pyymal
Numpy:
1. Use module command to load latest version of numpy (put this in your .my.bashrc file)
    module load numpy_1.9.2 
2. Numpy might be upgraded so newer version could exist. View these using
    module spider numpy
