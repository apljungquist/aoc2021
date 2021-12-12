#!/usr/bin/env python3
import logging
import pathlib
import statistics

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parents[1]
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

AUTOCOMPLETE_POINTS = {
    ")": 1,
    "]": 2,
    "}": 3,
    ">": 4,
}


def parse_line(line):
    stack = []
    for c in line:
        if c in OPEN2CLOSE:
            stack.append(c)
        elif c in CLOSE2OPEN:
            if stack[-1] != CLOSE2OPEN[c]:
                return stack, c
            stack.pop()
        else:
            assert False
    return stack, None


def autocomplete_score(stack):
    result = 0
    for c in stack[::-1]:
        result *= 5
        result += AUTOCOMPLETE_POINTS[OPEN2CLOSE[c]]
    return result


def solution_1(path):
    return sum(
        POINTS.get(parse_line(line)[1], 0) for line in path.read_text().splitlines()
    )


def solution_2(path):
    incomplete = [
        parse_line(line)[0]
        for line in path.read_text().splitlines()
        if parse_line(line)[1] is None
    ]
    scores = [autocomplete_score(stack) for stack in incomplete]
    return statistics.median(scores)


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
    expected = 288957
    assert actual == expected


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 2768166558
    assert actual == expected
