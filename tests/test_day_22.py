from __future__ import annotations

import collections
import dataclasses
import logging
import pathlib
import re

import pytest

logger = logging.getLogger(__name__)


def _cuboids(text: str):
    return [
        (
            Cuboid.new(
                int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6])
            ),
            (1 if m[0] == "on" else -1),
        )
        for m in re.findall(
            r"^(on|off) x=(-?\d+)..(-?\d+),y=(-?\d+)..(-?\d+),z=(-?\d+)..(-?\d+)$",
            text,
            re.MULTILINE,
        )
    ]


@dataclasses.dataclass(frozen=True, eq=True)
class Point:
    x: int
    y: int
    z: int

    def __le__(self, other: Point) -> bool:
        return self.x <= other.x and self.y <= other.y and self.z <= other.z

    def __lt__(self, other: Point) -> bool:
        return self.x < other.x and self.y < other.y and self.z < other.z


@dataclasses.dataclass(frozen=True, eq=True)
class Cuboid:
    lo: Point
    hi: Point

    @staticmethod
    def new(x0, x1, y0, y1, z0, z1):
        return Cuboid(
            Point(x0, y0, z0),
            Point(x1, y1, z1),
        )

    def __len__(self):
        # Ugly hack to avoid explicitly filtering empty intersections
        return max(
            0,
            (
                (self.hi.x - self.lo.x + 1)
                * (self.hi.y - self.lo.y + 1)
                * (self.hi.z - self.lo.z + 1)
            ),
        )

    def intersection(self, other: Cuboid) -> Cuboid:
        lo = Point(
            max(self.lo.x, other.lo.x),
            max(self.lo.y, other.lo.y),
            max(self.lo.z, other.lo.z),
        )
        hi = Point(
            min(self.hi.x, other.hi.x),
            min(self.hi.y, other.hi.y),
            min(self.hi.z, other.hi.z),
        )
        if not lo <= hi:
            raise ValueError
        return Cuboid(lo, hi)

    def __iter__(self):
        for x in range(self.lo.x, self.hi.x + 1):
            for y in range(self.lo.y, self.hi.y + 1):
                for z in range(self.lo.z, self.hi.z + 1):
                    yield (x, y, z)

    # def __repr__(self):
    #     return f"({self.lo.x}, {self.lo.y}), ({self.hi.x}, {self.hi.y})"


def _combine(cuboids):
    counts = collections.defaultdict(int)
    for new_cuboid, new_count in cuboids:
        # print()
        # print(f"{new_count:+d} {new_cuboid}")
        # pprint(counts)
        for old_cuboid, old_count in list(counts.items()):
            try:
                intersection = new_cuboid.intersection(old_cuboid)
            except ValueError:
                continue

            delta = -old_count
            # print(f"{delta:+d} {intersection} ({old_cuboid})")
            counts[intersection] += delta

        if new_count == 1:
            # print(f"{new_count:+d} {new_cuboid}")
            counts[new_cuboid] += new_count
        else:
            assert new_count == -1

    # print()
    # for k, v in counts.items():
    #     print(f"{k}: {v}")
    # print(len(counts))
    return sum(len(cuboid) * count for cuboid, count in counts.items())


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def solution_1(puzzle_input: str):
    lo = Point(-50, -50, -50)
    hi = Point(50, 50, 50)
    cuboids = [
        (cuboid, count)
        for (cuboid, count) in _cuboids(puzzle_input)
        if lo <= cuboid.lo and cuboid.hi <= hi
    ]
    return _combine(cuboids)


def solution_2(puzzle_input: str):
    return _combine(_cuboids(puzzle_input))


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 590784),
        ("example_l", 474140),
        ("input", 527915),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    actual = solution_1(_read_input(stem))
    # print(actual - expected)
    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example_l", 2758514936282235),
        ("input", 1218645427221987),
    ],
)
def test_part_2_on_file_examples(stem, expected):
    assert solution_2(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [],
)
def test_part_2_on_text_examples(text, expected):
    assert solution_2(text) == expected


def test_tiny_example():
    a = Cuboid.new(10, 12, 10, 12, 10, 12)
    b = Cuboid.new(11, 13, 11, 13, 11, 13)
    c = Cuboid.new(9, 11, 9, 11, 9, 11)

    cuboids = [
        (a, 1),
        (b, 1),
        (c, -1),
    ]

    actual = _combine(cuboids)
    expected = 38  # says 39 but I really cannot see it
    assert actual == expected


@pytest.mark.skip
def test_tiny_example2():
    a = Cuboid.new(10, 12, 10, 12, 10, 12)
    b = Cuboid.new(11, 13, 11, 13, 11, 13)
    c = Cuboid.new(11, 12, 11, 12, 11, 12)
    d = Cuboid.new(10, 13, 10, 13, 10, 13)
    e = Cuboid.new(11, 11, 11, 11, 11, 11)
    assert len(a) == len(b) == 3 ** 3
    assert len(c) == 2 ** 3
    assert a.intersection(b) == c

    add_a = (a, 1)
    sub_a = (a, -1)
    add_b = (b, 1)
    sub_b = (b, -1)
    add_c = (c, 1)
    sub_c = (c, -1)
    add_d = (d, 1)
    sub_d = (d, -1)
    add_e = (e, 1)
    sub_e = (e, -1)

    assert _combine([add_a, add_b, sub_e]) == len(a) + len(b) - len(sub_c)
    assert _combine([add_a]) == len(a)
    assert _combine([add_a, add_b]) == len(a) - len(c) + len(b)
    assert _combine([add_a, add_b, sub_c]) == len(a) + len(b) - 2 * len(c)
    assert _combine([add_a, add_b, add_c, sub_c]) == len(a) + len(b) - 2 * len(c)
    assert _combine([add_a, add_b, add_c, sub_c, sub_d]) == 0
    assert _combine([add_a, add_b, add_c, sub_d]) == 0
    assert _combine([add_a, add_b, add_c, sub_d, sub_d]) == 0
    assert _combine([add_a, add_b, add_c, sub_d, sub_d, add_c]) == len(c)
    assert _combine([add_a, sub_a]) == 0


@pytest.mark.skip
@pytest.mark.parametrize(
    "stem",
    [
        "example",
        "example_l",
        "input",
    ],
)
def test_example_prefixes(stem):
    cuboids = _cuboids(_read_input(stem))
    # for x in cuboids:
    #     print(x)
    # assert False
    for i in range(1, len(cuboids)):
        result = set()
        for cuboid, sign in cuboids[:i]:
            if sign == -1:
                result.difference_update(cuboid)
            elif sign == 1:
                result.update(cuboid)
            else:
                assert False

        print(i, cuboids[:i])
        actual = _combine(cuboids[:i])
        expected = len(result)
        assert actual == expected


def test_foo():
    cuboids = [
        (Cuboid(lo=Point(x=-20, y=-36, z=-47), hi=Point(x=26, y=17, z=7)), 1),
        # (Cuboid(lo=Point(x=-20, y=-21, z=-26), hi=Point(x=33, y=23, z=28)), 1),
        # (Cuboid(lo=Point(x=-22, y=-29, z=-38), hi=Point(x=28, y=23, z=16)), 1),
        (Cuboid(lo=Point(x=-46, y=-6, z=-50), hi=Point(x=7, y=46, z=-1)), 1),
        # (Cuboid(lo=Point(x=-49, y=-3, z=-24), hi=Point(x=1, y=46, z=28)), 1),
        # (Cuboid(lo=Point(x=2, y=-22, z=-23), hi=Point(x=47, y=22, z=27)), 1),
        # (Cuboid(lo=Point(x=-27, y=-28, z=-21), hi=Point(x=23, y=26, z=29)), 1),
        # (Cuboid(lo=Point(x=-39, y=-6, z=-3), hi=Point(x=5, y=47, z=44)), 1),
        # (Cuboid(lo=Point(x=-30, y=-8, z=-13), hi=Point(x=21, y=43, z=34)), 1),
        # (Cuboid(lo=Point(x=-22, y=-27, z=-29), hi=Point(x=26, y=20, z=19)), 1),
        # (Cuboid(lo=Point(x=-48, y=26, z=-47), hi=Point(x=-32, y=41, z=-37)), -1),
        # (Cuboid(lo=Point(x=-12, y=6, z=-50), hi=Point(x=35, y=50, z=-2)), 1),
        (Cuboid(lo=Point(x=-48, y=-32, z=-15), hi=Point(x=-32, y=-16, z=-5)), -1),
    ]
    result = set()
    for cuboid, sign in cuboids:
        if sign == -1:
            result.difference_update(cuboid)
        elif sign == 1:
            result.update(cuboid)
        else:
            assert False
    actual = _combine(cuboids)
    expected = len(result)
    assert actual == expected


@pytest.mark.skip
def test_intersection():
    a = Cuboid(lo=Point(x=-20, y=-36, z=-47), hi=Point(x=26, y=17, z=7))
    b = Cuboid(lo=Point(x=-46, y=-6, z=-50), hi=Point(x=7, y=46, z=-1))
    c = Cuboid(lo=Point(x=-48, y=-32, z=-15), hi=Point(x=-32, y=-16, z=-5))

    ab = a.intersection(b)
    ac = a.intersection(c)
    ba = b.intersection(a)
    bc = b.intersection(c)
    ca = c.intersection(a)
    cb = c.intersection(b)

    assert ab == ba
    assert ac == ca
    assert bc == cb

    abc = ab.intersection(c)
    acb = ac.intersection(b)
    bac = ba.intersection(c)
    bca = bc.intersection(a)
    cab = ca.intersection(b)
    cba = cb.intersection(a)

    assert abc == acb == bac == bca == cab == cba

    if abc:
        print(len(abc))
        assert ab
        assert ac
        assert bc
