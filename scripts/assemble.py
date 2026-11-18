"""Build the full aircraft assembly (aircraft frame), export STEP/GLB, render PNG views.

Usage: python scripts/assemble.py
Outputs: build/assembly/quadplane.step, docs/figures/cad_*.png, analysis/results/cad_mass.json
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from build123d import Compound, export_step  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from quadplane import cots  # noqa: E402
from quadplane.parts import booms, fuselage, tail, wing  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "assembly"
FIG = ROOT / "docs" / "figures"

COLORS = {
    "wing": "#d9dde3", "aileron": "#9fb4cc", "fuselage": "#e8e2d4", "battery_hatch": "#cfc6b0",
    "camera_cradle": "#3a3a3a", "boom_saddle": "#555555", "motor_mount": "#444444",
    "fin": "#c9d2c0", "hstab": "#d9dde3", "elevator": "#9fb4cc",
    "spar": "#222222", "tip_tube": "#222222", "boom": "#1a1a1a", "tail_spar": "#222222",
    "motor": "#b33a3a", "prop": "#6fa8dc", "pusher_motor": "#b33a3a", "pusher_prop": "#6fa8dc",
    "battery": "#4a7f3f", "camera": "#e0a030",
}


def color_for(name: str) -> str:
    for k in sorted(COLORS, key=len, reverse=True):
        if name.startswith(k):
            return COLORS[k]
    return "#999999"


def all_parts():
    printed = {}
    for mod in (wing, fuselage, booms, tail):
        printed.update(mod.make())
    return printed, cots.make()


def tri_mesh(shape, tol=0.6):
    verts, tris = shape.tessellate(tol, 0.5)
    v = np.array([[p.X, p.Y, p.Z] for p in verts])
    return v, np.array(tris)


def render(meshes, name, elev, azim, title, zoom=1.0, alpha_props=0.18):
    fig = plt.figure(figsize=(12, 8.5))
    ax = fig.add_subplot(111, projection="3d")
    light = np.array([0.4, 0.3, 0.85])
    light /= np.linalg.norm(light)
    allv, all_tri, all_col = [], [], []
    for pname, (v, t) in meshes.items():
        if len(t) == 0:
            continue
        tri = v[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = 0.45 + 0.55 * np.abs(n @ light)
        base = np.array(matplotlib.colors.to_rgb(color_for(pname)))
        cols = np.clip(base[None, :] * shade[:, None], 0, 1)
        a = alpha_props if "prop" in pname else 1.0
        all_tri.append(tri)
        all_col.append(np.c_[cols, np.full(len(cols), a)])
        allv.append(v)
    # one collection so matplotlib depth-sorts individual faces across parts
    pc = Poly3DCollection(np.concatenate(all_tri), facecolors=np.concatenate(all_col), edgecolors="none")
    ax.add_collection3d(pc)
    allv = np.vstack(allv)
    c = (allv.max(0) + allv.min(0)) / 2
    r = (allv.max(0) - allv.min(0)).max() / 2 / zoom
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(FIG / f"cad_{name}.png", dpi=110)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    printed, bought = all_parts()
    everything = {**printed, **bought}
    for k, v in everything.items():
        v.label = k
    comp = Compound(children=list(everything.values()))
    export_step(comp, str(OUT / "quadplane.step"))
    bb = comp.bounding_box()
    print(f"assembly envelope: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    all_meshes = {k: tri_mesh(v, 1.0) for k, v in everything.items()}
    internal = ("spar", "tip_tube", "tail_spar", "battery")
    meshes = {k: v for k, v in all_meshes.items() if not k.startswith(internal)}
    render(meshes, "iso", 28, -125, "QP-1 quadplane: isometric (front-left)", zoom=1.9)
    render(meshes, "iso_rear", 22, -35, "QP-1: rear three-quarter", zoom=1.9)
    render(meshes, "top", 90, -90, "QP-1: top view", zoom=1.45)
    render(meshes, "side", 0, -90, "QP-1: side view (left)", zoom=2.0)
    render(meshes, "front", 0, 0, "QP-1: front view", zoom=1.6)
    render(meshes, "rear", 0, 180, "QP-1: rear view", zoom=1.6)
    nose = {k: v for k, v in meshes.items() if not k.startswith(("wing_tip", "aileron", "prop"))}
    render(nose, "detail_centre", 18, -140, "QP-1: centre section detail (props hidden)", zoom=3.2)
    cut = {k: v for k, v in all_meshes.items()
           if k.startswith(("spar", "tip_tube", "tail_spar", "battery", "camera", "boom", "motor",
                            "pusher", "fuselage_rear", "fin", "hstab"))}
    render(cut, "internals", 25, -125, "QP-1: structure and internals (wing, nose, props hidden)", zoom=1.9)
    (ROOT / "analysis" / "results").mkdir(parents=True, exist_ok=True)
    (ROOT / "analysis" / "results" / "cad_envelope.json").write_text(json.dumps(
        {"x_mm": bb.size.X, "y_mm": bb.size.Y, "z_mm": bb.size.Z}, indent=2))
    # printed-part masses at their aircraft-frame centroids -> mass model
    from scripts.build_all import print_mass_g
    cad = {}
    for k, v in printed.items():
        g, mat = print_mass_g(k, v)
        c = v.center()
        cad[k] = {"g": g, "material": mat, "x": c.X / 1000, "y": c.Y / 1000, "z": c.Z / 1000}
    (ROOT / "analysis" / "results" / "cad_mass.json").write_text(json.dumps(cad, indent=2))
    print(f"printed parts: {sum(v['g'] for v in cad.values()):.0f} g")


if __name__ == "__main__":
    main()
