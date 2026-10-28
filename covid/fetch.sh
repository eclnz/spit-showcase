#!/bin/sh
# Download nf-core's SARS-CoV-2 test data into data/: the reference genome and
# two samples of paired Illumina reads.
# https://github.com/nf-core/test-datasets (modules branch), MIT licence.
set -eu
base=https://raw.githubusercontent.com/nf-core/test-datasets/modules/data/genomics/sarscov2
cd "$(dirname "$0")"
mkdir -p data/reference data/reads
curl -sSfL -o data/reference/genome.fasta "$base/genome/genome.fasta"
for sample in test test2; do
    for read in 1 2; do
        curl -sSfL -o "data/reads/${sample}_R${read}.fastq.gz" "$base/illumina/fastq/${sample}_${read}.fastq.gz"
    done
done
ls -R data
