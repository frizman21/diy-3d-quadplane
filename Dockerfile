# CAD + aero analysis toolchain container.
# The repo is bind-mounted at /work; the Python environment lives in the image at /opt/venv.

# ---- Stage 1: build AVL 3.40 (Drela & Youngren, GPL) from source ----
FROM python:3.12-slim-bookworm AS avl-build
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates gfortran make libx11-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
RUN curl -sSfL -o avl.tgz https://web.mit.edu/drela/Public/web/avl/avl3.40b.tgz \
    && tar xzf avl.tgz && cd Avl \
    && find . -name "*.a" -delete && find . -name "*.o" -delete \
    && (cd plotlib && (make gfortran || true) && test -f libPlt_gSP.a) \
    && (cd eispack && gfortran -O -c eispack.f && ar r libeispack.a eispack.o) \
    && cd bin && sed -i "s/-m64//g; s#plotlib/libPlt.a#plotlib/libPlt_gSP.a#" Makefile.gfortran \
    && (make -f Makefile.gfortran || true) && test -x avl && cp avl /usr/local/bin/avl

# ---- Stage 2: runtime ----
FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/
COPY --from=avl-build /usr/local/bin/avl /usr/local/bin/avl

# OCP/VTK runtime libs (headless); xfoil (Drela, GPL); AVL runtime libs.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libxrender1 libxext6 libsm6 libxi6 make git \
        xfoil libgfortran5 liblapack3 libx11-6 \
    && rm -rf /var/lib/apt/lists/*

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/work \
    MPLBACKEND=Agg

WORKDIR /work
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-install-project
