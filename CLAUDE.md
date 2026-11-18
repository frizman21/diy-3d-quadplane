# DIY 3D-printed quadplane (QP-1)

Parametric CAD (build123d) and engineering analysis (XFOIL, AVL, AeroSandbox/NeuralFoil) for
a 3D-printed VTOL quadplane.

## Environment
- All Python runs in Docker (`quadplane-cad` image). Never install Python packages on the host.
- Makefile targets:
  - `make analysis` / `make analysis-fast`: the analysis chain.
  - `make build [PART=module]`: export parts.
  - `make test`, `make shell`, `make viewer`.
  - The assembly, renders and CAD mass come from `docker compose run --rm cad python scripts/assemble.py`.
- Changing dependencies: edit pyproject.toml → `make lock` → `make image`. Commit uv.lock.
- The image installs uv from PyPI; ghcr.io metadata fetches hang in this Docker setup.
- compose uses `network_mode: bridge` because the host Docker has no free network address pools.
- XFOIL and AVL are built from MIT sources in the Dockerfile:
  - XFOIL is patched (polar append) for modern gfortran. Don't switch to Debian's `xfoil`
    package, which is built with floating-point traps.
  - Use `analysis/xfoil.py`, not the AeroSandbox XFoil wrapper.

## Project docs
- `docs/requirements.md` holds the requirements, with IDs to cite in code and commits.
- `docs/decisions.md` is the decision log. Record every new decision there. Never edit old
  entries; add a new entry that replaces them.
- `docs/AerodynamicsReport.md` has the analysis. Its numbers come from
  `analysis/results/*.json`, so update the report when the results change.
- `docs/cots-selection.md` has the bought-part (COTS) selections.
- `docs/build-instructions.md` has the printing and assembly steps. Its dimensions and part
  table come from params and `make build`, so update it when the design changes.
- Rule D-000: design v1 for v1 alone. The future 150 kg aircraft matters only for expensive purchases.

## Analysis loop (keep it closed)
1. `quadplane/params.py` changes (SI units, metres).
2. Run `scripts/assemble.py`. It writes CAD masses and centroids to
   `analysis/results/cad_mass.json`, which the mass model reads.
3. Run `make analysis-fast`. Stability places the battery for a 10% static margin and warns
   if the battery passes its forward limit.
4. Run `scripts/assemble.py` again (it places the battery from the stability results), then
   `make build` and `make test`.

## Layout
- `quadplane/params.py`: the design, the single source of truth. CAD and analysis both read it.
- `quadplane/geometry.py`: aircraft-frame geometry helpers (wing sections and lofts, spar line, bed placement).
- `quadplane/printer.py`: printer (QIDI Max 4) and material profiles. `quadplane/hardware.py`: COTS dimensions.
- `quadplane/parts/<module>.py`: each module exposes `make()` (aircraft frame, dict of parts)
  and `build()` (print orientation, dict of parts).
- `quadplane/cots.py`: reference geometry for bought parts (assembly only).
- `analysis/`: `a1`–`a6` scripts, `model.py` (AeroSandbox), `avl.py`, `xfoil.py`, `mass.py`, `hover.py`.
- `build/` is generated output. Never commit it.

## Conventions
- CAD units are mm (params are in m; convert with `mm()`). Body frame: +X forward, +Y left wing, +Z up.
  The origin is the wing-root leading edge.
- `build()` returns parts in print orientation, resting on z=0. `make test` checks that each
  part is a single valid solid inside the bed (390×390×340 minus a 5 mm margin), and checks
  the layout constraints.
- No magic numbers in parts. Derive dimensions from params, printer and hardware.
- Mark unverified dimensions `# VERIFY`. Mark undecided design values `TBD`.
