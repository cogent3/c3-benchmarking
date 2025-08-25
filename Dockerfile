# syntax=docker/dockerfile:1

FROM condaforge/miniforge3:latest

# Install system dependencies for biom-format and other scientific packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libhdf5-dev \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Create and activate mamba environment
RUN mamba create -n toolenv python=3.13 r-base -y && \
    echo "conda activate toolenv" >> /etc/profile.d/conda.sh

# Set environment variables
ENV CONDA_DEFAULT_ENV=toolenv
ENV PATH=/opt/conda/envs/toolenv/bin:$PATH
ENV PIP_ROOT_USER_ACTION=ignore

# add conda shell integration to /root/.zshrc    
RUN conda init zsh

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

# Install Oh My Zsh for root
RUN git clone https://github.com/ohmyzsh/ohmyzsh.git /root/.oh-my-zsh \
    && cp /root/.oh-my-zsh/templates/zshrc.zsh-template /root/.zshrc \
    && sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="agnoster"/' /root/.zshrc

# Auto-activate toolenv for root user
RUN echo 'conda activate toolenv' >> /root/.bashrc
RUN echo 'conda activate toolenv' >> /root/.zshrc

# Set default shell to zsh
SHELL ["/bin/zsh", "-c"]

# Set entrypoint to bash
ENTRYPOINT ["/bin/bash"]

# (Optional) Expose Jupyter port
EXPOSE 8888
