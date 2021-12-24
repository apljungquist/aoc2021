from __future__ import annotations

import dataclasses
import functools
import logging
import pathlib
from typing import Sequence

import more_itertools
import pytest

logger = logging.getLogger(__name__)


def _instructions(text: str):
    return [line.strip().split() for line in text.splitlines()]


@dataclasses.dataclass(frozen=True)
class Subroutine:
    b: int
    c: int
    f: int

    @staticmethod
    def from_instructions(instructions):
        assert instructions[4][0] == "div"
        b = int(instructions[4][2])
        assert instructions[5][0] == "add"
        c = int(instructions[5][2])
        assert instructions[15][0] == "add"
        f = int(instructions[15][2])
        return Subroutine(b, c, f)

    def __call__(self, w, z):
        x = (z % 26) + self.c != w
        ya = 25 * x + 1
        yb = (w + self.f) * x
        return (z // self.b) * ya + yb


def _subroutines(instructions):
    return [
        Subroutine.from_instructions(chunk)
        for chunk in more_itertools.chunked(instructions, 18)
    ]


def _fmt_int(number: int, digits: Sequence[str]) -> str:
    base = len(digits)
    indices = []
    while number:
        indices.append(number % base)
        number //= base
    return "".join(digits[i] for i in indices[::-1])


_fmt_int_b26 = functools.partial(_fmt_int, digits="ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def _recursive_search(subroutines, old_z=0, old_path=(), reverse=True):
    if not subroutines:
        if not old_z:
            yield old_path
        return

    if reverse:
        digits = range(9, 0, -1)
    else:
        digits = range(1, 10)

    old = _fmt_int_b26(old_z)
    for digit in digits:
        new_z = subroutines[0](digit, old_z)
        if subroutines[0].b == 26:
            new = _fmt_int_b26(new_z)
            if len(old) <= len(new):
                continue
        yield from _recursive_search(
            subroutines[1:], new_z, old_path + (digit,), reverse
        )


def solution_1(puzzle_input: str):
    subroutines = _subroutines(_instructions(puzzle_input))
    digits = more_itertools.first(_recursive_search(subroutines, reverse=True))
    return int("".join(map(str, digits)))


def solution_2(puzzle_input: str):
    subroutines = _subroutines(_instructions(puzzle_input))
    digits = more_itertools.first(_recursive_search(subroutines, reverse=False))
    return int("".join(map(str, digits)))


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("input", 41299994879959),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    actual = solution_1(_read_input(stem))
    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("input", 11189561113216),
    ],
)
def test_part_2_on_file_examples(stem, expected):
    assert solution_2(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [],
)
def test_part_2_on_text_examples(text, expected):
    assert solution_2(text) == expected
