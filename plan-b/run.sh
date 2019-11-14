#!/bin/bash

set -u

CWD=$(dirname "$0")
IMG="$CWD/centrifuge-1.0.4.img"
OUT_DIR="$(dirname $CWD)/data/centrifuge-out"
INDEX_DIR="/data/centrifuge-indexes"
RUN_CENTRIFUGE="singularity exec -B /data:/data $IMG run_centrifuge.py"

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

$RUN_CENTRIFUGE -I "$INDEX_DIR" -o "$OUT_DIR" "$@"
