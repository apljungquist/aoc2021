#!/usr/bin/env python3
import logging
import pathlib
import re

import more_itertools
import pytest

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")

A = """\
.##.
#..#
#..#
####
#..#
#..#
"""
E = """\
####
#...
###.
#...
#...
####
"""
H = """\
#..#
#..#
####
#..#
#..#
#..#
"""
O = """\
#####
#...#
#...#
#...#
#####
"""
P = """\
###.
#..#
#..#
###.
#...
#...
"""
R = """\
###.
#..#
#..#
###.
#.#.
#..#
"""
Z = """\
####
...#
..#.
.#..
#...
####
"""


def _read_points(path: pathlib.Path):
    return {
        (int(m[0]), int(m[1]))
        for m in re.findall(r"^(\d+),(\d+)$", path.read_text(), re.MULTILINE)
    }


def _read_folds(path: pathlib.Path):
    return [
        (m[0], int(m[1]))
        for m in re.findall(r"^fold along (x|y)=(\d+)$", path.read_text(), re.MULTILINE)
    ]


def _folded_horizontal(points, row):
    assert not any(y == row for _, y in points)
    return {(x, y) if y < row else (x, 2 * row - y) for x, y in points}


def _folded_vertical(points, col):
    assert not any(x == col for x, _ in points)
    return {(x, y) if x < col else (2 * col - x, y) for x, y in points}


def _folded(points, axis, location):
    match axis:
        case "x":
            return _folded_vertical(points, location)
        case "y":
            return _folded_horizontal(points, location)
        case _:
            assert False


def _format_points(points):
    max_row = max(y for _, y in points)
    max_col = max(x for x, _ in points)
    return "\n".join(
        "".join("#" if (x, y) in points else "." for x in range(max_col + 1))
        for y in range(max_row + 1)
    )


def _parse_points(text):
    result = set()
    for y, row in enumerate(text.splitlines()):
        for x, cell in enumerate(row):
            if cell == "#":
                result.add((x, y))
    return result


ALPHABET = {
    "A": _parse_points(A),
    "E": _parse_points(E),
    "H": _parse_points(H),
    "O": _parse_points(O),
    "P": _parse_points(P),
    "R": _parse_points(R),
    "Z": _parse_points(Z),
    "": frozenset(),
}
REVERSE = {frozenset(v): k for k, v in ALPHABET.items()}
assert len(ALPHABET) == len(REVERSE)


def _possible_decodings(points):
    if not any(x == 0 for x, _ in points):
        yield ""

    FIVE = frozenset((x, y) for x, y in points if x < 5)
    print("")
    print(_format_points(FIVE))
    if any(x == 4 for x, _ in FIVE) and FIVE in REVERSE:
        yield REVERSE[FIVE]

    FOUR = frozenset((x, y) for x, y in FIVE if x < 4)
    if any(x == 3 for x, _ in FIVE) and FOUR in REVERSE:
        yield REVERSE[FOUR]


def _decode_points(points, path=()):
    if not points:
        return "".join(path)

    letter = more_itertools.one(_possible_decodings(points))
    width = max([x for x, _ in ALPHABET[letter]], default=0) + 1
    return _decode_points(
        {(x - width, y) for x, y in points if x >= width}, path + (letter,)
    )


def solution_1(path):
    points = _read_points(path)
    folds = _read_folds(path)
    return len(_folded(points, *folds[0]))


def solution_2(path):
    points = _read_points(path)
    folds = _read_folds(path)
    for fold in folds:
        points = _folded(points, *fold)
    return _decode_points(points)


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 17),
        ("input", 814),
    ],
)
def test_part_1_on_examples(stem, expected):
    assert solution_1(INPUTS_PATH / f"{stem}.txt") == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", "O"),
        ("input", "PZEHRAER"),
    ],
)
def test_part_2_on_examples(stem, expected):
    assert solution_2(INPUTS_PATH / f"{stem}.txt") == expected
