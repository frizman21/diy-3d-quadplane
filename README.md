# DIY 3D-printed quadplane

Parametric CAD for a 3D-printed VTOL quadplane, built with [build123d](https://github.com/gumyr/build123d).

## Quick start (needs only Docker Desktop)

```sh
make image    # build the toolchain container (once, or after dependency changes)
make build    # export all parts to build/*.stl and *.step
make test     # check every part is a valid solid and fits the QIDI Max 4 bed
make viewer   # interactive 3D viewer at http://localhost:3939
```

Print `build/fit_coupon.stl` first and tune the clearances in `quadplane/printer.py`.
