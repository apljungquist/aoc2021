#!/usr/bin/env python3

import logging
import pathlib
import textwrap

import fire as fire
import more_itertools
import pytest

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parents[1]


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


def test_solution_2_by_example():
    assert solution_2(PROJECT_ROOT / "day" / "1" / "example2.txt") == 5


def solution_2(path):
    path = pathlib.Path(path)
    text = path.read_text()
    nums = [int(line.strip().split()[0]) for line in text.splitlines()]
    sums = [sum(triple) for triple in more_itertools.triplewise(nums)]
    return sum(left < right for left, right in more_itertools.pairwise(sums))


if __name__ == "__main__":
    fire.Fire()
