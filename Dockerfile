# syntax=docker/dockerfile:1
FROM condaforge/miniforge3:latest

# Create and activate mamba environment
RUN mamba create -n toolenv python=3.13 r-base -y && \
    echo "conda activate toolenv" >> /etc/profile.d/conda.sh

# Set environment variables
ENV CONDA_DEFAULT_ENV=toolenv
ENV PATH=/opt/conda/envs/toolenv/bin:$PATH

# Install Python packages with uv
RUN /opt/conda/envs/toolenv/bin/python -m pip install --upgrade pip && \
    /opt/conda/envs/toolenv/bin/pip install uv && \
    /opt/conda/envs/toolenv/bin/uv pip install "cogent3[extra]" scikit-bio biopython

# Create workspace and data directories
RUN mkdir -p /workspace/data
WORKDIR /workspace

# Copy project files into the container
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# Install c3bench in editable mode
RUN uv pip install -e .

# Set default shell to bash (VS Code expects bash)
SHELL ["/bin/bash", "-c"]

# Set entrypoint to bash
ENTRYPOINT ["/bin/bash"]

# (Optional) Expose Jupyter port
EXPOSE 8888
