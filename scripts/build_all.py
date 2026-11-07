"""Export every printable part to build/<part>.stl and .step, check bed fit, and estimate
printed mass from the CAD (shell = surface area x wall thickness, plus infill on the rest).

Usage: python scripts/build_all.py [module ...]   (module = file name in quadplane/parts)
"""

import importlib
import pkgutil
import sys
from pathlib import Path

from build123d import Part, export_step, export_stl

import quadplane.parts as parts_pkg
from quadplane import printer

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build"

# Print profiles: (wall thickness mm, infill fraction). Wall = perimeters x line width.
PROFILES = {
    "wing": (0.5, 0.02), "aileron": (0.5, 0.03),
    "fuselage": (1.2, 1.0), "battery_hatch": (1.2, 1.0), "camera_cradle": (1.2, 0.3),
    "boom_saddle": (1.2, 0.15), "motor_mount": (1.6, 0.25),
    "fin": (0.8, 0.05), "hstab": (0.5, 0.03), "elevator": (0.5, 0.03),
    "fit_coupon": (1.2, 0.2),
}
MATERIALS = {
    "wing": printer.LWPLA, "aileron": printer.LWPLA, "hstab": printer.LWPLA, "elevator": printer.LWPLA,
    "fuselage_nose": printer.LWPLA, "fuselage_rear": printer.LWPLA, "battery_hatch": printer.LWPLA, "camera_cradle": printer.TPU,
    "boom_saddle": printer.PACF, "motor_mount": printer.PACF, "fin": printer.LWPLA,
}


def lookup(table, name, default):
    for k in sorted(table, key=len, reverse=True):
        if name.startswith(k):
            return table[k]
    return default


def module_names() -> list[str]:
    return sorted(m.name for m in pkgutil.iter_modules(parts_pkg.__path__))


def built_parts(module: str) -> dict[str, Part]:
    mod = importlib.import_module(f"quadplane.parts.{module}")
    out = mod.build()
    if not isinstance(out, dict):
        out = {module: out}
    return out


def fits_bed(part) -> tuple[bool, tuple[float, float, float]]:
    bb = part.bounding_box()
    size = (bb.size.X, bb.size.Y, bb.size.Z)
    lim_xy = (printer.BED_X - 2 * printer.BED_MARGIN, printer.BED_Y - 2 * printer.BED_MARGIN)
    flat = sorted(size[:2])
    ok = flat[0] <= min(lim_xy) and flat[1] <= max(lim_xy) and size[2] <= printer.BED_Z
    return ok, size


def print_mass_g(name: str, part) -> tuple[float, str]:
    wall, infill = lookup(PROFILES, name, (1.2, 0.2))
    mat = lookup(MATERIALS, name, printer.DEFAULT)
    area_mm2 = part.area
    vol_mm3 = part.volume
    shell = min(area_mm2 * wall, vol_mm3)
    mass = (shell + max(vol_mm3 - shell, 0) * infill) / 1000 * mat.density_g_cm3
    return mass, mat.name


def main(modules: list[str]) -> int:
    OUT.mkdir(exist_ok=True)
    failures = 0
    masses = {}
    for module in modules or module_names():
        for name, part in built_parts(module).items():
            ok, size = fits_bed(part)
            m, mat = print_mass_g(name, part)
            masses[name] = {"g": m, "material": mat}
            export_stl(part, str(OUT / f"{name}.stl"))
            export_step(part, str(OUT / f"{name}.step"))
            flag = "OK " if ok else "TOO BIG FOR BED"
            print(f"{name:22s} {size[0]:6.0f} x {size[1]:6.0f} x {size[2]:6.0f} mm  "
                  f"~{m:6.1f} g  {mat:22s} {flag}")
            failures += not ok
    if not modules:
        total = sum(v["g"] for k, v in masses.items() if k != "fit_coupon")
        print(f"\nprinted airframe total ~{total:.0f} g (excl. fit coupon)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
