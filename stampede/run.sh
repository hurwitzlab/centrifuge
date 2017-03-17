#!/bin/bash

set -u

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

#
# Set up PATH
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
fi

if [[ -e "$BIN/bin" ]]; then
  PATH="$BIN/bin:$PATH"
fi

export PATH

if [[ ! -d $INDEX_DIR ]]; then
  echo "Cannot find INDEX_DIR \"$INDEX_DIR\""
  exit 1
fi

function lc() {
  wc -l "$1" | cut -d ' ' -f 1
}

function HELP() {
  printf "Usage:\n  %s -d IN_DIR\n\n" $(basename $0)
  printf "Usage:\n  %s -a FASTA\n\n" $(basename $0)
  printf "Usage:\n  %s -f FASTA_r1 -r FASTA_r2\n\n" $(basename $0)

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
  echo ""
  exit 0
}

if [[ $# -eq 0 ]]; then
  HELP
fi

while getopts :a:d:i:f:m:o:r:s:h OPT; do
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

if [[ ! -d $OUT_DIR ]]; then
  mkdir -p "$OUT_DIR"
fi

NUM=$(find $INDEX_DIR -name $INDEX.\*.cf | wc -l | awk '{print $1}')

if [[ $NUM -gt 0 ]]; then
  echo "Using INDEX \"$INDEX\""
else
  echo "Cannot find INDEX \"$INDEX\""
  echo "Please choose from the following:"
  ls -1 $INDEX_DIR/*.cf | cat -n
  exit 1
fi

if [[ ! -d "$OUT_DIR" ]]; then
  mkdir -p "$OUT_DIR"
fi

REPORT_DIR="$OUT_DIR/reports"
if [[ ! -d "$REPORT_DIR" ]]; then
  mkdir -p "$REPORT_DIR"
fi

PLOT_DIR="$OUT_DIR/plots"
if [[ ! -d "$PLOT_DIR" ]]; then
  mkdir -p "$PLOT_DIR"
fi

CENT_PARAM="$$.centrifuge.param"
cat /dev/null > $CENT_PARAM

#
# Single
#
if [[ ! -z $FASTA ]]; then
  BASENAME=$(basename $FASTA)
  echo "Will process single FASTA \"$BASENAME\""
  echo "CENTRIFUGE_INDEXES=$INDEX_DIR centrifuge -f -x $INDEX -U $FASTA -S $REPORT_DIR/$BASENAME.sum --report-file $REPORT_DIR/$BASENAME.tsv" > $CENT_PARAM
#
# Paired-end
#
elif [[ ! -z $FORWARD ]] && [[ ! -z $REVERSE ]]; then
  echo "Will process FORWARD \"$FORWARD\" REVERSE \"$REVERSE\""
  S=""
  if [[ ! -z $SINGLETONS ]]; then
    S="-U $SINGLETONS"
  fi
  echo "CENTRIFUGE_INDEXES=$INDEX_DIR centrifuge -f -x $INDEX -1 $FORWARD -2 $REVERSE $S -S $REPORT_DIR/$BASENAME.sum --report-file $REPORT_DIR/$BASENAME.tsv" > $CENT_PARAM
elif [[ ! -z $IN_DIR ]] && [[ -d $IN_DIR ]]; then
  if [[ $MODE == 'single' ]]; then
    FILES=$(mktemp)
    find $IN_DIR -type f -size +0c > $FILES
    while read FILE; do
      BASENAME=$(basename $FILE)
      echo "CENTRIFUGE_INDEXES=$INDEX_DIR centrifuge -f -x $INDEX -U $FILE -S $REPORT_DIR/$BASENAME.sum --report-file $REPORT_DIR/$BASENAME.tsv" >> $CENT_PARAM
    done < $FILES
    rm $FILES
  else
    echo "Can't yet run IN_DIR with 'paired' mode"
    exit 1
  fi
else
  echo "Must have -d IN_DIR/-a FASTA/-f FORWARD & -r REVERSE [-s SINGLETON]"
  exit 1
fi

echo "Running NJOBS \"$(lc $CENT_PARAM)\" for Centrifuge \"$CENT_PARAM\""
export LAUNCHER_DIR=$HOME/src/launcher
export LAUNCHER_PPN=2
export LAUNCHER_WORKDIR=$BIN
export LAUNCHER_JOB_FILE="$CENT_PARAM"
export LAUNCHER_RMI=SLURM
export LAUNCHER_SCHED=interleaved
export LAUNCHER_PLUGIN_DIR=$LAUNCHER_DIR/plugins
$LAUNCHER_DIR/paramrun
echo "Finished Centrifuge"

BUBBLE_PARAM="$$.bubble.param"
echo "Rscript --vanilla centrifuge_bubble.R --dir $REPORT_DIR --outdir $PLOT_DIR --outfile bubble --title centrifuge" > $BUBBLE_PARAM
export LAUNCHER_JOB_FILE=$BUBBLE_PARAM
echo "Starting bubble"
$LAUNCHER_DIR/paramrun
echo "Finished bubble"

echo "Done, look in OUT_DIR \"$OUT_DIR\""

echo "Comments to Ken Youens-Clark <kyclark@email.arizona.edu"
