#!/bin/sh
# Download recordings of the Free Spoken Digit Dataset into data/recordings:
# six speakers saying each digit, TAKES times each (5 by default, 50 at most).
# https://github.com/Jakobovski/free-spoken-digit-dataset, CC BY-SA 4.0.
set -eu
takes=${TAKES:-5}
base=https://raw.githubusercontent.com/Jakobovski/free-spoken-digit-dataset/master/recordings
cd "$(dirname "$0")"
mkdir -p data/recordings
for speaker in george jackson lucas nicolas theo yweweler; do
    for digit in 0 1 2 3 4 5 6 7 8 9; do
        take=0
        while [ "$take" -lt "$takes" ]; do
            name=${digit}_${speaker}_${take}.wav
            [ -s "data/recordings/$name" ] || echo "$base/$name"
            take=$((take + 1))
        done
    done
done | xargs -n 1 -P 8 sh -c 'curl -sSfL -o "data/recordings/$(basename "$0")" "$0"'
echo "$(ls data/recordings | wc -l) recordings in data/recordings"
