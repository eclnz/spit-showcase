# SPIT showcase

Two pipelines on public data, written in [SPIT](https://github.com/eclnz/spit) and run on one machine with [spit-bash](https://github.com/eclnz/spit-bash). They show the same language describing unrelated work, with real tools from conda-forge and bioconda:

| Folder | Data | Tools | Jobs |
| --- | --- | --- | --- |
| [`digits/`](digits) | [Free Spoken Digit Dataset](https://github.com/Jakobovski/free-spoken-digit-dataset): 6 speakers × 10 digits × 50 takes | sox, soxi, Python | 1,276 for 5 takes, 12,076 for all 50 |
| [`covid/`](covid) | [nf-core SARS-CoV-2 test data](https://github.com/nf-core/test-datasets/tree/modules/data/genomics/sarscov2): a reference and two samples of paired reads | fastp, bwa, samtools, bcftools | 14 |

## Set up

```sh
micromamba create -f environment.yml        # or: conda env create -f environment.yml
micromamba activate spit-showcase
cargo install --git https://github.com/eclnz/spit --branch dev spit
pip install git+https://github.com/eclnz/spit-bash@job-resources
```

spit-bash's `job-resources` branch is the one that reads the cores and memory these pipelines declare. Once it is merged, `@dev` will do.

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

## SARS-CoV-2 variants

```sh
cd covid
./fetch.sh
spit-bash run variants.spitin -j 4
```

[`variants.spit`](covid/variants.spit) runs these steps for each sample:

1. Index the reference.
2. Trim the reads with fastp.
3. Align them with `bwa mem`, with a read group that names the sample.
4. Sort and index the alignments.
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
- **Memory is enforced.** A run given less `--memory` than a step declares is refused before it starts, naming each job.

## Usability findings

Building these pipelines turned up friction, filed as issues:

- **Shell wrappers are common.** Four of the nine genomics commands need `sh -c '... "$1" ...' sh {a} {b}`, for a tool run twice in a row (`samtools sort && samtools index`) or for a check that needs a pipe ([spit#183](https://github.com/eclnz/spit/issues/183)).
- **Indexes are folder outputs.** bwa's index is one folder, `bwa index -p {@output}/genome`, read by `bwa mem {index}/genome`, now that the runner makes an output folder before its command ([spit#181](https://github.com/eclnz/spit/issues/181)). bcftools still needs the `.fai` beside the FASTA it reads, so that step copies the FASTA into a folder of its own and indexes it there. Every output must also be named at the call, even when nothing reads it.
- **Commands need dimension values.** A command could name only files, so [`scripts/table.py`](scripts/table.py) parsed each file's speaker, digit and take back out of its name. Now `{sample}` gives a job's own value, which `bwa mem` puts in its read group ([spit#180](https://github.com/eclnz/spit/issues/180)), and `{durations.digit}` gives each collected file's, in the order of `{durations}` ([spit#186](https://github.com/eclnz/spit/issues/186)).
- **Commands run from the dataset root.** A script shipped beside the pipeline is reached as `../../scripts/table.py` ([spit#182](https://github.com/eclnz/spit/issues/182)).
- **Outputs and runner state live inside the dataset folder,** and later `spit` commands note the runner's 1,278 log and state files there ([spit#185](https://github.com/eclnz/spit/issues/185), [spit-bash#32](https://github.com/eclnz/spit-bash/issues/32)).
- **The paths guide gives a recipe form the parser rejects** ([spit#184](https://github.com/eclnz/spit/issues/184)).
- **The runner is the slow part at scale.**
  - Loading a 12,000-job DAG takes most of an 8 s no-op rerun ([spit-bash#28](https://github.com/eclnz/spit-bash/issues/28)).
  - `run` prints a line for every job before starting ([spit-bash#29](https://github.com/eclnz/spit-bash/issues/29)).
- **Memory reads can miss short jobs.** A job that goes over its memory and finishes within half a second isn't caught ([spit-bash#30](https://github.com/eclnz/spit-bash/issues/30)).
- **Partial runs leave stale results silently.** A run with `--only` doesn't say which results it left out of date ([spit-bash#31](https://github.com/eclnz/spit-bash/issues/31)).
