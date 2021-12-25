from __future__ import annotations

import itertools
import logging
import operator
import pathlib

import more_itertools
import pytest

logger = logging.getLogger(__name__)


def _format_herd(combined, eb, sb):
    return "\n".join(
        "".join(combined.get((row, col), ".") for col in range(eb)) for row in range(sb)
    )


def _herds(text: str):
    east, south = more_itertools.partition(
        lambda v: v[1] == "v",
        [
            ((row, col), v)
            for row, line in enumerate(text.splitlines())
            for col, v in enumerate(line.strip())
            if v in {"v", ">"}
        ],
    )
    return dict(east), dict(south)


def _step(old_east, old_south, east_boundary, south_boundary):
    new_east = set()
    for old_k in old_east:
        new_k = (old_k[0], (old_k[1] + 1) % east_boundary)
        if new_k in old_east or new_k in old_south:
            new_east.add(old_k)
        else:
            new_east.add(new_k)

    new_south = set()
    for old_k in old_south:
        new_k = ((old_k[0] + 1) % south_boundary, old_k[1])
        if new_k in new_east or new_k in old_south:
            new_south.add(old_k)
        else:
            new_south.add(new_k)

    return new_east, new_south


def _simulate(new):
    old = None

    i = 0
    south_boundary = (
        max(map(operator.itemgetter(0), itertools.chain.from_iterable(new))) + 1
    )
    east_boundary = (
        max(map(operator.itemgetter(1), itertools.chain.from_iterable(new))) + 1
    )
    while old != new:
        i += 1
        old, new = new, _step(
            *new, east_boundary=east_boundary, south_boundary=south_boundary
        )
    return i


def solution_1(puzzle_input: str):
    east, south = _herds(puzzle_input)
    return _simulate((set(east), set(south)))


def solution_2(puzzle_input: str):
    ...


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 58),
        ("input", 516),
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
        # ("example", 44169),
        # ("input", 49180),
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
