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