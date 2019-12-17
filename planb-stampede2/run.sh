#!/bin/bash

#SBATCH -A iPlant-Collabs
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 24:00:00
#SBATCH -p skx-normal

if [[ -z "$JOBID" ]]; then
    echo "Error: missing JOBID"
    exit 1
fi

module load tacc-singularity

IMG="/work/04848/mbomhoff/stampede2/plan-b/$JOBID/plan-b_stampede2/centrifuge-1.0.4.img"
OUT_DIR="/work/04848/mbomhoff/stampede2/plan-b/$JOBID/data/centrifuge-out"
INDEX_DIR="/work/05066/imicrobe/iplantc.org/data/centrifuge-indexes"
RUN_CENTRIFUGE="singularity exec -B /work:/work $IMG run_centrifuge.py"

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

$RUN_CENTRIFUGE -I $INDEX_DIR -o $OUT_DIR "$@"
