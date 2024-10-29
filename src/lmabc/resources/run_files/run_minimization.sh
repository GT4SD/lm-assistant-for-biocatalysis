#!/bin/bash

# Input parameters
INPUT_FILE=$1
MINIMIZATION_DIR=$2
MDP_FILE=$3

# Get the current directory
CURRENT_DIR=$(pwd)

# GROMACS executable
GMX=gmx

# Change to minimization directory
cd $MINIMIZATION_DIR

# Step 1: Prepare the system with pdb2gmx
cp $INPUT_FILE .

$GMX pdb2gmx -f $INPUT_FILE -o processed.gro -water spce <<-EOF
15
EOF

# Step 2: Define the box
$GMX editconf -f processed.gro -o boxed.gro -c -d 1.0 -bt cubic

# Step 3: Add solvent
$GMX solvate -cp boxed.gro -cs spc216 -o solvated.gro -p topol.top

# Step 4: Prepare for ion addition
$GMX grompp -f $MDP_FILE -c solvated.gro -p topol.top -o ions.tpr -maxwarn 2

# Step 5: Add ions (neutralize system)
$GMX genion -s ions.tpr -o solvated_ions.gro -p topol.top -pname NA -nname CL -neutral <<-EOF
13
EOF

# Step 6: Energy minimization
NAME="minimization"
$GMX grompp -f $MDP_FILE -c solvated_ions.gro -p topol.top -o ${NAME}.tpr -maxwarn 2
$GMX mdrun -v -deffnm ${NAME}

# Return to the original directory
cd $CURRENT_DIR