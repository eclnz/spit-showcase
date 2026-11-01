# SPIT showcase

Four pipelines on public data, written in [SPIT](https://github.com/eclnz/spit) and run on one machine with [spit-bash](https://github.com/eclnz/spit-bash). They show the same language describing unrelated work, with real tools from conda-forge and bioconda:

| Folder | Data | Tools | Jobs |
| --- | --- | --- | --- |
| [`digits/`](digits) | [Free Spoken Digit Dataset](https://github.com/Jakobovski/free-spoken-digit-dataset): 6 speakers × 10 digits × 50 takes | sox, soxi, Python | 1,276 for 5 takes, 12,076 for all 50 |
| [`anatomical/`](anatomical) | The T1-weighted images of [OpenNeuro ds000001](https://openneuro.org/datasets/ds000001): 16 subjects, 4 by default | nibabel, dipy, matplotlib | 17 for 4 subjects, 65 for all 16 |
| [`functional/`](functional) | The first task run of the same dataset: 16 subjects, 3 by default | nibabel, matplotlib | 19 for 3 runs, 97 for all 16 |
| [`covid/`](covid) | [nf-core SARS-CoV-2 test data](https://github.com/nf-core/test-datasets/tree/modules/data/genomics/sarscov2): a reference and two samples of paired reads | fastp, bwa, samtools, bcftools | 14 |

## Set up

```sh
micromamba create -f environment.yml        # or: conda env create -f environment.yml
micromamba activate spit-showcase
cargo install --git https://github.com/eclnz/spit --branch dev spit
pip install git+https://github.com/eclnz/spit-bash@dev
```

spit-bash's `dev` branch reads the cores and memory these pipelines declare, and runs each line of a command written as a block.

## Spoken digits

```sh
cd digits
./fetch.sh                       # 5 takes each, 300 files; TAKES=50 ./fetch.sh for all 3,000
spit dag digits.spitin --counts  # what will run, without running it
spit-bash run digits.spitin
```

[`digits.spit`](digits/digits.spit) has three stages:

- **clean:** trims the silence from both ends of each recording and brings it to 16 kHz at -1 dBFS.
- **measure:** writes each recording's duration, with `soxi -D` on its stdout, and draws its spectrogram.
- **summarise:**
  - joins each speaker's takes of a digit into one file, with `@vary(take)`;
  - writes a duration table per speaker, with `@vary(digit, take)`;
  - writes a duration table per digit, with `@vary(speaker, take)`.

The recipe, [`digits.spitin`](digits/digits.spitin), reads the dataset's own file names, `recordings/3_theo_12.wav`, as `{digit}_{speaker}_{take}`. It requires that every speaker says every digit.

Results land under `data/out/`, one folder per stage and product, such as `out/summarise/by_digit/digit=3.tsv`.

## T1-weighted quality control

```sh
cd anatomical
./fetch.sh                        # 4 subjects, 18 MB; SUBJECTS=16 ./fetch.sh for all 16, 80 MB
spit dag t1w_qc.spitin --counts
spit-bash run t1w_qc.spitin       # exits 1 when a subject fails the check
```

[`t1w_qc.spit`](anatomical/t1w_qc.spit) reads the dataset's BIDS names, `sub-01/anat/sub-01_T1w.nii.gz`, and for each subject:

- **inspect:** draws the middle slice of each axis.
- **measure:** writes the image's grid, voxel size, orientation and signal-to-noise ratio as JSON, then collects them into `data/out/measure/cohort.tsv`, one row per subject.
- **qc:** copies the summary, and the copy must pass `check usable(min_snr)`, declared in the pipeline and attached as `@check(usable(35))`. A subject that passes is released: its image is copied to `data/out/qc/ready/`, where later steps would read it.

Some subjects fail, and the pipeline expects it. With the 4 default subjects, 17 jobs run in 5 s and subject 4 fails. For all 16 subjects, 65 jobs run in 17 s on 4 cores, and:

- Subjects 4, 7 and 8 fail the check. Subject 4's background has been removed, so there is almost no air to measure noise in and its ratio is `n/a`. Subjects 7 and 8 have SNRs of 33.3 and 34.8, below 35. The log says why: `SNR 33.3 is below 35`.
- Each failed subject's release job fails with it, and the other 13 subjects are released.
- All 16 subjects are still in the table and have their mosaics, because neither reads the check's output. The run exits 1.

## BOLD quality control

```sh
cd functional
./fetch.sh                        # 3 runs, 138 MB; SUBJECTS=16 ./fetch.sh for all 16, 741 MB
spit-bash run bold_qc.spitin -j 3
```

[`bold_qc.spit`](functional/bold_qc.spit) reads `sub-01/func/sub-01_task-balloonanalogrisktask_run-01_bold.nii.gz` as `sub-{sub}_task-{task}_run-{run}`, and for each run:

1. Writes the mean image over time and the temporal SNR, each voxel's mean over its standard deviation, from one pass over the 4D file.
2. Masks the voxels that hold signal.
3. Draws the SNR map with the mask's outline.
4. Writes the median SNR inside the mask as JSON, and collects the runs into `data/out/summary/cohort.tsv`.
5. Approves each run whose median SNR is at least 40, with `@check(usable(40))`, and releases its SNR map to `data/out/qc/ready/`.

With the 3 default runs, 19 jobs run in 9 s and subject 3 fails. For all 16 subjects, 97 jobs run in 31 s with `-j 4`. Subjects 3 and 15 fail the check, with median SNRs of 34.7 and 30.6, and the other 14 runs are released. The median SNR in the table runs from 30.6 to 64.9.

Both pipelines keep their scripts in a `scripts/` folder beside the pipeline and name it with `{@here}`, so they run from wherever the dataset is. The thresholds, 35 and 40, are examples of a policy a lab would set for itself.

## SARS-CoV-2 variants

```sh
cd covid
./fetch.sh
spit-bash run variants.spitin -j 4
```

[`variants.spit`](covid/variants.spit) runs these steps for each sample:

1. Index the reference twice: with `bwa index`, into a folder of its own, and with `samtools faidx`, which writes `genome.fasta.fai` beside the FASTA in `data/reference/`, where bcftools looks for it.
2. Trim the reads with fastp.
3. Align them with `bwa mem`, with a read group that names the sample.
4. Sort and index the alignments, in one job whose command runs `samtools sort` and then `samtools index`, since the index is written beside the BAM.
5. Run `samtools flagstat`.
6. Pile up and call variants with bcftools.

Last, it merges the calls into one cohort VCF, `data/out/call/cohort.vcf.gz`, which holds 12 variants. Each step declares the cores and memory it needs, and `{@cores}` hands the tool its thread count.

## What it shows

Times are on 4 cores.

- **Planning is instant.** `spit dag` plans 12,076 audio jobs in 0.3 s.
- **A full run is quick.** spit-bash runs all 12,076 jobs in 65 s with `-j 4`. A rerun with nothing to do takes 8 s, of which loading the DAG is most.
- **Editing a command reruns only what changed.** Adding `-M` to `bwa mem` reran the alignments and the steps after them. The pileups came out byte-identical, so spit-bash stopped there: the variant calls and the cohort merge didn't rerun.
- **Touching a file reruns nothing**, because spit-bash compares files by content.
- **Selection.** `spit-bash run digits.spitin --only speaker=theo` runs one speaker's 211 jobs out of 1,276.
- **Bad input is caught by checks.** A gzip of garbage passed fastp and `test -s`. A `fastq_ok` check on the reads stops it, and the run reports which file failed.
- **Commands take dimension values.** `bwa mem` names each sample in its read group with `{sample}`. Each duration table gets every file's speaker, digit and take as `{durations.speaker}`, `{durations.digit}` and `{durations.take}`, in the order of `{durations}`.
- **A subject that fails quality control stops only itself.** In `anatomical/`, subjects 4, 7 and 8 fail `@check(usable(35))`. Their release jobs fail with them, the other 13 subjects are released, the table still holds all 16, and the run exits 1.
- **Memory is enforced.** A run given less `--memory` than a step declares is refused before it starts, naming each job.
