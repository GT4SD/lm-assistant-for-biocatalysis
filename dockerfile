# -------------------------------
# BUILDER STAGE
# -------------------------------
FROM continuumio/miniconda3:24.5.0-0 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.39.5-0+deb12u2 \
    wget=1.21.3-1+b2 \
    curl=7.88.1-10+deb12u8 \
    build-essential \
    cmake \
    libfftw3-dev \
    libopenblas-dev \
    libopenmpi-dev \
    openmpi-bin \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://ftp.gromacs.org/gromacs/gromacs-2023.3.tar.gz && \
    tar -xzf gromacs-2023.3.tar.gz && \
    cd gromacs-2023.3 && \
    mkdir build && \
    cd build && \
    cmake .. -DGMX_BUILD_OWN_FFTW=ON -DCMAKE_INSTALL_PREFIX=/opt/gromacs && \
    make -j$(nproc) && \
    make install && \
    cd ../.. && \
    rm -rf gromacs-2023.3 gromacs-2023.3.tar.gz

RUN conda create -n lmabc python=3.10 -y

SHELL ["/bin/bash", "-c"]

WORKDIR /app
COPY . /app

RUN conda run -n lmabc conda install -y -c conda-forge -c schrodinger pymol-bundle && \
    conda run -n lmabc pip install uv && \
    conda run -n lmabc uv pip install .

RUN conda clean -a -y

# -------------------------------
# RUNTIME STAGE
# -------------------------------
FROM debian:bookworm-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    git \
    wget \
    curl \
    ca-certificates \
    libfftw3-dev \
    libopenblas-dev \
    libopenmpi-dev \
    openmpi-bin \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

COPY --from=builder /opt/conda /opt/conda
COPY --from=builder /opt/gromacs /opt/gromacs
COPY --from=builder /app /app

WORKDIR /app

ENV LMABC_BASE_DIR=/app/.lmabc \
    TRANSFORMERS_CACHE=/app/.hf_cache \
    MOLECULAR_DYNAMICS_GROMACS_PATH=/opt/gromacs/bin \
    PATH=/opt/conda/bin:/opt/conda/envs/lmabc/bin:/opt/gromacs/bin:$PATH

RUN /opt/conda/bin/conda init bash && \
    /opt/conda/bin/conda config --set auto_activate_base false && \
    /opt/conda/bin/conda clean -a -y

RUN useradd -m -d /app -s /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

RUN conda run -n lmabc bash tools_setup/setup.sh

EXPOSE 8501

CMD ["bash"]