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
    assert AC.wing.span <= AC.limits.span, "SIZE-1 doorway"
    assert AC.overall_length <= AC.limits.length + 1e-6, "SIZE-2 Suburban (estimated)"
    assert abs(AC.booms.x_front - (AC.x_lift_front + AC.booms.front_overhang)) < 1e-3, \
        "boom front end sits inside the front motor clamp"
    assert AC.booms.x_rear < AC.x_tail_le, "boom reaches the stabiliser"
    assert AC.x_tail_le - 0.25 * AC.tail.h_chord > AC.x_fin_le - AC.tail.v_root_chord, \
        "stab spar lands on the fin root"


def test_pusher_prop_clears_rear_lift_props():
    """Plan view: the pusher prop tip stays outside the rear lift-prop disks."""
    from quadplane import hardware as HW
    x_prop = AC.fuselage.x_tail - (HW.PUSHER_BODY_L + HW.PUSHER_PROP_OFFSET) / 1000
    dx = abs(x_prop - AC.x_lift_rear)
    R = AC.lift.radius
    if dx < R:
        inner_edge = AC.booms.y - (R ** 2 - dx ** 2) ** 0.5  # lift disk edge at the pusher plane
        assert inner_edge - AC.pusher.prop_diameter / 2 >= AC.lift.tip_gap, \
            "pusher prop overlaps a rear lift prop"


def test_tubes_are_catalogue_parts():
    """Every carbon tube is a size and length the supplier stocks (docs/cots-selection.md §9)."""
    from quadplane import hardware as HW
    w, b = AC.wing, AC.booms
    stock = {(od, id_): length for od, id_, length in HW.CARBON_ROLL_WRAPPED}
    for od, id_, need in ((w.spar_od, w.spar_id, 2 * w.spar_half_length),
                          (b.tube_od, b.tube_id, b.length),
                          (w.tip_spar_od, w.tip_spar_id, w.semi_span - 0.02 - w.tip_spar_start)):
        key = (round(od * 1000), round(id_ * 1000))
        assert key in stock, f"{key} is not a stocked roll-wrapped tube"
        assert need * 1000 <= stock[key] + 1e-6, f"{key} needs {need * 1000:.0f} mm, stock is {stock[key]} mm"


def test_spar_wall():
    from quadplane import geometry as G
    assert G.spar_min_wall() >= 0.9, "straight spar must keep >= 0.9 mm wall inside the wing"
    w = AC.wing
    assert G.tube_min_wall(w.tip_spar_od, w.tip_spar_start, w.semi_span - 0.02) >= 0.9, \
        "tip tube must keep >= 0.9 mm wall out to the tip"
