# -------------------------------
# BUILDER STAGE
# -------------------------------
FROM continuumio/miniconda3:24.5.0-0 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.39.5-0+deb12u2 \
    wget=1.21.3-1+b2 \
    curl=7.88.1-10+deb12u8 \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

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
    bash=5.2.15-2+b7 \
    git=1:2.39.5-0+deb12u2 \
    wget=1.21.3-1+b2 \
    curl=7.88.1-10+deb12u8 \
    ca-certificates=20230311 && \
    rm -rf /var/lib/apt/lists/*

RUN wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

COPY --from=builder /opt/conda /opt/conda
COPY --from=builder /app /app

WORKDIR /app

ENV LMABC_BASE_DIR=/app/.lmabc \
    TRANSFORMERS_CACHE=/app/.hf_cache \
    PATH=/opt/conda/bin:/opt/conda/envs/lmabc/bin:$PATH

RUN /opt/conda/bin/conda init bash && \
    /opt/conda/bin/conda config --set auto_activate_base false && \
    /opt/conda/bin/conda clean -a -y

RUN useradd -m -d /app -s /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

RUN conda run -n lmabc bash tools_setup/setup.sh

EXPOSE 8501

CMD ["bash"]
