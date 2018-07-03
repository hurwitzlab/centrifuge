#!/bin/bash

echo "QUERY            \"${QUERY}\""
echo "READS_ARE_PAIRED \"${READS_ARE_PAIRED}\""
echo "FORMAT           \"${FORMAT}\""
echo "INDEX            \"${INDEX}\""
echo "EXCLUDE_TAXIDS   \"${EXCLUDE_TAXIDS}\""
echo "FIGURE_TITLE     \"${FIGURE_TITLE}\""

sh run.sh ${QUERY} ${READS_ARE_PAIRED} ${FORMAT} ${INDEX} ${EXCLUDE_TAXIDS} ${FIGURE_TITLE}
