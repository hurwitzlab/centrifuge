#!/bin/bash

#SBATCH -J cntrfge 
#SBATCH -A iPlant-Collabs 
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00
#SBATCH -p skx-normal

# Author: Ken Youens-Clark <kyclark@email.arizona.edu>

module load tacc-singularity 

set -u

OUT_DIR="$PWD/centrifuge-out"
INDEX_DIR="/work/05066/imicrobe/iplantc.org/data/centrifuge-indexes"
IMG="/work/05066/imicrobe/singularity/centrifuge-1.0.4.img"
RUN_CENTRIFUGE="singularity exec $IMG run_centrifuge.py"

if [[ ! -e "$IMG" ]]; then
    echo "Missing IMG \"$IMG\""
    exit 1
fi

#
# Show HELP if no arguments
#
[[ $# -eq 0 ]] && $RUN_CENTRIFUGE -h

#
# Verify existence of INDEX_DIR, chosen INDEX
#
if [[ ! -d "$INDEX_DIR" ]]; then
    echo "Cannot find INDEX_DIR \"$INDEX_DIR\""
    exit 1
fi

$RUN_CENTRIFUGE -I "$INDEX_DIR" "$@"
