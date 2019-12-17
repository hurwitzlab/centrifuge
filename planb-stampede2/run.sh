#!/bin/bash

module load tacc-singularity

IMG="$PLANB_JOBPATH/planb-stampede2/centrifuge-1.0.4.img"
OUT_DIR="$PLANB_JOBPATH/data/centrifuge-out"
INDEX_DIR="/work/05066/imicrobe/iplantc.org/data/centrifuge-indexes"
RUN_CENTRIFUGE="singularity exec -B $PLANB_JOBPATH:$PLANB_JOBPATH -B /work:/work $IMG run_centrifuge.py"

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
