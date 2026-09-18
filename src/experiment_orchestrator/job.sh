#!/bin/bash
#SBATCH -A hpc2n2026-126 
#SBATCH -t 00:20:00       # wall time - change as you need 
#SBATCH -n 4              # Change number of tasks as you want 
#SBATCH -o output_%j.out  # output file
#SBATCH -e error_%j.err   # error messages

ml purge > /dev/null 2>&1 # Clean the module environment  
module load GCC/13.2.0 OpenMPI/4.1.6 
module load mpi4py/3.1.5 
module load PyYAML/6.0.1

mpirun -n 4 python launcher.py

