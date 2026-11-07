# CAD toolchain container: Python + build123d (OpenCascade).
# The repo is bind-mounted at /work; the Python environment lives in the image at /opt/venv.
FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Runtime libs needed by OCP/VTK (headless, no display).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libxrender1 libxext6 libsm6 libxi6 make git \
    && rm -rf /var/lib/apt/lists/*

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/work

WORKDIR /work
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-install-project
