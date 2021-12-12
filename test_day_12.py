#!/usr/bin/env python3
import collections
import itertools
import logging
import operator
import pathlib
import textwrap

import more_itertools
import pytest

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


def _read_graph(path: pathlib.Path):
    result = collections.defaultdict(set)
    for line in path.read_text().splitlines():
        left, right = line.split("-")
        result[left].add(right)
        result[right].add(left)
    return result


def _paths(graph: dict[str, str]):
    return _paths_helper(
        graph, frozenset(k for k in graph if k.islower() and k != "start"), ("start",)
    )


def _paths_helper(graph: dict[str, str], remaining: frozenset[str], path):
    if path[-1] == "end":
        yield path
        return

    for dst in graph[path[-1]]:
        if dst.isupper() or dst in remaining:
            new_remaining = frozenset(x for x in remaining if x != dst)
            new_path = path + (dst,)
            yield from _paths_helper(graph, new_remaining, new_path)


def solution_1(path):
    graph = _read_graph(path)
    return more_itertools.ilen(_paths(graph))


def solution_2(path):
    raise NotImplementedError


def test_example_1():
    actual = solution_1(INPUTS_PATH / "example.txt")
    expected = 10
    assert actual == expected


def test_large_example_1():
    actual = solution_1(INPUTS_PATH / "large_example.txt")
    expected = 19
    assert actual == expected


def test_larger_example_1():
    actual = solution_1(INPUTS_PATH / "larger_example.txt")
    expected = 226
    assert actual == expected


def test_input_1():
    actual = solution_1(INPUTS_PATH / "input.txt")
    expected = 4720
    assert actual == expected


def test_example_2():
    actual = solution_2(INPUTS_PATH / "example.txt")
    expected = 195
    assert actual == expected


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 494
    assert actual == expected
