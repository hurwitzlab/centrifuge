#!/bin/bash

if [[ $# -lt 2 ]]; then
  printf "Usage: %s QUERY_DIR OUT_DIR\n" $(basename $0)
  exit 1
fi

#TIME=02:00:00
#PARTITION=development
QUERY_DIR=$1
OUT_DIR=$2
INDEX=${3:-b_compressed+h+v}
PARTITION=${4-development}
TIME=04:00:00
JOB_NAME=centrifuge

sbatch -A iPlant-Collabs -N 1 -n 4 -t $TIME -p $PARTITION -J $JOB_NAME --mail-type BEGIN,END,FAIL --mail-user kyclark@email.arizona.edu run.sh -q $QUERY_DIR -o $OUT_DIR -i $INDEX
