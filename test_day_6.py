#!/usr/bin/env python3
import collections
import logging
import pathlib

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


def _read_population(path: pathlib.Path):
    return collections.Counter(int(n) for n in path.read_text().split(","))


def _next_population(old):
    new = collections.defaultdict(int)
    for k, v in old.items():
        if k:
            new[k - 1] += v
        else:
            new[6] += v
            new[8] += v
    return new


def _simulate(population, num_day):
    for _ in range(num_day):
        population = _next_population(population)
    return population


def _size(population):
    return sum(population.values())


def solution_1(path, num_day=80):
    return _size(_simulate(_read_population(path), num_day))


def solution_2(path):
    return solution_1(path, 256)


def test_example_1_day_18():
    assert solution_1(INPUTS_PATH / "example.txt", 18) == 26


def test_example_1():
    assert solution_1(INPUTS_PATH / "example.txt") == 5934


def test_input_1():
    assert solution_1(INPUTS_PATH / "input.txt") == 372300


def test_example_2():
    assert solution_2(INPUTS_PATH / "example.txt") == 26984457539


def test_input_2():
    assert (
        solution_2(
            INPUTS_PATH / "input.txt",
        )
        == 1675781200288
    )
