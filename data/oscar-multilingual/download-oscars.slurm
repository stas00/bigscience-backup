#!/bin/bash
#SBATCH --job-name=download-oscars    # job name
#SBATCH --ntasks=1                   # number of MP tasks
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40           # number of cores per tasks
#SBATCH --hint=nomultithread         # we get physical cores not logical
#SBATCH --time=20:00:00             # maximum execution time (HH:MM:SS)
#SBATCH --output=%x-%j.out           # output file name
#SBATCH --account=six@cpu
#SBATCH --partition=compil

set -x -e

source $six_ALL_CCFRWORK/start-prod

# use SCRATCH for building as it's much faster
cd $six_ALL_CCFRSCRATCH/datasets/oscar-multilingual
python $SCRATCH/bigscience/data/oscar-multilingual/download-oscars.py
