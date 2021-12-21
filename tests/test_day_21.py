import itertools
import logging
import pathlib

import more_itertools
import pytest

logger = logging.getLogger(__name__)


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def solution_1(puzzle_input: str):
    dice = (i % 100 + 1 for i in itertools.count())
    positions = list(puzzle_input)
    scores = [0, 0]
    for i in itertools.count():
        player = i % 2
        steps = sum(more_itertools.take(3, dice))
        positions[player] = positions[player] + steps
        while positions[player] > 10:
            positions[player] -= 10
        scores[player] += positions[player]
        if scores[player] >= 1000:
            break
    return (i + 1) * 3 * scores[(i + 1) % 2]


def solution_2(puzzle_input: str):
    ...


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example", 35),
        # ("input", 5571),  # not 5619, 6225
    ],
)
def test_part_1_on_file_examples(stem, expected):
    assert solution_1(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ((4, 8), 739785),
        ((10, 2), 916083),
    ],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example", 3351),
        # ("input", 17965),
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
