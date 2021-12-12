#!/usr/bin/env python3
import collections
import logging
import pathlib

logger = logging.getLogger(__name__)

PROJECT_ROOT = pathlib.Path(__file__).parents[1]
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


def _read_population(path: pathlib.Path):
    return collections.Counter(int(n) for n in path.read_text().split(","))


def _cost1(population, n):
    return sum(abs(n - k) * v for k, v in population.items())


def _cost2(population, n):
    return sum(abs(n - k) * (abs(n - k) + 1) // 2 * v for k, v in population.items())


def _min_cost(population, cost):
    return min(cost(population, i) for i in range(max(population)))


def solution_1(path):
    return _min_cost(_read_population(path), _cost1)


def solution_2(path):
    return _min_cost(_read_population(path), _cost2)


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
