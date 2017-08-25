#!/bin/bash

#  Usage:
#    run.sh -d IN_DIR
#  
#  Usage:
#    run.sh -a FASTA
#  
#  Usage:
#    run.sh -f FASTA_r1 -r FASTA_r2 [-s SINGLETONS]
#  
#  Required arguments:
#   -d IN_DIR (single-only)
#  
#  OR
#   -a FASTA (single)
#  
#  OR
#   -f FASTA_r1 (forward)
#   -r FASTA_r2 (reverse)
#  
#  Options:
#   -i INDEX (p_compressed+h+v)
#   -o OUT_DIR (/work/03137/kyclark/centrifuge-0.0.1/stampede/centrifuge-out)
#   -s SINGLETONS
#   -k SKIP_EXISTING (0)

set -u

#	./submit.sh $(WORK)/pam-morris/fasta $(WORK)/pam-morris/centrifuge 'p_compressed+h+v' normal 24:00:00

IN_DIR=$1
OUT_DIR=$2
DB=${3:-p_compressed+h+b}
QUEUE=${4:-normal}
TIME=${5:-24:00:00}

if [[ $# -lt 2 ]]; then
  printf "  Usage: %s IN_DIR OUT_DIR [DB QUEUE TIME]\n" "$(basename "$0")"
  exit 1
fi

sbatch -A iPlant-Collabs -N 1 -n 1 -t "$TIME" -p "$QUEUE" -J cntrfge run.sh -d "$IN_DIR" -o "$OUT_DIR" -i "$DB"
