#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

ORIG_DIR=$(pwd)
BLASTDB_ARG="swissprot"
FORCE_REINSTALL=false
RUN_MC_SETUP=true

usage() {
    echo "Usage: $0 [--skip-mc] [--reinstall] [--blastdb <db_name|all>]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-mc)
            RUN_MC_SETUP=false
            shift
            ;;
        --reinstall)
            FORCE_REINSTALL=true
            shift
            ;;
        --blastdb)
            if [[ $# -lt 2 ]]; then
                echo "Error: --blastdb requires an argument." >&2
                usage
            fi
            BLASTDB_ARG="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage
            ;;
        *)
            shift
            ;;
    esac
done

print_header() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

LMABC_BASE_DIR="${LMABC_BASE_DIR:-$HOME/.lmabc/}"
RXNAAMAPPER_BASE_DIR="${LMABC_BASE_DIR}/rxnaamapper"
ENZYME_OPTIMIZATION_BASE_DIR="${LMABC_BASE_DIR}/enzyme_optimization/models"
MOLECULAR_DYNAMICS_MDP_BASE_DIR="${LMABC_BASE_DIR}/molecular_dynamics/mdp_files"
MOLECULAR_DYNAMICS_RUN_BASE_DIR="${LMABC_BASE_DIR}/molecular_dynamics/run_files"
BLAST_INSTALL_DIR="${LMABC_BASE_DIR}/blast"
BLASTDB_DIR="${BLAST_INSTALL_DIR}/blastdb"
BLAST_VERSION="2.16.0"
BLAST_ARCHIVE="ncbi-blast-${BLAST_VERSION}+-x64-linux.tar.gz"
BLAST_DOWNLOAD_URL="https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/${BLAST_ARCHIVE}"

if $FORCE_REINSTALL; then
    rm -rf "$MOLECULAR_DYNAMICS_MDP_BASE_DIR" \
           "$MOLECULAR_DYNAMICS_RUN_BASE_DIR" \
           "$RXNAAMAPPER_BASE_DIR" \
           "${BLAST_INSTALL_DIR}/ncbi-blast-${BLAST_VERSION}+"
fi

mkdir -p "$MOLECULAR_DYNAMICS_MDP_BASE_DIR" \
         "$MOLECULAR_DYNAMICS_RUN_BASE_DIR" \
         "$RXNAAMAPPER_BASE_DIR" \
         "$BLAST_INSTALL_DIR" \
         "$BLASTDB_DIR"

print_header "Setting up MD simulations"
if [ ! -f "${MOLECULAR_DYNAMICS_MDP_BASE_DIR}/minimization.mdp" ]; then
    cp src/lmabc/resources/mdp_files/{minimization.mdp,nvt.mdp,npt.mdp} "$MOLECULAR_DYNAMICS_MDP_BASE_DIR/"
    echo "MDP files instantiated"
else
    echo "MD simulation MDP files already set up, skipping"
fi

if [ ! -f "${MOLECULAR_DYNAMICS_RUN_BASE_DIR}/run_minimization.sh" ]; then
    cp src/lmabc/resources/run_files/{run_minimization.sh,run_nvt.sh,run_npt.sh} "$MOLECULAR_DYNAMICS_RUN_BASE_DIR/"
    echo "MD run files instantiated"
else
    echo "MD simulation run files already set up, skipping"
fi

print_header "Setting up RXNAAMapper"
if [ ! -f "${RXNAAMAPPER_BASE_DIR}/tokenizer.json" ]; then
    TEMP_DIR=$(mktemp -d)
    REPO_URL="https://github.com/rxn4chemistry/rxnaamapper.git"
    git clone "$REPO_URL" "$TEMP_DIR"
    mv "$TEMP_DIR/examples/token_75K_min_600_max_750_500K.json" "${RXNAAMAPPER_BASE_DIR}/tokenizer.json"
    mv "$TEMP_DIR/examples/vocabulary_token_75K_min_600_max_750_500K.txt" "${RXNAAMAPPER_BASE_DIR}/vocabulary.txt"
    python tools_setup/rxn_aa_mapper_model_download.py "${RXNAAMAPPER_BASE_DIR}"
    rm -rf "$TEMP_DIR"
else
    echo "RXNAAMapper already set up, skipping"
fi

if $RUN_MC_SETUP; then
    print_header "Setting up Enzeptional"
    if ! command -v mc >/dev/null || $FORCE_REINSTALL; then
        brew install minio/stable/mc
    else
        echo "Minio Client (mc) is already installed, skipping installation"
    fi
    mc alias set gt4sd-public-cos https://s3.par01.cloud-object-storage.appdomain.cloud b087e6810a5d4246a64e07e36ace338f ba4a1db5647a32c6109b58714befb7ea7145b983143e0836
    if [ ! -d "${ENZYME_OPTIMIZATION_BASE_DIR}/kcat" ] || [ -z "$(ls -A "${ENZYME_OPTIMIZATION_BASE_DIR}/kcat")" ]; then
        mc mirror --overwrite gt4sd-public-cos/gt4sd-cos-properties-artifacts/proteins/enzeptional/scorers/kcat/ "${ENZYME_OPTIMIZATION_BASE_DIR}/kcat/"
    else
        echo "kcat scorers already mirrored, skipping"
    fi
    if [ ! -d "${ENZYME_OPTIMIZATION_BASE_DIR}/feasibility" ] || [ -z "$(ls -A "${ENZYME_OPTIMIZATION_BASE_DIR}/feasibility")" ]; then
        mc mirror --overwrite gt4sd-public-cos/gt4sd-cos-properties-artifacts/proteins/enzeptional/scorers/feasibility/ "${ENZYME_OPTIMIZATION_BASE_DIR}/feasibility/"
    else
        echo "feasibility scorers already mirrored, skipping"
    fi
else
    print_header "Skipping Enzeptional setup"
    echo "Minio Client (mc) setup has been skipped. Please set up Enzeptional manually if needed."
fi

print_header "Setting up BLAST+ installation"
if [ ! -d "${BLAST_INSTALL_DIR}/ncbi-blast-${BLAST_VERSION}+/bin" ]; then
    if [ ! -f "${BLAST_INSTALL_DIR}/${BLAST_ARCHIVE}" ]; then
        wget -O "${BLAST_INSTALL_DIR}/${BLAST_ARCHIVE}" "${BLAST_DOWNLOAD_URL}"
    fi
    tar -zxvpf "${BLAST_INSTALL_DIR}/${BLAST_ARCHIVE}" -C "$BLAST_INSTALL_DIR"
    echo "BLAST+ installed in ${BLAST_INSTALL_DIR}"
else
    echo "BLAST+ is already installed in ${BLAST_INSTALL_DIR}."
fi

print_header "Configuring BLAST+ environment"
echo "Please add the following lines to your shell profile (e.g., .bash_profile or .zshrc):"
echo "export PATH=\$PATH:${BLAST_INSTALL_DIR}/ncbi-blast-${BLAST_VERSION}+/bin"
echo "export BLASTDB=${BLASTDB_DIR}"

print_header "Downloading BLAST databases"
export BLASTDB="${BLASTDB_DIR}"
cd "${BLASTDB_DIR}"

download_db() {
    local db_name="$1"
    if [ ! -f "${BLASTDB_DIR}/${db_name}.nsq" ]; then
        echo "Downloading BLAST database: ${db_name}"
        perl "${BLAST_INSTALL_DIR}/ncbi-blast-${BLAST_VERSION}+/bin/update_blastdb.pl" --passive --decompress "$db_name"
    else
        echo "BLAST database ${db_name} already exists, skipping"
    fi
}

if [[ "${BLASTDB_ARG}" == "all" ]]; then
    databases=("swissprot" "nr" "nt" "refseq_protein" "refseq_rna" "pdb")
    for db in "${databases[@]}"; do
        download_db "$db"
    done
else
    download_db "${BLASTDB_ARG}"
fi

cd "$ORIG_DIR"
echo -e "\n${GREEN}Setup completed successfully!${NC}\n"
