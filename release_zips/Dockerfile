FROM python:3.12-slim-bookworm

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y p7zip-full git && \
    rm -rf /var/lib/apt/lists/*

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies with uv
RUN uv pip install --system PyGithub

ADD release_tar.py /release_tar.py

ENTRYPOINT ["python", "/release_tar.py"]
