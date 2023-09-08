FROM python:3.11-slim-buster

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg2 \
        libffi-dev \
        libssl-dev \
        openssh-client \
        wget \
        xz-utils \
        zlib1g-dev

# Set up Miniconda environment
ENV MINICONDA_VERSION=4.9.2
ENV CONDA_DIR=/opt/conda
RUN mkdir $CONDA_DIR && \
    cd $CONDA_DIR && \
    curl -O https://repo.anaconda.com/miniconda/$MINICONDA_VERSION/Miniconda$MINICONDA_VERSION-$PLATFORM-x86_64.sh && \
    chmod +x Miniconda$MINICONDA_VERSION-$PLATFORM-x86_64.sh && \
    ./Miniconda$MINICONDA_VERSION-$PLATFORM-x86_64.sh -b -p $CONDA_DIR && \
    rm -rf /tmp/*

SHELL [ "conda", "env", "create", "-n", "chat_doc_env", "--file", "requirements.txt" ]
# Activate conda environment
SHELL ["conda", "run"]

# Install Streamlit
RUN pip install streamlit==0.75.0

# Copy application code
COPY . /app
WORKDIR /app

# Expose port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "--server.port=$PORT", "--server.address=0.0.0.0"]