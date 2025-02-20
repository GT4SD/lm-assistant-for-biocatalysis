#!/bin/bash

# Input parameters
INPUT_FILE=$1
NVT_DIR=$2
MDP_FILE=$3

# GROMACS executable
GMX=$4

# Get the current directory
CURRENT_DIR=$(pwd)

# Change to NVT equilibration directory
cd $NVT_DIR

# Step 1: Copy necessary files from the Energy Minimization phase
cp ../minimization/minimization.gro .
cp ../minimization/topol.top .

# Step 2: Prepare the system for NVT equilibration
$GMX grompp -f $MDP_FILE -c minimization.gro -p topol.top -o nvt.tpr -maxwarn 2

# Step 3: Run the NVT equilibration
$GMX mdrun -v -deffnm nvt 

# Return to the original directory
cd $CURRENT_DIR