#!/usr/bin/env python3
import logging
import pathlib

import pytest

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")


def read_levels(path: pathlib.Path):
    return {
        (row_num, col_num): int(cell)
        for row_num, row in enumerate(path.read_text().splitlines())
        for col_num, cell in enumerate(row)
    }


def _neighbors(row_num, col_num, max_row, max_col):
    if row_num > 0:
        yield row_num - 1, col_num

    if col_num > 0:
        yield row_num, col_num - 1

    if col_num < max_col:
        yield row_num, col_num + 1

    if row_num < max_row:
        yield row_num + 1, col_num


def solution_1(path):
    levels = read_levels(path)
    frontier = {(0, 0)}
    optima = {(0, 0): 0}
    dst = max(levels)
    while dst not in optima:
        prev = min(frontier, key=lambda k: optima[k])
        frontier.remove(prev)
        for curr in _neighbors(*prev, *dst):
            prev_optimum = optima[prev]
            if curr not in optima or prev_optimum + levels[curr] < optima[curr]:
                optima[curr] = prev_optimum + levels[curr]
                frontier.add(curr)
    return optima[dst]


def solution_2(path):
    raise NotImplementedError


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 40),
        ("input", 553),
    ],
)
def test_part_1_on_examples(stem, expected):
    assert solution_1(INPUTS_PATH / f"{stem}.txt") == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 2188189693529),
        ("input", 2884513602164),
    ],
)
def test_part_2_on_examples(stem, expected):
    assert solution_2(INPUTS_PATH / f"{stem}.txt") == expected
