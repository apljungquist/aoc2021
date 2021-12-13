#!/usr/bin/env python3
import io
import logging
import pathlib
import re

import more_itertools
import numpy as np
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
    result = set()
    for line in path.read_text().splitlines():
        if not line:
            break
        parts = line.split(",")
        result.add((int(parts[0]), int(parts[1])))
    return result


def _as_array(points):
    num_row = max(y for _, y in points) + 1
    num_col = max(x for x, _ in points) + 1
    result = np.full((num_row, num_col), False)
    for p in points:
        result[p[::-1]] = True
    return result


def _read_folds(path: pathlib.Path):
    return [
        (m[0], int(m[1]))
        for m in re.findall(r"^fold along (x|y)=(\d+)$", path.read_text(), re.MULTILINE)
    ]


def _folded_horizontal(points, location):
    result = points[:location, :]
    lower = points[location + 1 :, :]
    result[None : -lower.shape[0] - 1 : -1, :] |= lower
    return result


def _folded_vertical(points, location):
    result = points[:, :location]
    lower = points[:, location + 1 :]
    result[:, None : -lower.shape[1] - 1 : -1] |= lower
    return result


def _folded(points, folds):
    for direction, location in folds:
        match direction:
            case "x":
                points = _folded_vertical(points, location)
            case "y":
                points = _folded_horizontal(points, location)
            case _:
                raise ValueError
    return points


def _format_points(points):
    buffer = io.StringIO()
    cells = np.full(points.shape, ".")
    cells[points] = "#"
    np.savetxt(buffer, cells, fmt="%s", delimiter="")
    return buffer.getvalue()


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


def _possible_decodings(points: np.ndarray):
    for letter in ALPHABET:
        if letter:
            template = _as_array(ALPHABET[letter])
        else:
            template = np.full((6, 1), False)

        candidate = points[: template.shape[0], : template.shape[1]]
        print("-" * 80)
        print(_format_points(template))
        print()
        print(_format_points(candidate))
        if np.all(candidate == template):
            yield letter


def _decode_points(points, path=()):
    if not points.shape[1]:
        return "".join(path)

    letter = more_itertools.one(_possible_decodings(points))
    width = max([x for x, _ in ALPHABET[letter]], default=0) + 1

    return _decode_points(points[:, width:], path + (letter,))


def solution_1(path):
    points = _as_array(_read_points(path))
    folds = _read_folds(path)
    return _folded(points, folds[:1]).sum()


def solution_2(path):
    points = _as_array(_read_points(path))
    folds = _read_folds(path)
    folded = _folded(points, folds)
    return _decode_points(folded)


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
