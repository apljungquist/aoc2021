#!/usr/bin/env python3
import collections
import logging
import pathlib

import more_itertools

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


def test_gamma_rate():
    assert _gamma_rate(INPUTS_PATH / "example.txt") == 22


def test_epsilon_rate():
    assert _epsilon_rate(INPUTS_PATH / "example.txt") == 9


def test_example_1():
    assert solution_1(INPUTS_PATH / "example.txt") == 198


def test_input_1():
    assert solution_1(INPUTS_PATH / "input.txt") == 2954600


def test_oxygen_rating():
    assert _oxygen_rating(INPUTS_PATH / "example.txt") == 23


def test_carbon_rating():
    assert _carbon_rating(INPUTS_PATH / "example.txt") == 10


def test_example_2():
    assert solution_2(INPUTS_PATH / "example.txt") == 230


def test_input_2():
    assert solution_2(INPUTS_PATH / "input.txt") == 1662846


def _gamma_rate(path):
    lines = path.read_text().splitlines()
    cols = list(zip(*lines))

    result = ""
    for col in cols:
        counter = collections.Counter(col)
        if counter["0"] < counter["1"]:
            result += "1"
        elif counter["1"] < counter["0"]:
            result += "0"
        else:
            assert False
    return int(result, 2)


def _epsilon_rate(path):
    lines = path.read_text().splitlines()
    cols = list(zip(*lines))

    result = ""
    for col in cols:
        counter = collections.Counter(col)
        if counter["0"] < counter["1"]:
            result += "0"
        elif counter["1"] < counter["0"]:
            result += "1"
        else:
            assert False
    return int(result, 2)


def _oxygen_rating(path):
    lines = path.read_text().splitlines()
    result = ""
    for i in range(max(map(len, lines))):
        col = [line[i] for line in lines]
        counter = collections.Counter(col)
        if counter["0"] < counter["1"]:
            result += "1"
        elif counter["1"] < counter["0"]:
            result += "0"
        else:
            result += "1"
        lines = [line for line in lines if line[i] == result[i]]
        if len(lines) == 1:
            result = "".join(more_itertools.one(lines))
            break
    return int(result, 2)


def _carbon_rating(path):
    lines = path.read_text().splitlines()
    result = ""
    for i in range(max(map(len, lines))):
        col = [line[i] for line in lines]
        counter = collections.Counter(col)
        if counter["0"] < counter["1"]:
            result += "0"
        elif counter["1"] < counter["0"]:
            result += "1"
        else:
            result += "0"
        lines = [line for line in lines if line[i] == result[i]]
        if len(lines) == 1:
            result = "".join(more_itertools.one(lines))
            break
    return int(result, 2)


def solution_1(path):
    return _gamma_rate(path) * _epsilon_rate(path)


def solution_2(path):
    return _oxygen_rating(path) * _carbon_rating(path)
