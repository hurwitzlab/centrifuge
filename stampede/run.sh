#!/bin/bash

# Author: Ken Youens-Clark <kyclark@email.arizona.edu>

set -u

#
# Set up defaults for inputs, constants
#
BIN=$( cd "$( dirname "$0" )" && pwd )
IN_DIR=""
MODE="single"
FASTA=""
FORWARD=""
REVERSE=""
SINGLETONS=""
INDEX="p_compressed+h+v"
OUT_DIR="$BIN/centrifuge-out"
CENTRIFUGE_DIR="$WORK/tools/centrifuge-1.0.3-beta"
INDEX_DIR="$WORK/centrifuge-indexes"
MAX_SEQS_PER_FILE=100000
SKIP_EXISTING=0

#
# Some needed functions
#
function lc() { 
  # "line count"
  wc -l "$1" | cut -d ' ' -f 1
}

function HELP() {
  printf "Usage:\n  %s -d IN_DIR\n\n" "$(basename "$0")"
  printf "Usage:\n  %s -a FASTA\n\n" "$(basename "$0")"
  printf "Usage:\n  %s -f FASTA_r1 -r FASTA_r2 [-s SINGLETONS]\n\n" \
    "$(basename "$0")"

  echo "Required arguments:"
  echo " -d IN_DIR (single-only)"
  echo ""
  echo "OR"
  echo " -a FASTA (single)"
  echo ""
  echo "OR"
  echo " -f FASTA_r1 (forward)"
  echo " -r FASTA_r2 (reverse)"
  echo ""
  echo "Options:"
  echo " -i INDEX ($INDEX)"
  echo " -o OUT_DIR ($OUT_DIR)"
  echo " -s SINGLETONS"
  echo " -k SKIP_EXISTING ($SKIP_EXISTING)"
  echo ""
  exit 0
}

#
# Show HELP if no arguments
#
[[ $# -eq 0 ]] && HELP

while getopts :a:d:i:f:k:m:o:r:s:h OPT; do
  case $OPT in
    a)
      FASTA="$OPTARG"
      ;;
    d)
      IN_DIR="$OPTARG"
      ;;
    h)
      HELP
      ;;
    i)
      INDEX="$OPTARG"
      ;;
    f)
      FORWARD="$OPTARG"
      ;;
    k)
      SKIP_EXISTING=1
      ;;
    m)
      MODE="$OPTARG"
      ;;
    o)
      OUT_DIR="$OPTARG"
      ;;
    r)
      REVERSE="$OPTARG"
      ;;
    s)
      SINGLETONS="$OPTARG"
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

#
# Set up PATH, "bin" directory
#
if [[ -d $CENTRIFUGE_DIR ]]; then
  PATH="$CENTRIFUGE_DIR:$PATH"
else
  echo "Cannot find CENTRIFUGE_DIR \"$CENTRIFUGE_DIR\""
  exit 1
fi

SCRIPTS="scripts.tgz"
if [[ -e $SCRIPTS ]]; then
  echo "Untarring $SCRIPTS to bin"
  if [[ ! -d bin ]]; then
    mkdir bin
  fi
  tar -C bin -xvf $SCRIPTS
  PATH="$(PWD)/bin:$PATH"
fi

export PATH

echo "PWD = $(PWD)"
echo "BIN = $BIN"
echo "WHAT'S IN \"$BIN\""
find "$BIN"

#
# Verify existence of INDEX_DIR, chosen INDEX
#
if [[ ! -d $INDEX_DIR ]]; then
  echo "Cannot find INDEX_DIR \"$INDEX_DIR\""
  exit 1
fi

NUM=$(find "$INDEX_DIR" -name $INDEX.\*.cf | wc -l | awk '{print $1}')

if [[ $NUM -gt 0 ]]; then
  echo "Using INDEX \"$INDEX\""
else
  echo "Cannot find INDEX \"$INDEX\""
  echo "Please choose from the following:"
  find "$INDEX_DIR" -name \*.cf -exec basename {} \; | sed "s/\.[0-9]\.cf//" | sort | uniq | cat -n
  exit 1
fi

#
# Verify existence of various directories
#
[[ ! -d $OUT_DIR ]] && mkdir -p "$OUT_DIR"


REPORT_DIR="$OUT_DIR/reports"
[[ ! -d "$REPORT_DIR" ]] && mkdir -p "$REPORT_DIR"

PLOT_DIR="$OUT_DIR/plots"
[[ ! -d "$PLOT_DIR" ]] && mkdir -p "$PLOT_DIR"

#
# Create, null-out command file for running Centrifuge
#
CENT_PARAM="$PWD/$$.centrifuge.param"
cat /dev/null > "$CENT_PARAM"

#
# A single FASTA
#
if [[ ! -z $FASTA ]]; then
  BASENAME=$(basename "$FASTA")
  echo "Will process single FASTA \"$BASENAME\""
  echo "CENTRIFUGE_INDEXES=$INDEX_DIR centrifuge -f -x \"$INDEX\" -U \"$FASTA\" -S \"$REPORT_DIR/$BASENAME.sum\" --report-file \"$REPORT_DIR/$BASENAME.tsv\"" > "$CENT_PARAM"

#
# Paired-end FASTA reads
#
elif [[ ! -z $FORWARD ]] && [[ ! -z $REVERSE ]]; then
  BASENAME=$(basename "$FORWARD")
  echo "Will process FORWARD \"$FORWARD\" REVERSE \"$REVERSE\""
  S=""
  if [[ ! -z $SINGLETONS ]]; then
    S="-U \"$SINGLETONS\""
  fi
  echo "CENTRIFUGE_INDEXES=$INDEX_DIR centrifuge -f -x \"$INDEX\" -1 \"$FORWARD\" -2 \"$REVERSE\" $S -S \"$REPORT_DIR/$BASENAME.sum\" --report-file \"$REPORT_DIR/$BASENAME.tsv\"" > "$CENT_PARAM"

#
# A directory of single FASTA files
#
elif [[ ! -z $IN_DIR ]] && [[ -d $IN_DIR ]]; then
  if [[ $MODE == 'single' ]]; then
    SPLIT_DIR="$OUT_DIR/split"
    [[ ! -d "$SPLIT_DIR" ]] && mkdir -p "$SPLIT_DIR"

    INPUT_FILES=$(mktemp)
    find "$IN_DIR" -type f -size +0c > "$INPUT_FILES"

    while read -r FILE; do
      fasplit.py -f "$FILE" -o "$SPLIT_DIR/$(basename "$FILE")" -n "$MAX_SEQS_PER_FILE"
    done < "$INPUT_FILES"

    SPLIT_FILES=$(mktemp)
    find "$SPLIT_DIR" -type f -size +0c > "$SPLIT_FILES"
    while read -r FILE; do
      BASENAME=$(basename "$FILE")
      SUM_FILE="$REPORT_DIR/$BASENAME.sum"

      if [[ "$SKIP_EXISTING" -gt 0 ]] && [[ -s "$SUM_FILE" ]]; then
        echo "Skipping $BASENAME (sum file exists)"
      else
        echo "CENTRIFUGE_INDEXES=$INDEX_DIR centrifuge -f -x $INDEX -U $FILE -S $REPORT_DIR/$BASENAME.sum --report-file $REPORT_DIR/$BASENAME.tsv" >> "$CENT_PARAM"
      fi
    done < "$SPLIT_FILES"

    rm "$INPUT_FILES"
    rm "$SPLIT_FILES"
    #rm -rf "$SPLIT_DIR"
  else
    echo "Can't yet run IN_DIR with 'paired' mode"
    exit 1
  fi

#
# Else "error"
#
else
  echo "Must have -d IN_DIR/-a FASTA/-f FORWARD & -r REVERSE [-s SINGLETON]"
  exit 1
fi

#
# Pass Centrifuge run to LAUNCHER
# Run "interleaved" to ensure this finishes before bubble
#
echo "Running NJOBS \"$(lc "$CENT_PARAM")\" for Centrifuge \"$CENT_PARAM\""
export LAUNCHER_DIR="$HOME/src/launcher"
export LAUNCHER_PLUGIN_DIR="$LAUNCHER_DIR/plugins"
export LAUNCHER_WORKDIR="$BIN"
export LAUNCHER_JOB_FILE="$CENT_PARAM"
export LAUNCHER_RMI=SLURM
export LAUNCHER_SCHED=interleaved
"$LAUNCHER_DIR/paramrun"
echo "Finished Centrifuge"

#
# so that it will be run /after/ Centrifuge has finished
#
BUBBLE_PARAM="$PWD/$$.bubble.param"
echo "centrifuge_bubble.r --dir \"$REPORT_DIR\" --outdir \"$PLOT_DIR\" --outfile bubble --title centrifuge" > "$BUBBLE_PARAM"
#export LAUNCHER_NJOBS=1
export LAUNCHER_JOB_FILE="$BUBBLE_PARAM"
echo "Starting bubble"
"$LAUNCHER_DIR/paramrun"
echo "Finished bubble"

#
# Clean up
#
#[[ -d bin ]] && rm -rf bin

echo "Done, look in OUT_DIR \"$OUT_DIR\""
echo "Comments to Ken Youens-Clark <kyclark@email.arizona.edu>"
