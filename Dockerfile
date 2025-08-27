# syntax=docker/dockerfile:1

FROM condaforge/miniforge3:latest

# Install system dependencies including zsh and curl
RUN apt-get update && apt-get install -y \
    curl \
    git \
    zsh \
    sudo \
    libhdf5-dev \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create user account and add to sudo group
RUN useradd -m -s /bin/zsh user && \
    echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy the latest UV installer
COPY --from=ghcr.io/astral-sh/uv:0.8.9 /uv /uvx /bin/

# Change ownership of conda directories to user
RUN chown -R user:user /opt/conda

# Switch to the user account
ENV USER=user
USER ${USER}
WORKDIR /home/${USER}
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" --unattended

RUN mamba shell init --shell zsh
RUN mamba create -n benchmark python=3.13 r-base -y
RUN mamba run -n benchmark mamba install -c conda-forge h5py python-blosc2 -y
RUN mamba run -n benchmark uv pip install "cogent3[extra]" cogent3-h5seqs scikit-bio biopython

# now run cogent3 import once to trigger numba.jit compiles
RUN mamba run -n benchmark python -c "import cogent3"

# Add conda activation to .zshrc and set benchmark as default environment
RUN echo "" >> ~/.zshrc && \
    echo "# Auto-activate benchmark environment" >> ~/.zshrc && \
    echo "mamba activate benchmark" >> ~/.zshrc

# Set the default command to start zsh
CMD ["zsh"]


