# SPIT showcase

Four pipelines on public data, written in [SPIT](https://github.com/eclnz/spit) and run on one machine with [spit-bash](https://github.com/eclnz/spit-bash). They show the same language describing unrelated work, with real tools from conda-forge and bioconda:

| Folder | Data | Tools | Jobs |
| --- | --- | --- | --- |
| [`digits/`](digits) | [Free Spoken Digit Dataset](https://github.com/Jakobovski/free-spoken-digit-dataset): 6 speakers × 10 digits × 50 takes | sox, soxi, Python | 1,276 for 5 takes, 12,076 for all 50 |
| [`covid/`](covid) | [nf-core SARS-CoV-2 test data](https://github.com/nf-core/test-datasets/tree/modules/data/genomics/sarscov2): a reference and two samples of paired reads | fastp, bwa, samtools, bcftools | 14 |
| [`terrain/`](terrain) | [Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) on AWS: 2 × 2 elevation tiles around Rainier, Fuji and the Matterhorn | gdalwarp, gdaldem, gdal_contour, Python | 19 |
| [`ml/`](ml) | scikit-learn's bundled datasets: iris, wine, breast cancer, digits | scikit-learn, pandas | 53 |

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

## Terrain

```sh
cd terrain
./fetch.sh
spit-bash run terrain.spitin -j 4
```

[`terrain.spit`](terrain/terrain.spit) runs these steps for each region:

1. Stitch its four tiles into one raster on the region's UTM grid with `gdalwarp`. The grid comes from [`grids/`](terrain/grids), one gdalwarp option file per region.
2. Draw a hillshade and a colour relief from the shared [`ramp.txt`](terrain/ramp.txt).
3. Compute slopes, and trace a contour every 100 m.
4. Measure its elevation and slope with [`row.py`](terrain/row.py).

Last, it gathers one row per region into `data/out/summary/regions.tsv`:

```plain
region      lowest_m  highest_m  mean_m  mean_slope_deg  steepest_deg
fuji        30        3753       901     12.8            76.7
matterhorn  1108      4518       2803    25.4            75.6
rainier     376       4387       1552    24.2            71.8
```

**What SPIT does for the workflow here:**
- **Every setting is an input.** The ramp, each region's grid and the measuring script are sources like the tiles.
  - Editing the ramp reruns the three colour reliefs and nothing else.
  - Changing Fuji's cell size reruns Fuji's seven jobs and the table, not the other regions.
- **A new region is new files.** Adding a folder of tiles and a grid file adds that region's jobs. The pipeline itself doesn't change.

## Classifiers

```sh
cd ml
./fetch.sh                      # writes scikit-learn's bundled datasets as CSV
spit-bash run ml.spitin -j 4
```

[`classifiers.spit`](ml/classifiers.spit) makes a comparison grid of every model in [`models/`](ml/models) on every dataset.

1. **Split:** each dataset is split once, stratified, into training and test sets.
2. **Fit:** every model is fitted to every training set, with `model @each(model)`. A model is a JSON file naming a scikit-learn estimator and its settings.
3. **Score:** each fit is scored on its test set.
4. **Rank:** the scores are ranked twice:
   - the models on each dataset, with `@vary(model)`;
   - the datasets for each model, with `@vary(dataset)`.

`{scores.model}` labels each row with the model it came from, so the ranking script never parses file names. For example, `data/out/rank/per_dataset/dataset=digits.tsv`:

```plain
model     accuracy  macro_f1
forest    0.984     0.984
svm       0.982     0.982
knn       0.973     0.973
logistic  0.969     0.969
tree      0.856     0.856
```

**What SPIT does for the workflow here:**
- **Adding a model is adding a file.** Dropping `tree.json` into `models/` ran 13 jobs: four fits, four scores, four rankings and the tree's own table. The 40 others stayed current.
- **Retuning a model reruns that model.** Changing `knn`'s `n_neighbors` reran its four fits and scores. Two of its scores came out identical, so their rankings didn't rerun.
- **The code is an input too.** Each step's script in [`steps/`](ml/steps) is a source, so editing `rank.py` reruns the 9 rankings and nothing upstream. One script for every step would rerun all 53 jobs for any edit.
- **The split is shared.** Every model reads the same split, made once per dataset, so the scores are comparable.

## What it shows

Times are on 4 cores.

- **Planning is instant.** `spit dag` plans 12,076 audio jobs in 0.3 s.
- **A full run is quick.** spit-bash runs all 12,076 jobs in 65 s with `-j 4`. A rerun with nothing to do takes 8 s, of which loading the DAG is most.
- **Editing a command reruns only what changed.** Adding `-M` to `bwa mem` reran the alignments and the steps after them. The pileups came out byte-identical, so spit-bash stopped there: the variant calls and the cohort merge didn't rerun.
- **Touching a file reruns nothing**, because spit-bash compares files by content.
- **Selection.** `spit-bash run digits.spitin --only speaker=theo` runs one speaker's 211 jobs out of 1,276.
- **Bad input is caught by checks.** A gzip of garbage passed fastp and `test -s`. A `fastq_ok` check on the reads stops it, and the run reports which file failed.
- **Commands take dimension values.** `bwa mem` names each sample in its read group with `{sample}`. Each duration table gets every file's speaker, digit and take as `{durations.speaker}`, `{durations.digit}` and `{durations.take}`, in the order of `{durations}`.
- **Memory is enforced.** A run given less `--memory` than a step declares is refused before it starts, naming each job.

## Usability findings

The terrain and classifier pipelines turned up these issues:

- **A rerun fails when its tool won't overwrite.** spit-bash leaves a job's old output in place, so `gdalwarp` needs `-overwrite`. A failed rerun then removes the old result ([spit-bash#36](https://github.com/eclnz/spit-bash/issues/36)).
- **One collection per step.** The terrain table needs each region's elevation and slope statistics, but an operation takes one `many` input. So one step per region writes a row first, and another joins the rows ([spit#195](https://github.com/eclnz/spit/issues/195)).
- **Runner state shows up as unmatched files.** With `root .`, `spit dag` counts spit-bash's logs in `.spit-bash/` as files no rule matches ([spit#196](https://github.com/eclnz/spit/issues/196)).
