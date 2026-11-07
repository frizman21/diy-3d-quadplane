"""Export every part in quadplane/parts to build/<part>.stl and .step.

Usage: python scripts/build_all.py [part_name ...]
"""

import importlib
import pkgutil
import sys
from pathlib import Path

from build123d import export_step, export_stl

import quadplane.parts as parts_pkg
from quadplane import printer

OUT = Path(__file__).resolve().parent.parent / "build"


def part_names() -> list[str]:
    return sorted(m.name for m in pkgutil.iter_modules(parts_pkg.__path__))


def fits_bed(part) -> tuple[bool, tuple[float, float, float]]:
    bb = part.bounding_box()
    size = (bb.size.X, bb.size.Y, bb.size.Z)
    lim_xy = (printer.BED_X - 2 * printer.BED_MARGIN, printer.BED_Y - 2 * printer.BED_MARGIN)
    flat = sorted(size[:2])
    ok = flat[0] <= min(lim_xy) and flat[1] <= max(lim_xy) and size[2] <= printer.BED_Z
    return ok, size


def main(names: list[str]) -> int:
    OUT.mkdir(exist_ok=True)
    failures = 0
    for name in names or part_names():
        mod = importlib.import_module(f"quadplane.parts.{name}")
        part = mod.build()
        material = getattr(mod, "MATERIAL", printer.DEFAULT)
        ok, size = fits_bed(part)
        mass_g = part.volume / 1000 * material.density_g_cm3  # solid; real mass depends on infill
        export_stl(part, str(OUT / f"{name}.stl"))
        export_step(part, str(OUT / f"{name}.step"))
        flag = "OK " if ok else "TOO BIG FOR BED"
        print(f"{name:24s} {size[0]:7.1f} x {size[1]:7.1f} x {size[2]:7.1f} mm  "
              f"solid {mass_g:6.1f} g ({material.name})  {flag}")
        failures += not ok
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
