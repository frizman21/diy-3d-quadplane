"""Minimal XFOIL driver.

AeroSandbox's wrapper pre-creates the polar file, which trips a gfortran runtime error in
XFOIL 6.99 (append after EOF). This driver lets XFOIL create the polar file itself.
Sweeps run outward from alpha=0 in two passes (0 -> max, 0 -> min) for robust BL init.
"""

import subprocess
import tempfile
from pathlib import Path

import numpy as np


def _sweep(coords: np.ndarray, re: float, ncrit: float, a_start: float, a_end: float,
           step: float, max_iter: int, timeout: float, xtr: tuple[float, float]):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        af_file = td / "af.dat"
        np.savetxt(af_file, coords, header="airfoil", comments="")
        polar = td / "polar.txt"
        step = abs(step) if a_end >= a_start else -abs(step)
        cmds = [
            "plop", "g f", "",  # graphics off
            f"load {af_file}",
            "pane",
            "oper",
            f"visc {re:.0f}",
            "vpar", f"n {ncrit}", f"xtr {xtr[0]} {xtr[1]}", "",
            f"iter {max_iter}",
            "pacc", str(polar), "",
            f"aseq {a_start} {a_end} {step}",
            "pacc", "", "quit",
        ]
        try:
            subprocess.run(["xfoil"], input="\n".join(cmds) + "\n", capture_output=True,
                           text=True, timeout=timeout, cwd=td)
        except subprocess.TimeoutExpired:
            pass
        if not polar.exists():
            return np.empty((0, 4))
        rows = []
        for line in polar.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 5:
                try:
                    vals = [float(p) for p in parts[:5]]
                except ValueError:
                    continue
                rows.append((vals[0], vals[1], vals[2], vals[4]))  # alpha, CL, CD, CM
        return np.array(rows) if rows else np.empty((0, 4))


def polar(coords: np.ndarray, re: float, alphas: np.ndarray, ncrit: float = 9.0,
          max_iter: int = 150, timeout: float = 90, xtr: tuple[float, float] = (1.0, 1.0)):
    """Return dict of arrays alpha, CL, CD, CM (converged points only, sorted by alpha)."""
    step = float(np.median(np.diff(alphas)))
    up = _sweep(coords, re, ncrit, 0.0, float(alphas.max()), step, max_iter, timeout, xtr)
    dn = _sweep(coords, re, ncrit, 0.0, float(alphas.min()), step, max_iter, timeout, xtr)
    data = np.vstack([d for d in (up, dn) if len(d)]) if (len(up) or len(dn)) else np.empty((0, 4))
    if len(data) == 0:
        return {k: np.array([]) for k in ("alpha", "CL", "CD", "CM")}
    data = data[np.argsort(data[:, 0])]
    _, idx = np.unique(np.round(data[:, 0], 3), return_index=True)
    data = data[idx]
    return {"alpha": data[:, 0], "CL": data[:, 1], "CD": data[:, 2], "CM": data[:, 3]}
