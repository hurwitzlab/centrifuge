#!/bin/bash

set -u

if [[ $# -lt 2 ]]; then
    printf "  Usage: %s IN_DIR OUT_DIR [EXCLUDE DB QUEUE TIME]\n" "$(basename "$0")"
    exit 1
fi

IN_DIR=$1
OUT_DIR=$2
DB=${3:-p_compressed+h+b}
EXCLUDE=${4:-""}
QUEUE=${5:-normal}
TIME=${6:-24:00:00}

EX_ARG=""
[[ -n "$EXCLUDE" ]] && EX_ARG="-x $EXCLUDE"

sbatch -A iPlant-Collabs -N 2 -n 2 -t "$TIME" -p "$QUEUE" -J cntrfge \
    run.sh -d "$IN_DIR" -o "$OUT_DIR" -i "$DB" "$EX_ARG" -k
