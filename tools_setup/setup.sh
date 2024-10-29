#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

RUN_MC_SETUP=true
[ "$1" = "--skip-mc" ] && RUN_MC_SETUP=false

LMABC_LOCAL_CACHE_PATH="${LMABC_LOCAL_CACHE_PATH:-$HOME/.lmabc/}"
RXNAAMAPPER_CACHE_DIR="${LMABC_LOCAL_CACHE_PATH}rxnaamapper"
ENZYME_OPTIMIZATION_CACHE_DIR="${LMABC_LOCAL_CACHE_PATH}enzyme_optimization/models"
MOLECULAR_DYNAMICS_MDP_CACHE_DIR="${LMABC_LOCAL_CACHE_PATH}molecular_dynamics/mdp_files"
MOLECULAR_DYNAMICS_RUN_CACHE_DIR="${LMABC_LOCAL_CACHE_PATH}molecular_dynamics/run_files"

print_header "Setting up MD simulations MDP files"
mkdir -p "$MOLECULAR_DYNAMICS_MDP_CACHE_DIR"
cp src/lmabc/resources/mdp_files/{minimization.mdp,nvt.mdp,npt.mdp} "$MOLECULAR_DYNAMICS_MDP_CACHE_DIR/"
echo "MDP files instantiated"

mkdir -p "$MOLECULAR_DYNAMICS_RUN_CACHE_DIR"
cp src/lmabc/resources/run_files/{run_minimization.sh,run_nvt.sh,run_npt.sh} "$MOLECULAR_DYNAMICS_RUN_CACHE_DIR/"
echo "MD run files instantiated"

mkdir -p "$RXNAAMAPPER_CACHE_DIR"
print_header "Setting up RXNAAMapper"
TEMP_DIR=$(mktemp -d)
REPO_URL="https://github.com/rxn4chemistry/rxnaamapper.git"

echo "Cloning rxnaamapper repository..."
git clone "$REPO_URL" "$TEMP_DIR"

echo "Moving tokenizer and vocabulary files..."
mv "$TEMP_DIR/examples/token_75K_min_600_max_750_500K.json" "$RXNAAMAPPER_CACHE_DIR/tokenizer.json"
mv "$TEMP_DIR/examples/vocabulary_token_75K_min_600_max_750_500K.txt" "$RXNAAMAPPER_CACHE_DIR/vocabulary.txt"

echo "Running Python setup script..."
python tools_setup/rxn_aa_mapper_model_download.py

echo "Cleaning up temporary directory..."
rm -rf "$TEMP_DIR"

if $RUN_MC_SETUP; then
    print_header "Setting up Enzeptional"
    echo "Installing Minio Client (mc)..."
    brew install minio/stable/mc

    echo "Configuring Minio Client..."
    mc alias set gt4sd-public-cos https://s3.par01.cloud-object-storage.appdomain.cloud \
        6e9891531d724da89997575a65f4592e 5997d63c4002cc04e13c03dc0c2db9dae751293dab106ac5

    echo "Mirroring kcat scorers..."
    mc mirror --overwrite gt4sd-public-cos/gt4sd-cos-properties-artifacts/proteins/enzeptional/scorers/kcat/ \
        "$ENZYME_OPTIMIZATION_CACHE_DIR/kcat/"

    echo "Mirroring feasibility scorers..."
    mc mirror --overwrite gt4sd-public-cos/gt4sd-cos-properties-artifacts/proteins/enzeptional/scorers/feasibility/ \
        "$ENZYME_OPTIMIZATION_CACHE_DIR/feasibility/"
else
    print_header "Skipping Enzeptional setup"
    echo "Minio Client (mc) setup has been skipped. Please set up Enzeptional manually if needed."
fi

echo -e "\n${GREEN}Setup completed successfully!${NC}\n"
