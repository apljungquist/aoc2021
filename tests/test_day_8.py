#!/usr/bin/env python3
import dataclasses
import itertools
import logging
import pathlib
from typing import Tuple

import more_itertools
import pytest

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parents[1]
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


@dataclasses.dataclass
class Entry:
    train_digits: Tuple[str, str, str, str, str, str, str, str, str, str]
    test_digits: Tuple[str, str, str, str]

    @staticmethod
    def from_line(line):
        signal, digit = line.split("|")
        return Entry(
            tuple(map(str.strip, signal.split())),
            tuple(map(str.strip, digit.split())),
        )


def _read_entries(path: pathlib.Path):
    return [Entry.from_line(line) for line in path.read_text().splitlines()]


LETTERS = {
    0: frozenset("abcefg"),
    1: frozenset("cf"),
    2: frozenset("acdeg"),
    3: frozenset("acdfg"),
    4: frozenset("bcdf"),
    5: frozenset("abdfg"),
    6: frozenset("abdefg"),
    7: frozenset("acf"),
    8: frozenset("abcdefg"),
    9: frozenset("abcdfg"),
}


def _key(digits):
    by_length = more_itertools.map_reduce(
        digits,
        valuefunc=frozenset,
        keyfunc=len,
    )

    one = more_itertools.one(by_length[2])
    four = more_itertools.one(by_length[4])
    seven = more_itertools.one(by_length[3])
    eight = more_itertools.one(by_length[7])

    three = more_itertools.one(d for d in by_length[5] if d.issuperset(one))
    six = more_itertools.one(d for d in by_length[6] if not d.issuperset(one))
    b = more_itertools.one(four - three)

    two = more_itertools.one(d for d in by_length[5] if d != three and b not in d)
    five = more_itertools.one(d for d in by_length[5] if d != three and b in d)
    e = more_itertools.one(six - five)

    zero = more_itertools.one(d for d in by_length[6] if d != six and e in d)
    nine = more_itertools.one(d for d in by_length[6] if d != six and e not in d)

    result = {
        zero: 0,
        one: 1,
        two: 2,
        three: 3,
        four: 4,
        five: 5,
        six: 6,
        seven: 7,
        eight: 8,
        nine: 9,
    }
    assert len(result) == 10
    return result


def _decoded(digits, key):
    decoded_digits = [key[frozenset(display)] for display in digits]
    return int("".join(map(str, decoded_digits)))


def _cracked_and_decoded(entry):
    key = _key(entry.train_digits)
    return _decoded(entry.test_digits, key)


def solution_1(path):
    return more_itertools.ilen(
        d
        for d in itertools.chain.from_iterable(
            entry.test_digits for entry in _read_entries(path)
        )
        if len(d) in {2, 3, 4, 7}
    )


def solution_2(path):
    entries = _read_entries(path)
    return sum(_cracked_and_decoded(entry) for entry in entries)


def test_decode_original():
    key = _key(LETTERS.values())
    assert _decoded([LETTERS[int(i)] for i in "1234567890"], key) == 1234567890


@pytest.mark.parametrize(
    "entry, expected",
    list(
        itertools.zip_longest(
            _read_entries(INPUTS_PATH / "example.txt"),
            [8394, 9781, 1197, 9361, 4873, 8418, 4548, 1625, 8717, 4315],
        )
    ),
)
def test_decode_entry(entry, expected):
    key = _key(entry.train_digits)
    assert _decoded(entry.test_digits, key) == expected


def test_example_1():
    actual = solution_1(INPUTS_PATH / "example.txt")
    expected = 26
    assert actual == expected


def test_input_1():
    actual = solution_1(INPUTS_PATH / "input.txt")
    expected = 470
    assert actual == expected


def test_example_2():
    actual = solution_2(INPUTS_PATH / "example.txt")
    expected = 61229
    assert actual == expected


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 989396
    assert actual == expected
