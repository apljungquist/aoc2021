#!/usr/bin/env python3

import logging
import pathlib
import textwrap

import fire as fire
import more_itertools
import pytest

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parents[1]
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


@pytest.mark.parametrize(
    "text, result",
    [
        (
            textwrap.dedent(
                """\
                    199
                    200
                    208
                    210
                    200
                    207
                    240
                    269
                    260
                    263
                    """
            ),
            7,
        )
    ],
)
def test_solution_1_by_example(text, result):
    assert solution_1(text) == result


def solution_1(text):
    try:
        text = pathlib.Path(text).read_text()
    except FileNotFoundError:
        pass
    distances = [int(line.strip()) for line in text.splitlines()]
    return sum(left < right for left, right in more_itertools.pairwise(distances))


def solution_2(path):
    path = pathlib.Path(path)
    text = path.read_text()
    nums = [int(line.strip().split()[0]) for line in text.splitlines()]
    sums = [sum(triple) for triple in more_itertools.triplewise(nums)]
    return sum(left < right for left, right in more_itertools.pairwise(sums))


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 7),
        ("input", 1139),
    ],
)
def test_part_1_on_examples(stem, expected):
    assert solution_1(INPUTS_PATH / f"{stem}.txt") == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 5),
        ("input", 1103),
    ],
)
def test_part_2_on_examples(stem, expected):
    assert solution_2(INPUTS_PATH / f"{stem}.txt") == expected


if __name__ == "__main__":
    fire.Fire()
