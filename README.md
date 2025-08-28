# c3-benchmarking

Benchmarking cogent3 and other Python/R tools for sequence analysis.

## Overview

This project **WILL** benchmark cogent3, biopython, scikit-bio, and R tools (Biostrings, genbankr, rtracklayer, ape) for common sequence analysis tasks.

---

## For Developers (VS Code / Dev Container)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/khiron/c3-benchmarking.git
   cd c3-benchmarking
   ```
2. **Open in VS Code.**
3. **Reopen in Container** when prompted, or use the Command Palette: `Dev Containers: Reopen in Container`.
4. The workspace will be bind-mounted into the container as `c3-benchmarking`. The environment is set up automatically.
5. **Install your code in editable mode:** This is done automatically when the container is built.

---

## Data

Within the active docker container, change into the `c3-benchmarking` directory and run

```
python setup_data.py
```

This will download any datasets not yet present and put them into `data/`. They currently take up ~4GB.

---

## Note on VS Code Dev Container Terminals

After the container builds, the initial terminal may be used by VS Code for setup and extension installation, and may appear to hang or display setup logs. For interactive work, open a new terminal in VS Code after the container is ready.
