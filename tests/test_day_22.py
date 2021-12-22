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


@dataclasses.dataclass(frozen=True, eq=True, slots=True)
class Cuboid:
    x0: int
    x1: int
    y0: int
    y1: int
    z0: int
    z1: int

    @staticmethod
    def new(x0, x1, y0, y1, z0, z1):
        return Cuboid(
            x0,
            x1 + 1,
            y0,
            y1 + 1,
            z0,
            z1 + 1,
        )

    def volume(self):
        return (self.x1 - self.x0) * (self.y1 - self.y0) * (self.z1 - self.z0)

    def intersection(self, other: Cuboid) -> Cuboid:
        x0 = max(self.x0, other.x0)
        x1 = min(self.x1, other.x1)
        if x1 <= x0:
            raise ValueError
        y0 = max(self.y0, other.y0)
        y1 = min(self.y1, other.y1)
        if y1 <= y0:
            raise ValueError
        z0 = max(self.z0, other.z0)
        z1 = min(self.z1, other.z1)
        if z1 <= z0:
            raise ValueError

        return Cuboid(x0, x1, y0, y1, z0, z1)


def _combine(cuboids):
    counts = collections.defaultdict(int)
    for new_cuboid, new_count in cuboids:
        for old_cuboid, old_count in list(counts.items()):
            try:
                intersection = new_cuboid.intersection(old_cuboid)
            except ValueError:
                continue

            counts[intersection] -= old_count

        if new_count == 1:
            counts[new_cuboid] += new_count
        else:
            assert new_count == -1

        for k, v in list(counts.items()):
            if not v:
                del counts[k]

    return sum(cuboid.volume() * count for cuboid, count in counts.items())


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def solution_1(puzzle_input: str):
    cuboids = [
        (cuboid, count)
        for (cuboid, count) in _cuboids(puzzle_input)
        if all(-50 <= v <= 51 for v in dataclasses.asdict(cuboid).values())
    ]
    from pprint import pprint

    pprint(cuboids)
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
