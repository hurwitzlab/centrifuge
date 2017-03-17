#!/bin/bash

ARGS=""
if [[ ! -z ${FASTA} ]]; then
  ARGS="-a ${FASTA}"
elif [[ ! -z ${IN_DIR} ]]; then
  ARGS="-d ${IN_DIR}"
elif [[ ! -z ${FORWARD} ]] && [[ ! -z ${REVERSE} ]]; then
  ARGS="-f ${FORWARD} -r ${REVERSE}"

  if [[ ! -z ${SINGLETONS} ]]; then
    ARGS="$ARGS -s $SINGLETONS"
  fi
fi

if [[ ! -z ${INDEX} ]]; then
  ARGS="$ARGS -i ${INDEX}"
fi

if [[ ! -z ${OUT_DIR} ]]; then
  ARGS="$ARGS -o ${OUT_DIR}"
fi

sh run.sh $ARGS
