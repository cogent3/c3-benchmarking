# syntax=docker/dockerfile:1
FROM condaforge/miniforge3:latest

# Create and activate mamba environment
RUN mamba create -n toolenv python=3.13 r-base -y && \
    echo "conda activate toolenv" >> /etc/profile.d/conda.sh

# Set environment variables
ENV CONDA_DEFAULT_ENV=toolenv
ENV PATH=/opt/conda/envs/toolenv/bin:$PATH



# Install Python packages with pip (recommended for conda env)
RUN /opt/conda/envs/toolenv/bin/python -m pip install --upgrade pip --root-user-action=ignore && \
    /opt/conda/envs/toolenv/bin/pip install "cogent3[extra]" scikit-bio biopython --root-user-action=ignore

# Create workspace and data directories
RUN mkdir -p /workspace/data
WORKDIR /workspace

# Copy project files into the container
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# Copy scripts directory into the container
COPY scripts ./scripts

# Install c3bench in editable mode
RUN /opt/conda/envs/toolenv/bin/pip install -e . --root-user-action=ignore

# Set default shell to bash (VS Code expects bash)
SHELL ["/bin/bash", "-c"]

# Set entrypoint to bash
ENTRYPOINT ["/bin/bash"]

# (Optional) Expose Jupyter port
EXPOSE 8888
