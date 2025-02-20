#!/bin/bash

# Input parameters
INPUT_FILE=$1
NPT_DIR=$2
MDP_FILE=$3

# GROMACS executable
GMX=$4

# Get the current directory
CURRENT_DIR=$(pwd)

# Change to NPT equilibration directory
cd $NPT_DIR

# Step 1: Copy necessary files from the Energy nvt phase
cp ../nvt/nvt.gro .
cp ../nvt/topol.top .

# Step 2: Prepare the system for NPT equilibration
NAME="npt"
$GMX grompp -f $MDP_FILE -c nvt.gro -p topol.top -o npt.tpr -maxwarn 2

# Step 3: Run the NPT equilibration
$GMX mdrun -v -deffnm npt

# Return to the original directory
cd $CURRENT_DIR