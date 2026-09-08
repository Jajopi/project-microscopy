#!/usr/bin/bash

set -ueo pipefail

MAX_JOBS="${MAX_JOBS:-4}"

if [ -f stats.csv ]; then rm stats.csv; fi
printf "file\tlabels\tidentified\tTP\tFP\tFN\taccuracy\n" > stats.csv

if [ -f log.txt ]; then rm log.txt; fi
touch log.txt

process_file() {
    file="$1"
    date | tee -a log.txt
    if [ ! -f "$file".csv ]; then
        echo "Preprocessing: $file" | tee -a log.txt
        fiji --headless --console -macro ./Preprocess.ijm "$file" &>> log.txt

        echo "Analyzing: $file".tmp | tee -a log.txt
        fiji --headless --console -macro ./Analyze.ijm "$file" &>> log.txt

        rm "$file".tmp
    fi
    name=$(basename "$file" .png)
    echo "Comparing: $file".csv with dataset/labels/train/"$name".txt | tee -a log.txt
    python ../../compare_results.py "$file".csv dataset/labels/train/"$name".txt "$file" >> stats.csv
}

for file in ../../dataset/images/train/*.png; do
    while [ "$(jobs -rp | wc -l)" -ge "$MAX_JOBS" ]; do
        wait -n
    done
    process_file "$file" &
done
wait
