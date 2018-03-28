#!/bin/bash

echo "QUERY \"${QUERY}\""
echo "INDEX  \"${INDEX}\""
echo "EXCLUDE_TAXIDS \"${EXCLUDE_TAXIDS}\""

sh run.sh ${QUERY} ${INDEX} ${EXCLUDE_TAXIDS}
