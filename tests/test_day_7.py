#!/usr/bin/env python3
import collections
import logging
import pathlib
import statistics

logger = logging.getLogger(__name__)

PROJECT_ROOT = pathlib.Path(__file__).parents[1]
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


def _read_population(path: pathlib.Path):
    return [int(n) for n in path.read_text().split(",")]


def _min_cost1(population):
    end = statistics.median(population)
    assert int(end) == end
    end = int(end)
    return sum(abs(start - end) for start in population)


def _min_cost2(population):
    end = round(statistics.mean(population))
    return sum(abs(start - end) * (abs(start - end) + 1) // 2 for start in population)


def solution_1(path):
    return _min_cost1(_read_population(path))


def solution_2(path):
    return _min_cost2(_read_population(path))


def test_example_1():
    actual = solution_1(INPUTS_PATH / "example.txt")
    expected = 37
    assert actual == expected


def test_input_1():
    actual = solution_1(INPUTS_PATH / "input.txt")
    expected = 342641
    assert actual == expected


def test_example_2():
    actual = solution_2(INPUTS_PATH / "example.txt")
    expected = 168
    assert actual == expected


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 93006301
    assert actual == expected
