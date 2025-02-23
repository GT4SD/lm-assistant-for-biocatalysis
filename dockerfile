# Use the latest Miniconda image as the base
FROM continuumio/miniconda3:latest

# Create a Conda environment named 'py310' with Python 3.10
RUN conda create -n py310 python=3.10 -y

# Change the default shell so that all subsequent commands run within the 'py310' environment
SHELL ["conda", "run", "-n", "py310", "/bin/bash", "-c"]

# Install essential system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install PyMOL via Conda from the conda-forge and schrodinger channels
RUN conda install -y -c conda-forge -c schrodinger pymol-bundle

# Install MinIO Client (mc) manually for the enzyme optimization setup
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install Poetry and configure it to install packages globally
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Run the setup script with the default BLAST database (swissprot)
RUN bash tools_setup/setup.sh --blastdb swissprot

# Expose port 8501 (used for the Streamlit web application, if needed)
EXPOSE 8501

# Add poetry's bin directory to PATH
ENV PATH /opt/conda/envs/py310/bin:$PATH
# Default command: Launch the CLI help message
SHELL ["conda", "run", "-n", "py310", "/bin/bash", "-c"]
