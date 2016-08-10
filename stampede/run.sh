#!/bin/bash

set -u

BIN=$( cd "$( dirname "$0" )" && pwd )
QUERY_DIR=""
OUT_DIR=$BIN
INDEX="b_compressed+h+v"

function lc() {
  wc -l "$1" | cut -d ' ' -f 1
}

function HELP() {
  printf "Usage:\n  %s -q QUERY_DIR -o OUT_DIR\n\n" $(basename $0)

  echo "Required arguments:"
  echo " -q QUERY_DIR"
  echo " -o OUT_DIR"
  echo ""
  echo "Options:"
  echo " -i INDEX ($INDEX)"
  echo ""
  exit 0
}

if [[ $# -eq 0 ]]; then
  HELP
fi

while getopts :i:o:q:h OPT; do
  case $OPT in
    h)
      HELP
      ;;
    i)
      INDEX="$OPTARG"
      ;;
    o)
      OUT_DIR="$OPTARG"
      ;;
    q)
      QUERY_DIR="$OPTARG"
      ;;
    :)
      echo "Error: Option -$OPTARG requires an argument."
      exit 1
      ;;
    \?)
      echo "Error: Invalid option: -${OPTARG:-""}"
      exit 1
  esac
done

if [[ ! -d $QUERY_DIR ]]; then
  echo QUERY_DIR \"$QUERY_DIR\" does not exist.
  exit 1
fi

if [[ ! -d $OUT_DIR ]]; then
  mkdir -p "$OUT_DIR"
fi

#
# Convert BAM files to FASTA if necessary
#
BAM_FILES=$(mktemp)
find "$QUERY_DIR" -name \*.bam > "$BAM_FILES"
NUM_BAM=$(lc "$BAM_FILES")

if [[ $NUM_BAM -gt 0 ]]; then
  while read BAM_FILE; do
    BASENAME=$(basename $BAM_FILE '.bam')
    FASTA="$QUERY_DIR/${BASENAME}.fa"

    if [[ ! -s $FASTA ]]; then
      echo "Converting BAM_FILE \"$BASENAME\""
      samtools fasta -0 "$FASTA" "$BAM_FILE"
    fi
  done < $BAM_FILES
fi
rm "$BAM_FILES"

CENTRIFUGE="$WORK/tools/centrifuge-1.0.2-beta/centrifuge"

if [[ ! -e $CENTRIFUGE ]]; then
  echo "Cannot find CENTRIFUGE binary \"$CENTRIFUGE\""
  exit 1
fi

export CENTRIFUGE_INDEXES="$SCRATCH/centrifuge-indexes/$INDEX"

if [[ -d "$CENTRIFUGE_INDEXES" ]]; then
  echo "Running samples to CENTRIFUGE_INDEXES \"$CENTRIFUGE_INDEXES\""
else
  echo "CENTRIFUGE_INDEXES directory \"$CENTRIFUGE_INDEXES\" does not exist."
  exit 1
fi

if [[ ! -d "$OUT_DIR" ]]; then
  mkdir -p "$OUT_DIR"
fi

FILES_LIST=$(mktemp)
find "$QUERY_DIR" -type f -size +0c -not -name \*.bam > "$FILES_LIST"
#find "$QUERY_DIR" -name \*.fa > "$FILES_LIST"
NUM_FILES=$(lc $FILES_LIST)

echo "NUM_FILES \"$NUM_FILES\" to process"

PARAM="$$.param"

if [[ -e $PARAM ]]; then
  rm $PARAM
fi

i=0
while read FILE; do
  BASENAME=$(basename $FILE)
  let i++
  printf "%3d: %s\n" $i $BASENAME
  $CENTRIFUGE -f -x "$INDEX" -U "$FILE" -S "$OUT_DIR/$BASENAME.sum" --report-file "$OUT_DIR/$BASENAME.tsv" 
#  echo $CENTRIFUGE -f -x "$INDEX" -U "$FILE" -S "$OUT_DIR/$BASENAME.sum" --report-file "$OUT_DIR/$BASENAME.tsv" >> $PARAM
done < $FILES_LIST

#echo "Starting parallel job... $(date)"
#export LAUNCHER_DIR=$HOME/src/launcher
#export LAUNCHER_PPN=4
#export LAUNCHER_WORKDIR=$OUT_DIR
#time $LAUNCHER_DIR/paramrun SLURM $LAUNCHER_DIR/init_launcher $LAUNCHER_WORKDIR $PARAM
#echo "Finished parallel $(date)"
#rm $PARAM

echo "Done, look in OUT_DIR \"$OUT_DIR\""
