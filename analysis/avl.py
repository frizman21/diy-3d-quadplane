"""AVL (Athena Vortex Lattice) driver: geometry/mass file writers and output parsers.

AVL axes: X aft, Y right(starboard)... AVL uses Y positive out the right wing in its
geometry convention for YDUPLICATE surfaces; we only use symmetric geometry, so the sign of
Y is immaterial. x_avl = -x_body, z_avl = z_body.
"""

import re
import subprocess
import tempfile
from pathlib import Path

import aerosandbox as asb
import numpy as np

from quadplane.params import AIRCRAFT as AC


def _af_file(td: Path, name: str) -> str:
    p = td / f"{name}.dat"
    if not p.exists():
        c = asb.Airfoil(name).repanel(120).coordinates
        np.savetxt(p, c, header=name, comments="")
    return p.name


def write_geometry(td: Path, mach: float = 0.0, xyz_ref=None, wing=None, tail=None) -> Path:
    w = wing or AC.wing
    t = tail or AC.tail
    b = AC.booms
    afw = _af_file(td, w.airfoil)
    afh = _af_file(td, t.h_airfoil)
    afv = _af_file(td, t.v_airfoil)
    xref = xyz_ref if xyz_ref is not None else (0.25 * w.root_chord, 0, 0)
    yc = w.center_span / 2
    dz = np.tan(np.radians(w.dihedral_deg)) * w.outer_span
    x_tip = 0.25 * (w.root_chord - w.tip_chord)
    ail0 = w.aileron_span_frac[0] * w.semi_span
    ail1 = w.aileron_span_frac[1] * w.semi_span
    # interpolate chord/LE/z at aileron stations on the outer panel
    def outer(y):
        f = (y - yc) / w.outer_span
        return (x_tip * f, y, dz * f, w.root_chord + (w.tip_chord - w.root_chord) * f,
                w.root_incidence_deg + w.tip_twist_deg * f)

    hinge_w = 1 - w.aileron_chord_frac
    secs = [(0, 0, 0, w.root_chord, w.root_incidence_deg, None),
            (0, yc, 0, w.root_chord, w.root_incidence_deg, None),
            (*outer(ail0), "a"), (*outer(ail1), "a"),
            (x_tip, w.semi_span, dz, w.tip_chord, w.root_incidence_deg + w.tip_twist_deg, None)]
    lines = [
        "QP1 quadplane", f"{mach}", "0 0 0",
        f"{w.area:.5f} {w.mac:.5f} {w.span:.5f}",
        f"{xref[0]:.5f} {xref[1]:.5f} {xref[2]:.5f}",
        "0.0",  # CDp handled outside AVL
        "SURFACE", "Wing", "12 1.0 30 -1.1", "YDUPLICATE", "0.0", "ANGLE", "0.0",
    ]
    for i, (x, y, z, c, tw, ctl) in enumerate(secs):
        lines += ["SECTION", f"{x:.5f} {y:.5f} {z:.5f} {c:.5f} {tw:.3f}", "AFILE", afw]
        # aileron spans sections 2..3 (ctl on both ends of the hinged strip)
        if ctl == "a":
            lines += ["CONTROL", f"aileron 1.0 {hinge_w:.3f} 0 0 0 -1"]
    xt = -AC.x_tail_le
    he = 1 - t.elevator_chord_frac
    lines += ["SURFACE", "Htail", "8 1.0 12 -1.1", "YDUPLICATE", "0.0", "ANGLE",
              f"{t.h_incidence_deg:.3f}"]
    for y in (0.0, t.h_span / 2):
        lines += ["SECTION", f"{xt:.5f} {y:.5f} {t.h_z:.5f} {t.h_chord:.5f} 0", "AFILE", afh,
                  "CONTROL", f"elevator 1.0 {he:.3f} 0 0 0 1"]
    lines += ["SURFACE", "Fin", "8 1.0 8 1.0", "YDUPLICATE", "0.0"]
    lines += ["SECTION", f"{xt:.5f} {b.y:.5f} {b.z:.5f} {t.v_root_chord:.5f} 0", "AFILE", afv,
              "SECTION", f"{xt + t.v_root_chord - t.v_tip_chord:.5f} {b.y:.5f} "
                         f"{b.z - t.v_height:.5f} {t.v_tip_chord:.5f} 0", "AFILE", afv]
    p = td / "qp.avl"
    p.write_text("\n".join(lines) + "\n")
    return p


def write_mass(td: Path, items) -> Path:
    lines = ["Lunit = 1.0 m", "Munit = 1.0 kg", "Tunit = 1.0 s", "g = 9.81", "rho = 1.225",
             "#  mass   x   y   z   Ixx  Iyy  Izz"]
    for it in items:
        lines.append(f"{it.mass:.5f} {-it.x:.5f} {it.y:.5f} {it.z:.5f}   ! {it.name}")
    p = td / "qp.mass"
    p.write_text("\n".join(lines) + "\n")
    return p


def run(commands: list[str], td: Path, timeout: float = 60) -> str:
    r = subprocess.run(["avl"], input="\n".join(commands) + "\n", capture_output=True,
                       text=True, timeout=timeout, cwd=td)
    return r.stdout


def parse_float(text: str, key: str) -> float:
    m = re.search(re.escape(key) + r"\s*=\s*([-+0-9.Ee]+)", text)
    return float(m.group(1)) if m else float("nan")


def stability(items, cl_trim: float, velocity: float, xyz_cg, wing=None, tail=None) -> dict:
    """Trim at cl_trim (alpha -> CL, elevator -> Cm=0) about the CG; return derivatives,
    neutral point, elevator/alpha at trim and eigenmodes."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        write_geometry(td, xyz_ref=(-xyz_cg[0], 0.0, xyz_cg[2]), wing=wing, tail=tail)
        write_mass(td, items)
        cmds = ["PLOP", "G", "", "LOAD qp.avl", "MASS qp.mass", "MSET 0", "OPER",
                f"A C {cl_trim:.4f}", "D2 PM 0",
                "M", f"V {velocity:.3f}", "", "X", "ST st.txt", "FT ft.txt", "",
                "MODE", "N", "W", "eig.txt", "", "QUIT"]
        out = run(cmds, td)
        st = (td / "st.txt").read_text() if (td / "st.txt").exists() else ""
        eig = (td / "eig.txt").read_text() if (td / "eig.txt").exists() else ""
    res = {k: parse_float(st, k) for k in (
        "Alpha", "CLtot", "CDind", "Cmtot", "CLa", "Cma", "Cnb", "Clb", "CYb", "Clp", "Cmq",
        "Cnr", "Xnp", "e", "Cmd2", "CLd2", "Cld1", "Cnd1")}
    m = re.search(r"elevator\s*=\s*([-+0-9.Ee]+)", st)
    res["elevator_deg"] = float(m.group(1)) if m else float("nan")
    res["eig_raw"] = eig
    res["avl_stdout_tail"] = out[-3000:]
    return res


def parse_modes(eig_text: str):
    """Return list of (real, imag) eigenvalues from AVL's W output."""
    vals = []
    for line in eig_text.splitlines():
        parts = line.split()
        if len(parts) >= 3 and not line.strip().startswith("#"):
            try:
                vals.append((float(parts[1]), float(parts[2])))
            except ValueError:
                pass
    return vals
