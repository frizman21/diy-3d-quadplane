import importlib

import pytest

from scripts.build_all import fits_bed, part_names


@pytest.mark.parametrize("name", part_names())
def test_part_is_valid_and_fits_bed(name):
    part = importlib.import_module(f"quadplane.parts.{name}").build()
    assert part.is_valid
    assert part.volume > 0
    ok, size = fits_bed(part)
    assert ok, f"{name} is {size}, exceeds the print bed"
    assert part.bounding_box().min.Z >= -1e-6, f"{name} is below the bed (z<0)"
