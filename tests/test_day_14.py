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
    return list(more_itertools.first(path.read_text().splitlines()))


def _read_rules(path: pathlib.Path):
    return {
        (m[0][0], m[0][1]): m[1]
        for m in re.findall(r"([A-Z]{2}) -> ([A-Z])", path.read_text(), re.MULTILINE)
    }


def _insert(polymer, rules):
    return list(
        more_itertools.flatten(
            [
                [a, rules[a, b]] if (a, b) in rules else [a]
                for a, b in more_itertools.pairwise(polymer)
            ]
        )
    ) + [polymer[-1]]


def _insert_repeatedly(polymer, rules, n):
    return polymer


def solution_1(path):
    polymer = _read_template(path)
    rules = _read_rules(path)
    # assert "".join(polymer) == "NNCB"
    # # 1
    # polymer = _insert(polymer, rules)
    # assert "".join(polymer) == "NCNBCHB"
    # # 2
    # polymer = _insert(polymer, rules)
    # assert "".join(polymer) == "NBCCNBBBCBHCB"
    # # 3
    # polymer = _insert(polymer, rules)
    # assert "".join(polymer) == "NBBBCNCCNBBNBNBBCHBHHBCHB"
    # # 4
    # polymer = _insert(polymer, rules)
    # assert "".join(polymer) == "NBBNBNBBCCNBCNCCNBBNBBNBBBNBBNBBCBHCBHHNHCBBCBHCB"
    # # 5
    # polymer = _insert(polymer, rules)
    # assert len(polymer) == 97

    for _ in range(10):
        print("".join(polymer))
        polymer = _insert(polymer, rules)
    # assert len(polymer) == 3073

    counter = collections.Counter(polymer)
    lo, hi = more_itertools.minmax(counter.values())
    return hi - lo


def solution_2(path):
    raise NotImplementedError


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
        ("example", "O"),
        ("input", "PZEHRAER"),
    ],
)
def test_part_2_on_examples(stem, expected):
    assert solution_2(INPUTS_PATH / f"{stem}.txt") == expected
