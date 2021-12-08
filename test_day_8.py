#!/usr/bin/env python3
import dataclasses
import itertools
import logging
import pathlib
from pprint import pprint
from typing import Dict, Set, Tuple

import more_itertools
import pytest

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


@dataclasses.dataclass
class Entry:
    signal_group: Tuple[str, str, str, str, str, str, str, str, str, str]
    digit_group: Tuple[str, str, str, str]

    @staticmethod
    def from_line(line):
        signal, digit = line.split("|")
        return Entry(
            tuple(map(str.strip, signal.split())),
            tuple(map(str.strip, digit.split())),
        )


def _read_entries(path: pathlib.Path):
    return [Entry.from_line(line) for line in path.read_text().splitlines()]


def _decode(entry: Entry):
    d = Display()
    samples = list(itertools.chain(entry.signal_group, entry.digit_group))
    print()
    print(samples)
    print(["".join(sorted(sample)) for sample in samples])
    for sample in samples:
        d.observe(sample)
    pprint(sorted((k, sorted(v)) for k, v in d._map.items()))
    d.deduce1()
    pprint(sorted((k, sorted(v)) for k, v in d._map.items()))
    d.deduce2()
    pprint(sorted((k, sorted(v)) for k, v in d._map.items()))
    return 0


LENGTHS = {
    0: 6,
    1: 2,
    2: 5,
    3: 5,
    4: 4,
    5: 5,
    6: 6,
    7: 3,
    8: 7,
    9: 6,
}
REV_LENGTHS = {}
for k, v in LENGTHS.items():
    REV_LENGTHS.setdefault(v, set())
    REV_LENGTHS[v].add(k)
pprint(REV_LENGTHS)
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


def test_foo():
    print()
    pprint({k: len(v) for k, v in LETTERS.items()})
    pprint(LENGTHS)
    assert {k: len(v) for k, v in LETTERS.items()} == LENGTHS


class Display:
    def __init__(self):
        self._map = {k: set("abcdefg") for k in "abcdefg"}

    def expected(self, text):
        return {frozenset(LETTERS[k]) for k in REV_LENGTHS[len(text)]}

    def observe(self, actual):
        actual = set(actual)
        possibilities = REV_LENGTHS[len(actual)]
        assert possibilities
        if len(possibilities) > 1:
            return
        possibility = more_itertools.one(possibilities)
        for k in actual:
            old = self._map[k]
            new = old & set(LETTERS[possibility])
            assert new
            self._map[k] = new
        if possibility == 1:
            ks = LETTERS[8] - actual
            for k in ks:
                old = self._map[k]
                new = old - LETTERS[1]
                assert new
                self._map[k] = new

    def deduce1(self):
        ks = set(LETTERS[8])
        making_progress = True
        while making_progress:
            making_progress = False
            for k in list(ks):
                try:
                    v = more_itertools.one(self._map[k])
                except ValueError:
                    continue
                for vs in self._map.values():
                    if len(vs) > 1 and v in vs:
                        vs.remove(v)
                ks.remove(k)
            if not ks:
                break

    def deduce2(self):
        for x in _possible_mappings(self._map):
            print(x)
        self._map = more_itertools.one(_possible_mappings(self._map))

    def decode(self, text):
        ...


def _possible_mappings(mapping: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    if any(len(vs) == 0 for vs in mapping.values()):
        return
    if all(len(vs) == 1 for vs in mapping.values()):
        yield mapping
    for k, vs in mapping.items():
        if len(vs) == 1:
            continue
        for v in vs:
            yield from _possible_mappings(
                {kk: {v} if kk == k else vv - {v} for kk, vv in mapping.items()}
            )


def solution_1(path):
    return sum(
        1 if len(text) in {2, 3, 4, 7} else 0
        for text in itertools.chain.from_iterable(
            entry.digit_group for entry in _read_entries(path)
        )
    )


def solution_2(path):
    entries = _read_entries(path)
    result = 0
    for entry in entries:
        key = _key(entry.signal_group)
        result += _decoded(entry.digit_group, key)
    return result


def test_example_1():
    actual = solution_1(INPUTS_PATH / "example.txt")
    expected = 26
    assert actual == expected


def test_input_1():
    actual = solution_1(INPUTS_PATH / "input.txt")
    expected = 470
    assert actual == expected


def _key(displays):
    by_length = more_itertools.map_reduce(
        map(frozenset, displays),
        keyfunc=len,
    )
    _1 = more_itertools.one(by_length[2])
    _4 = more_itertools.one(by_length[4])
    _7 = more_itertools.one(by_length[3])
    _8 = more_itertools.one(by_length[7])
    _3 = more_itertools.one(digit for digit in by_length[5] if digit.issuperset(_1))
    _6 = more_itertools.one(digit for digit in by_length[6] if not digit.issuperset(_1))
    b = more_itertools.one(_4 - _3)
    _2 = more_itertools.one(
        digit for digit in by_length[5] if digit != _3 and b not in digit
    )
    _5 = more_itertools.one(
        digit for digit in by_length[5] if digit != _3 and b in digit
    )
    e = more_itertools.one(_6 - _5)
    _0 = more_itertools.one(
        digit for digit in by_length[6] if digit != _6 and e in digit
    )
    _9 = more_itertools.one(
        digit for digit in by_length[6] if digit != _6 and e not in digit
    )
    result = {
        _0: 0,
        _1: 1,
        _2: 2,
        _3: 3,
        _4: 4,
        _5: 5,
        _6: 6,
        _7: 7,
        _8: 8,
        _9: 9,
    }
    assert len(result) == 10
    return result


def _decoded(displays, key):
    decoded_digits = [key[frozenset(display)] for display in displays]
    return int("".join(map(str, decoded_digits)))


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
    key = _key(entry.signal_group)
    assert _decoded(entry.digit_group, key) == expected


def test_example_2():
    actual = solution_2(INPUTS_PATH / "example.txt")
    expected = 61229
    assert actual == expected


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 989396
    assert actual == expected
