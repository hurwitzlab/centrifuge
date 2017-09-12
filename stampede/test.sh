#!/bin/bash

#SBATCH -A iPlant-Collabs
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00
#SBATCH -p development
#SBATCH -J cntrfuge
#SBATCH --mail-type BEGIN,END,FAIL
#SBATCH --mail-user kyclark@email.arizona.edu

OUT_DIR="$SCRATCH/centrifuge/test"

[[ -d "$OUT_DIR" ]] && rm -rf $OUT_DIR/*

#run.sh -a "$WORK/data/pov/fasta/POV_GD.Spr.C.8m_reads.fa" -o $OUT_DIR
run.sh -d "$WORK/data/pov/fasta" -o $OUT_DIR
