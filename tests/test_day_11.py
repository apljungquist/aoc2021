#!/usr/bin/env python3
import itertools
import logging
import operator
import pathlib
import textwrap

import pytest

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")


def _fmt_energy_levels(energy_levels, max_row, max_col):
    return "\n".join(
        "".join(
            [str(energy_levels[row_num, col_num]) for col_num in range(max_col + 1)]
        )
        for row_num in range(max_row + 1)
    )


def _neighbors(row_num, col_num, max_row, max_col):
    if row_num > 0:
        if col_num > 0:
            yield row_num - 1, col_num - 1

        yield row_num - 1, col_num

        if col_num < max_col:
            yield row_num - 1, col_num + 1

    if col_num > 0:
        yield row_num, col_num - 1

    if col_num < max_col:
        yield row_num, col_num + 1

    if row_num < max_row:
        if col_num > 0:
            yield row_num + 1, col_num - 1

        yield row_num + 1, col_num

        if col_num < max_col:
            yield row_num + 1, col_num + 1


def _read_energy_levels(path: pathlib.Path):
    return {
        (row_num, col_num): int(cell)
        for row_num, line in enumerate(path.read_text().splitlines())
        for col_num, cell in enumerate(line)
    }


def _step(energy_levels, max_row, max_col):
    flashed = set()
    for k in energy_levels:
        energy_levels[k] += 1

    making_progress = True
    while making_progress:
        making_progress = False
        for octopus, energy_level in energy_levels.items():
            if energy_level > 9 and octopus not in flashed:
                flashed.add(octopus)
                making_progress = True
                for neighbor in _neighbors(*octopus, max_row, max_col):
                    energy_levels[neighbor] += 1

    for octopus in flashed:
        energy_levels[octopus] = 0

    return len(flashed)


def _simulate(energy_levels, num_step):
    max_row = max(map(operator.itemgetter(0), energy_levels))
    max_col = max(map(operator.itemgetter(1), energy_levels))
    return sum(_step(energy_levels, max_row, max_col) for _ in range(num_step))


def solution_1(path):
    energy_levels = _read_energy_levels(path)
    return _simulate(energy_levels, 100)


def solution_2(path):
    energy_levels = _read_energy_levels(path)
    max_row = max(map(operator.itemgetter(0), energy_levels))
    max_col = max(map(operator.itemgetter(1), energy_levels))
    for i in itertools.count():
        if not any(energy_levels.values()):
            break
        _step(energy_levels, max_row, max_col)
    return i


@pytest.mark.parametrize(
    "num_step, expected",
    [
        (
            0,
            textwrap.dedent(
                """\
                    5483143223
                    2745854711
                    5264556173
                    6141336146
                    6357385478
                    4167524645
                    2176841721
                    6882881134
                    4846848554
                    5283751526"""
            ),
        ),
        (
            1,
            textwrap.dedent(
                """\
                    6594254334
                    3856965822
                    6375667284
                    7252447257
                    7468496589
                    5278635756
                    3287952832
                    7993992245
                    5957959665
                    6394862637"""
            ),
        ),
        (
            2,
            textwrap.dedent(
                """\
                    8807476555
                    5089087054
                    8597889608
                    8485769600
                    8700908800
                    6600088989
                    6800005943
                    0000007456
                    9000000876
                    8700006848"""
            ),
        ),
        (
            100,
            textwrap.dedent(
                """\
                    0397666866
                    0749766918
                    0053976933
                    0004297822
                    0004229892
                    0053222877
                    0532222966
                    9322228966
                    7922286866
                    6789998766"""
            ),
        ),
    ],
)
def test_one_step(num_step, expected):
    energy_levels = _read_energy_levels(INPUTS_PATH / "example.txt")
    _simulate(energy_levels, num_step)
    max_row = max(map(operator.itemgetter(0), energy_levels))
    max_col = max(map(operator.itemgetter(1), energy_levels))
    assert _fmt_energy_levels(energy_levels, max_row, max_col) == expected


def test_example_1():
    actual = solution_1(INPUTS_PATH / "example.txt")
    expected = 1656
    assert actual == expected


def test_input_1():
    actual = solution_1(INPUTS_PATH / "input.txt")
    expected = 1773
    assert actual == expected


def test_example_2():
    actual = solution_2(INPUTS_PATH / "example.txt")
    expected = 195
    assert actual == expected


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 494
    assert actual == expected
