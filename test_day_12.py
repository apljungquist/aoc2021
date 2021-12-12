#!/usr/bin/env python3
import collections
import logging
import pathlib

import more_itertools

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


def _paths(graph: dict[str, str], num_extra=0):
    return _paths_helper(
        graph,
        frozenset(k for k in graph if k != "start"),
        ("start",),
        num_extra,
    )


def _paths_helper(graph: dict[str, str], allowed: frozenset[str], path, num_extra):
    assert num_extra >= 0
    if path[-1] == "end":
        yield path
        return

    for dst in graph[path[-1]]:
        if dst == "start":
            continue

        if dst in allowed:
            new_num_extra = num_extra
        elif num_extra:
            new_num_extra = num_extra - 1
        else:
            continue

        if dst.islower():
            new_allowed = allowed - {dst}
        else:
            new_allowed = allowed

        new_path = path + (dst,)
        yield from _paths_helper(graph, new_allowed, new_path, new_num_extra)


def solution_1(path):
    graph = _read_graph(path)
    return more_itertools.ilen(_paths(graph))


def solution_2(path):
    graph = _read_graph(path)
    return more_itertools.ilen(_paths(graph, 1))


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
    expected = 36
    assert actual == expected


def test_large_example_2():
    actual = solution_2(INPUTS_PATH / "large_example.txt")
    expected = 103
    assert actual == expected


def test_larger_example_2():
    actual = solution_2(INPUTS_PATH / "larger_example.txt")
    expected = 3509
    assert actual == expected


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 147848
    assert actual == expected
