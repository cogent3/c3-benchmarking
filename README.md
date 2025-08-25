# c3-benchmarking

Benchmarking cogent3 and other Python/R tools for sequence analysis.

## Overview
This project benchmarks cogent3, biopython, scikit-bio, and R tools (Biostrings, genbankr, rtracklayer, ape) for common sequence analysis tasks. Results are collected using `perf` and stored in the `results` folder.

## Data & Results
Datasets are stored in the `data` directory, and benchmark outputs are stored in the `results` directory. Both directories are gitignored by default and will not be tracked in the repository.

To download datasets, use the provided bash script:
```sh
bash scripts/download_data.sh
```
You can interactively select which datasets to download, and the script will prompt before overwriting any existing files.

---

## For Developers (VS Code / Dev Container)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/khiron/c3-benchmarking.git
   cd c3-benchmarking
   ```
2. **Open in VS Code.**
3. **Reopen in Container** when prompted, or use the Command Palette: `Dev Containers: Reopen in Container`.
4. The workspace will be bind-mounted into the container. The environment is set up automatically.
5. **Install your code in editable mode:** This is done automatically via `postCreateCommand`.
6. **Run the data download script:**
   ```sh
   bash scripts/download_data.sh
   ```
7. **Run benchmarks:**
   ```sh
   python -m c3bench.main
   ```

---

## For Reviewers (Docker Only)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/khiron/c3-benchmarking.git
   cd c3-benchmarking
   ```
2. **Build the Docker image:**
   ```sh
   docker build -t c3bench .
   ```
3. **Run the container:**
   ```sh
   docker run -it c3bench
   ```
   The code and dependencies are already installed in the image.
4. **Run the data download script:**
   ```sh
   bash scripts/download_data.sh
   ```
5. **Run benchmarks:**
   ```sh
   python -m c3bench.main
   ```

---

## Notes
- Results are stored in the `results` directory, which is gitignored.
- Datasets are stored in the `data` directory, which is gitignored.
- For questions or issues, please open an issue on GitHub.
