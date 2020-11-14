#!/bin/bash

gfiles=("$1"*);
rfiles=("$2"*);

i=0;

for gfile in "${gfiles[@]}"
do
    echo "Comparing $gfile with ${rfiles[i]}"
    python3 rouge.py $gfile "${rfiles[i]}"
    i=$((i+1));
done