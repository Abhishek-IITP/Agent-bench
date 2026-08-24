FROM ubuntu:22.04

# Avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    grep \
    sed \
    curl \
    wget \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3 as default
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create a working directory
WORKDIR /workspace

# Set a simple entrypoint
CMD ["/bin/bash"]
