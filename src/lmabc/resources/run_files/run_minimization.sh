#!/bin/bash
##
## MIT License
##
## Copyright (c) 2025 GT4SD team
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.##


# Input parameters
INPUT_FILE=$1
MINIMIZATION_DIR=$2
MDP_FILE=$3

# GROMACS executable
GMX=$4

# Get the current directory
CURRENT_DIR=$(pwd)

# Change to minimization directory
cd $MINIMIZATION_DIR

# Step 1: Prepare the system with pdb2gmx
cp $INPUT_FILE .

$GMX pdb2gmx -f $INPUT_FILE -o processed.gro -water spce -ignh <<-EOF
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