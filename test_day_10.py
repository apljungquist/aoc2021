#!/usr/bin/env python3
import logging
import pathlib

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]

OPEN2CLOSE = {
    "(": ")",
    "[": "]",
    "{": "}",
    "<": ">",
}
CLOSE2OPEN = {v: k for k, v in OPEN2CLOSE.items()}

POINTS = {
    ")": 3,
    "]": 57,
    "}": 1197,
    ">": 25137,
}


def find_illegal(line):
    stack = []
    for c in line:
        if c in OPEN2CLOSE:
            stack.append(c)
        elif c in CLOSE2OPEN:
            if stack[-1] != CLOSE2OPEN[c]:
                return c
            stack.pop()
        else:
            assert False
    return None


def solution_1(path):
    return sum(
        POINTS.get(find_illegal(line), 0) for line in path.read_text().splitlines()
    )


def solution_2(path):
    raise NotImplementedError


def test_example_1():
    actual = solution_1(INPUTS_PATH / "example.txt")
    expected = 26397
    assert actual == expected


def test_input_1():
    actual = solution_1(INPUTS_PATH / "input.txt")
    expected = 290691
    assert actual == expected


def test_example_2():
    actual = solution_2(INPUTS_PATH / "example.txt")
    expected = 1134
    assert actual == expected


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 585648
    assert actual == expected
