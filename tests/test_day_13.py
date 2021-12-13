#!/usr/bin/env python3
import logging
import pathlib
import re

import pytest

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")


def _read_points(path: pathlib.Path):
    result = set()
    for line in path.read_text().splitlines():
        if not line:
            break
        parts = line.split(",")
        result.add((int(parts[0]), int(parts[1])))
    return result


def _read_folds(path: pathlib.Path):
    return [
        (m[0], int(m[1]))
        for m in re.findall(r"^fold along (x|y)=(\d+)$", path.read_text(), re.MULTILINE)
    ]


def _folded_horizontal(points, location):
    assert not any(y == location for _, y in points)
    return {(x, y) if y < location else (x, 2 * location - y) for x, y in points}


def _folded_vertical(points, location):
    assert not any(x == location for x, _ in points)
    return {(x, y) if x < location else (2 * location - x, y) for x, y in points}


def _folded(points, folds):
    for direction, location in folds:
        if direction == "y":
            points = _folded_horizontal(points, location)
        elif direction == "x":
            points = _folded_vertical(points, location)
        else:
            assert False
    return points


def _format_points(points):
    max_row = max(y for _, y in points)
    max_col = max(x for x, _ in points)
    return "\n".join(
        "".join("#" if (x, y) in points else "." for x in range(max_col + 1))
        for y in range(max_row + 1)
    )


def solution_1(path):
    points = _read_points(path)
    folds = _read_folds(path)
    return len(_folded(points, folds[:1]))


def solution_2(path):
    points = _read_points(path)
    folds = _read_folds(path)
    folded = _folded(points, folds)
    print()
    print(_format_points(folded))


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
        ("example", 36),
        ("input", 147848),
    ],
)
def test_part_2_on_examples(stem, expected):
    assert solution_2(INPUTS_PATH / f"{stem}.txt") == expected
