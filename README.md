# c3-benchmarking

Benchmarking cogent3 and other Python/R tools for sequence analysis.

## Overview

This project **WILL** benchmark cogent3, biopython, scikit-bio, and R tools (Biostrings, genbankr, rtracklayer, ape) for common sequence analysis tasks.

Each `(task, tool)` pair is run as a standalone process under [`hyperfine`](https://github.com/sharkdp/hyperfine). Wall time and peak RSS are aggregated across runs and written to a TSV. Cold-import cost is included in the timed region, which reflects what an end user pays.

---

## For Developers

The dev environment is managed by [pixi](https://pixi.sh). It installs Python, R (when wired up), `hyperfine`, and the `c3bench` package in editable mode from `conda-forge` and PyPI.

1. **Install pixi** (one-time): see <https://pixi.sh/latest/#installation>.
2. **Provision the environment:**
   ```sh
   pixi install
   ```
3. **Download datasets** (~4 GB into `data/`):
   ```sh
   pixi run setup-data
   ```

To run anything below in the env, prefix with `pixi run` (or open a shell with `pixi shell`).

---

## Running benchmarks

Each benchmark runs every supported tool against the same input file and writes a TSV summary to `results/<task>/<dataset>/<file>.tsv` with mean/std time and mean/std RAM per tool.

Parse a FASTA file with biopython, cogent3, and scikit-bio:

```sh
pixi run c3bench parse-fasta --result_root results --path data/hsap_fa/Homo_sapiens.GRCh38.dna.chromosome.1.fa
```

Load a multiple sequence alignment (compares biopython, cogent3 default, cogent3 with the `c3h5s` storage backend, and scikit-bio):

```sh
pixi run c3bench load-aln --result_root results --path data/sars_msa/public-2024-10-01.all.msa.fa
```

`--runs` controls how many timed iterations hyperfine performs per tool (default 3). For tasks with side-effect setup (e.g. `load-aln`'s `.c3h5s` companion file), the orchestrator invokes `c3bench prepare <task> --path …` first. The prepare step is idempotent.

See `c3bench --help` for the rest of the subcommands (`parse-gbk`, `parse-gff`).
