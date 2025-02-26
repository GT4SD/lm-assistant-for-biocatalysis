# BUILDER STAGE
FROM continuumio/miniconda3:24.5.0-0 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN conda create -n lmabc python=3.10 -y

SHELL ["conda", "run", "-n", "lmabc", "/bin/bash", "-c"]

RUN conda install -y -c conda-forge -c schrodinger pymol-bundle

WORKDIR /app
COPY . /app

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# RUNTIME STAGE
FROM debian:bookworm AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*


RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc && \
chmod +x /usr/local/bin/mc


COPY --from=builder /opt/conda /opt/conda

COPY --from=builder /app /app
WORKDIR /app

ENV ...=/app/.lmabc
ENV TRANSFORMERS_CACHE=/app/.hf_cache
RUN bash tools_setup/setup.sh

EXPOSE 8501

ENV PATH=/opt/conda/envs/lmabc/bin:$PATH

CMD ["bash"]
