import logging
import pathlib
import re
from pprint import pprint

import pytest

logger = logging.getLogger(__name__)


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def _cuboids(text: str):
    return [
        (m[0] == "on", int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6]))
        for m in re.findall(
            r"^(on|off) x=(-?\d+)..(-?\d+),y=(-?\d+)..(-?\d+),z=(-?\d+)..(-?\d+)$",
            text,
            re.MULTILINE,
        )
    ]


def _range3d(x0, x1, y0, y1, z0, z1):
    assert x0 < x1
    assert y0 < y1
    assert z0 < z1
    if min(x0, y0, z0) < -50:
        return
    if max(x1, y1, z1) > 50:
        return
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                yield x, y, z


def solution_1(puzzle_input: str):
    cuboids = _cuboids(puzzle_input)
    map = {}
    for cuboid in cuboids:
        state = cuboid[0]
        for point in _range3d(*cuboid[1:]):
            map[point] = state
    return sum(map.values())


def solution_2(puzzle_input: str):
    ...


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 590784),
        ("input", 527915),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    assert solution_1(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example", 35),
        # ("input", 5571),  # not 5619, 6225
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
