# syntax=docker/dockerfile:1

FROM condaforge/miniforge3:latest

## ---------------------------------------------------------------------------
## Base system deps
## ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libhdf5-dev \
    zsh \
    sudo \
    git \
    passwd \
    && rm -rf /var/lib/apt/lists/*

## ---------------------------------------------------------------------------
## Dev user (named 'user')
##   - shell: zsh
##   - passwordless sudo
##   (Dev Containers will reuse this; avoid overriding entrypoint.)
## ---------------------------------------------------------------------------
ARG USERNAME=user
ARG USER_HOME=/home/${USERNAME}
RUN if ! id -u "${USERNAME}" >/dev/null 2>&1; then \
        useradd -m -s "$(which zsh)" "${USERNAME}"; \
    fi && \
    echo "${USERNAME}:${USERNAME}" | chpasswd && \
    (getent group sudo || groupadd sudo) && \
    usermod -aG sudo "${USERNAME}" && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/010-${USERNAME} && chmod 0440 /etc/sudoers.d/010-${USERNAME} && \
    grep "^${USERNAME}:" /etc/passwd && id "${USERNAME}"

## ---------------------------------------------------------------------------
## Install UV to manage packages
## ---------------------------------------------------------------------------
COPY --from=ghcr.io/astral-sh/uv:0.8.9 /uv /uvx /bin/

## ---------------------------------------------------------------------------
## Create and activate mamba environment
## ---------------------------------------------------------------------------
RUN mamba create -n toolenv python=3.13 r-base -y && \
    echo "conda activate toolenv" >> /etc/profile.d/conda.sh

# Set environment variables
ENV CONDA_DEFAULT_ENV=toolenv
ENV PATH=/opt/conda/envs/toolenv/bin:$PATH


## ---------------------------------------------------------------------------
# Install Python packages inside conda env using uv (no explicit python path required)
## ---------------------------------------------------------------------------
RUN conda run -n toolenv uv pip install --upgrade pip && \
    conda run -n toolenv uv pip install "cogent3[extra]" scikit-bio biopython

## ---------------------------------------------------------------------------
# Create workspace and data directories
## ---------------------------------------------------------------------------
RUN mkdir -p /workspace/data
WORKDIR /workspace
RUN chown -R ${USERNAME}:${USERNAME} /workspace

# Copy project files into the container in case user hasn't bound local directories
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# Ensure workspace owned by user (before switching users)
RUN chown -R ${USERNAME}:${USERNAME} /workspace

## Install this project (editable) into the conda environment so entry points are available
## using `uv pip` if possible, fallback to `pip` otherwise
RUN conda run -n toolenv uv pip install -e /workspace || conda run -n toolenv pip install -e /workspace

## ---------------------------------------------------------------------------
# Switch to user and install Oh My Zsh
## ---------------------------------------------------------------------------
USER ${USERNAME}
WORKDIR /workspace

# Install Oh My Zsh for user
RUN git clone https://github.com/ohmyzsh/ohmyzsh.git ${USER_HOME}/.oh-my-zsh \
        && cp ${USER_HOME}/.oh-my-zsh/templates/zshrc.zsh-template ${USER_HOME}/.zshrc \
        && sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="agnoster"/' ${USER_HOME}/.zshrc \
        && { \
                 echo ''; \
                 echo '# --- Conda initialization ---'; \
                 echo 'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then'; \
                 echo '  . /opt/conda/etc/profile.d/conda.sh'; \
                 echo '  conda activate toolenv'; \
                 echo 'fi'; \
             } >> ${USER_HOME}/.zshrc \
        && chown -R ${USERNAME}:${USERNAME} ${USER_HOME}/.oh-my-zsh ${USER_HOME}/.zshrc
