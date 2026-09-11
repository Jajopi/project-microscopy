#!/usr/bin/bash

set -ueo pipefail

MAX_JOBS="${MAX_JOBS:-4}"
IDENTIFIER="${IDENTIFIER:-clusters}"
PLOTS_DIR="${PLOTS_DIR:-overlays}"

mkdir -p "$PLOTS_DIR"

if [ -f stats.csv ]; then rm stats.csv; fi
printf "file\tclusters\tidentified\tTP\tFP\tFN\tsingle\tidentified\tTP\tFP\tFN\n" > stats.csv

if [ -f log.txt ]; then rm log.txt; fi
touch log.txt

process_file() {
    cpid=""
    trap 'kill -TERM "$cpid" 2>/dev/null; exit 143' TERM INT

    file="$(readlink -f "$1")"
    date | tee -a log.txt
    if [ ! -f "$file.$IDENTIFIER.csv" ]; then
        echo "Preprocessing: $file" | tee -a log.txt
        fiji --headless --console -macro ./Preprocess.ijm "$file|$file.$IDENTIFIER.tmp" &>> log.txt &
        cpid=$!; wait "$cpid"; cpid=""

        echo "Analyzing: $file.$IDENTIFIER.tmp" | tee -a log.txt
        fiji --headless --console -macro ./Analyze.ijm "$file.$IDENTIFIER.tmp|$file.$IDENTIFIER.csv" &>> log.txt &
        cpid=$!; wait "$cpid"; cpid=""

        rm "$file.$IDENTIFIER.tmp"
    fi
    name=$(basename "$file" .png)
    plot="$PLOTS_DIR/$name.$IDENTIFIER.png"
    echo "Comparing: $file.$IDENTIFIER.csv" to ../../dataset/labels/"$name".txt | tee -a log.txt
    python ../../compare_results_clusters.py "$file.$IDENTIFIER.csv" ../../dataset/labels/"$name".txt "$file" "$plot" >> stats.csv &
    cpid=$!; wait "$cpid"; cpid=""
}

trap 'echo "Terminating child jobs..." | tee -a log.txt; kill -TERM $(jobs -rp) 2>/dev/null; wait; exit 143' TERM INT

for file in ../../dataset/images/*.png; do
    while [ "$(jobs -rp | wc -l)" -ge "$MAX_JOBS" ]; do
        wait -n
    done
    process_file "$file" &
done
wait

{ head -1 stats.csv; tail -n +2 stats.csv | sort; } > stats.csv.sorted
mv stats.csv.sorted stats.csv
