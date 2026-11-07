"""Send the aircraft assembly to a running OCP viewer (python -m ocp_viewer, port 3939).

Usage (inside the container, with the viewer running): python scripts/show.py
`make viewer` starts the viewer and runs this for you.
"""

from ocp_viewer import set_port, show

from scripts.assemble import COLORS, all_parts, color_for

set_port(3939)


def main():
    printed, bought = all_parts()
    parts = {**printed, **bought}
    names = list(parts)
    alphas = [0.25 if "prop" in n else 1.0 for n in names]
    show(*parts.values(), names=names, colors=[color_for(n) for n in names], alphas=alphas,
         reset_camera="reset")
    print(f"sent {len(names)} parts to the viewer: open http://localhost:3939")


_ = COLORS

if __name__ == "__main__":
    main()
