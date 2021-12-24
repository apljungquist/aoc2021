from __future__ import annotations

import itertools
import logging
import pathlib
import re

import more_itertools
import pytest

logger = logging.getLogger(__name__)


def _instructions(text: str):
    return [line.strip().split() for line in text.splitlines()]
    return [
        tuple(m) for m in re.findall(r"^(\w+) (-+\d+) ?(-?\d+)?$", text, re.MULTILINE)
    ]


# def _run_program(instructions, inputs):
#     registers = {"w": 0, "x": 0, "y": 0, "z": 0}
#     inputs = iter(inputs)
#     for instruction in instructions:
#         match instruction[0]:
#             case
def _run_subroutine(a, b, c, d, e, f, z, digit):
    w = digit
    x = (z % 26) + c != w
    ya = 25 * x + 1
    yb = (w + f) * x
    result = (z // b) * ya + yb
    return result


def _run_subroutine2(subroutine, z, digit):
    assert subroutine[3][0] == "mod"
    a = int(subroutine[3][2])
    assert subroutine[4][0] == "div"
    b = int(subroutine[4][2])
    assert subroutine[5][0] == "add"
    c = int(subroutine[5][2])
    assert subroutine[9][0] == "add"
    d = int(subroutine[9][2])
    assert subroutine[11][0] == "add"
    e = int(subroutine[11][2])
    assert subroutine[15][0] == "add"
    f = int(subroutine[15][2])
    return _run_subroutine(a, b, c, d, e, f, z, digit)


def format_base26(number):
    letters = []
    while number:
        letters.insert(0, f"({number % 25:02}) ")
        letters.insert(0, chr(65 + number % 26))
        number //= 26
    return "".join(letters)


def _run_program(subroutines, digits):
    z = 0
    for digit, subroutine in itertools.zip_longest(digits, subroutines):
        z = _run_subroutine2(subroutine, z, digit)
        print(digit, format_base26(z))
    return z


def _recursive_search(subroutines, old_z=0, old_path=()):
    if not subroutines:
        if not old_z:
            yield old_path
        return

    for digit in range(9, 0, -1):
        new_z = _run_subroutine2(subroutines[0], old_z, digit)
        if int(subroutines[0][4][2]) == 26:
            new = format_base26(new_z)
            old = format_base26(old_z)
            if len(old) <= len(new):
                continue
        yield from _recursive_search(subroutines[1:], new_z, old_path + (digit,))


def solution_1(puzzle_input: str):
    print()
    instructions = _instructions(puzzle_input)
    subroutines = list(more_itertools.chunked(instructions, 18))
    for digits in _recursive_search(subroutines):
        print("".join(map(str, digits)))
        break
    return int("".join(map(str, digits)))


def solution_2(puzzle_input: str):
    print()
    instructions = _instructions(puzzle_input)
    subroutines = list(more_itertools.chunked(instructions, 18))
    for digits in _recursive_search(subroutines):
        print("".join(map(str, digits)))
    return int("".join(map(str, digits)))


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example", 12521),
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
        # ("example", 44169),
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
