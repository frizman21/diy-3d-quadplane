import pytest

from quadplane.params import AIRCRAFT as AC
from scripts.build_all import built_parts, fits_bed, module_names

ALL = [(m, n) for m in module_names() for n in built_parts(m)]


@pytest.fixture(scope="module")
def cache():
    return {m: built_parts(m) for m in module_names()}


@pytest.mark.parametrize("module,name", ALL)
def test_part_is_valid_and_fits_bed(cache, module, name):
    part = cache[module][name]
    assert part.is_valid
    assert part.volume > 0
    assert len(part.solids()) == 1, f"{name} is not a single solid"
    ok, size = fits_bed(part)
    assert ok, f"{name} is {size}, exceeds the print bed"
    assert part.bounding_box().min.Z >= -1e-6, f"{name} is below the bed (z<0)"


def test_layout_constraints():
    assert AC.wing.span <= 1.9, "SIZE-1 doorway"
    assert AC.overall_length <= 1.20 + 1e-6, "SIZE-2 Suburban (estimated)"
    assert abs(AC.booms.x_rear - (AC.x_tail_le - AC.tail.v_root_chord)) < 1e-3, "boom ends at the fin TE"
    assert AC.booms.x_front >= AC.x_lift_front, "front motor mount sits on the boom"


def test_spar_wall():
    from quadplane import geometry as G
    assert G.spar_min_wall() >= 0.9, "straight spar must keep >= 0.9 mm wall inside the wing"
