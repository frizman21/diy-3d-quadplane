# DIY 3D-printed quadplane

Parametric CAD-as-code for a 3D-printed VTOL quadplane, using build123d (Python, OpenCascade).

## Environment
- All Python runs in Docker (`quadplane-cad` image). Never install Python packages on the host.
- Use the Makefile: `make build [PART=name]`, `make test`, `make shell`, `make viewer`.
- Changing dependencies: edit pyproject.toml → `make lock` → `make image`. Commit uv.lock.
- compose uses `network_mode: bridge` because the host Docker has no free network address pools.

## Layout
- `quadplane/params.py` holds aircraft-level parameters (single source of truth).
- `quadplane/printer.py` has the printer (QIDI Max 4) and material profiles, including fit clearances.
- `quadplane/hardware.py` has off-the-shelf hardware dimensions.
- `quadplane/lib/` holds shared geometry helpers (airfoils, fastener holes, splitting).
- `quadplane/parts/<name>.py` holds one printable part each, exposing `build() -> Part` and an optional `MATERIAL`.
- `scripts/build_all.py` exports `build/<name>.stl|.step` and reports size, bed fit, and solid mass.
- `build/` is generated output. Never commit it.

## Conventions
- Units are mm and g. Body frame: +X forward, +Y toward the left wing, +Z up.
- Parts are returned in print orientation, resting on z=0.
- No magic numbers in parts. Derive dimensions from params, printer, and hardware.
- Every part must pass `make test`: a valid solid that fits the bed (390×390×340 minus a 5 mm margin).
- Parts larger than the bed are split into keyed or joined segments, not scaled.
- Mark unverified dimensions `# VERIFY`. Mark undecided design values `TBD`.
