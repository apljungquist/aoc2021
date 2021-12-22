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
        return (
            (self.hi.x - self.lo.x + 1)
            * (self.hi.y - self.lo.y + 1)
            * (self.hi.z - self.lo.z + 1)
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


def _combine(cuboids):
    counts = collections.defaultdict(int)
    for new_cuboid, new_count in cuboids:
        for old_cuboid, old_count in list(counts.items()):
            try:
                intersection = new_cuboid.intersection(old_cuboid)
            except ValueError:
                continue

            delta = -old_count
            counts[intersection] += delta

        if new_count == 1:
            counts[new_cuboid] += new_count
        else:
            assert new_count == -1

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
