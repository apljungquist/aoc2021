#!/usr/bin/env python3
import collections
import logging
import pathlib
import statistics

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
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
    assert solution_1(INPUTS_PATH / "example.txt") == 37


def test_input_1():
    assert solution_1(INPUTS_PATH / "input.txt") == 342641


def test_example_2():
    assert solution_2(INPUTS_PATH / "example.txt") == 168


def test_input_2():
    assert (
        solution_2(
            INPUTS_PATH / "input.txt",
        )
        == 93006301
    )
