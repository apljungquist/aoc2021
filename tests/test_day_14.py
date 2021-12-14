#!/usr/bin/env python3
import collections
import logging
import pathlib
import re

import more_itertools
import pytest

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")


def _read_template(path: pathlib.Path):
    line = more_itertools.first(path.read_text().splitlines()) + " "
    return collections.Counter(more_itertools.pairwise(line))


def _read_rules(path: pathlib.Path):
    return {
        (m[0][0], m[0][1]): m[1]
        for m in re.findall(r"([A-Z]{2}) -> ([A-Z])", path.read_text(), re.MULTILINE)
    }


def _insert(polymer, rules):
    result = collections.defaultdict(int)
    for (left, right), count in polymer.items():
        try:
            middle = rules[left, right]
            result[left, middle] += count
            result[middle, right] += count
        except KeyError:
            result[left, right] = count
    return result


def _count_elements(polymer):
    result = collections.defaultdict(int)
    for (l, _), v in polymer.items():
        result[l] += v
    return result


def _score(counter):
    lo, hi = more_itertools.minmax(counter.values())
    return hi - lo


def solution_1(path):
    polymer = _read_template(path)
    rules = _read_rules(path)
    for _ in range(10):
        polymer = _insert(polymer, rules)
    return _score(_count_elements(polymer))


def solution_2(path):
    polymer = _read_template(path)
    rules = _read_rules(path)
    for _ in range(40):
        polymer = _insert(polymer, rules)
    return _score(_count_elements(polymer))


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 1588),
        ("input", 2233),
    ],
)
def test_part_1_on_examples(stem, expected):
    assert solution_1(INPUTS_PATH / f"{stem}.txt") == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 2188189693529),
        ("input", 2884513602164),
    ],
)
def test_part_2_on_examples(stem, expected):
    assert solution_2(INPUTS_PATH / f"{stem}.txt") == expected
