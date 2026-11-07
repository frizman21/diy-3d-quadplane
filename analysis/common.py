"""Shared constants and helpers for the analysis scripts."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "docs" / "figures"
RES = ROOT / "analysis" / "results"
FIG.mkdir(parents=True, exist_ok=True)
RES.mkdir(parents=True, exist_ok=True)

# Standard atmosphere, sea level ISA + a warm summer day sensitivity is done where relevant.
RHO = 1.225  # kg/m^3
MU = 1.789e-5  # Pa s
NU = MU / RHO
G = 9.81


def reynolds(v: float, chord: float) -> float:
    return v * chord / NU


def save_json(name: str, data) -> None:
    (RES / f"{name}.json").write_text(json.dumps(data, indent=2, default=float))


def load_json(name: str):
    return json.loads((RES / f"{name}.json").read_text())


def savefig(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", dpi=130)
    plt.close(fig)
