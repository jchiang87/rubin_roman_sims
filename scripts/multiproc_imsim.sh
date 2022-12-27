#!/bin/bash

num_tranche=$1
tranche=$2
source /pscratch/sd/j/jchiang8/imSim/AY2022_sims/setup_shifter.sh
python ./multiproc_imsim.py $num_tranche $tranche
