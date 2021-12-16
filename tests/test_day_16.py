#!/usr/bin/env python3
import dataclasses
import enum
import logging
import pathlib
from typing import Sequence

import more_itertools
import pytest

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")


def _read_input(path: pathlib.Path) -> str:
    return path.read_text().strip()


def _binary_digits(hex_digits) -> str:
    return "".join(f"{int(digit, 16):04b}" for digit in hex_digits)


@dataclasses.dataclass(frozen=True)
class Package:
    version: int
    type_id: int

    def version_numbers(self):
        yield self.version


@dataclasses.dataclass(frozen=True)
class LiteralPackage(Package):
    value: int


@dataclasses.dataclass(frozen=True)
class OperatorPackage(Package):
    subpackages: Sequence[Package]

    def version_numbers(self):
        yield from super().version_numbers()
        for package in self.subpackages:
            yield from package.version_numbers()


class TypeId(enum.IntEnum):
    LITERAL = 4


def _take_package(digits):
    version = int(digits[:3], 2)
    type_id = int(digits[3:6], 2)
    if type_id == TypeId.LITERAL.value:
        return _take_literal(version, type_id, digits[6:])
    else:
        return _take_operator(version, type_id, digits[6:])


def _take_literal(version, type_id, digits):
    segments = []
    for segment in more_itertools.chunked(digits, 5):
        segments.append("".join(segment[1:]))
        if segment[0] == "0":
            break

    value = int("".join(segments), 2)

    num_consumed = len(segments) * 5
    # while num_consumed % 4:
    #     num_consumed += 1
    residual = digits[num_consumed:]

    return residual, LiteralPackage(version, type_id, value)


def _take_operator(version, type_id, digits):
    length_type_id = int(digits[0], 2)
    if length_type_id == 0:
        length = int(digits[1:16], 2)
        residual = digits[16 : 16 + length]
        subpackages = []
        while residual:
            residual, subpackage = _take_package(residual)
            subpackages.append(subpackage)

        residual = digits[16 + length :]
    else:
        num_subpackage = int(digits[1:12], 2)
        subpackages = []
        residual = digits[12:]
        for i in range(num_subpackage):
            residual, subpackage = _take_package(residual)
            subpackages.append(subpackage)

    return residual, OperatorPackage(version, type_id, subpackages)


def solution_1(path):
    digits = _binary_digits(_read_input(path))
    _, package = _take_package(digits)
    return sum(package.version_numbers())


def solution_2(path):
    raise NotImplementedError


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 16),
        ("example_2", 12),
        ("example_3", 23),
        ("example_4", 31),
        ("input", 917),
    ],
)
def test_part_1_on_examples(stem, expected):
    assert solution_1(INPUTS_PATH / f"{stem}.txt") == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 315),
        ("input", 2858),
    ],
)
def test_part_2_on_examples(stem, expected):
    assert solution_2(INPUTS_PATH / f"{stem}.txt") == expected


def test_expand_to_binary():
    assert _binary_digits("D2FE28") == "110100101111111000101000"


def test_take_literal():
    residual, package = _take_package("110100101111111000101000")
    assert (residual, package.value) == ("000", 2021)


def test_take_operator_0():
    residual, package = _take_package(
        "00111000000000000110111101000101001010010001001000000000"
    )
    assert isinstance(package, OperatorPackage)
    assert (residual, len(package.subpackages)) == ("0000000", 2)


def test_take_operator_1():
    residual, package = _take_package(
        "11101110000000001101010000001100100000100011000001100000"
    )
    assert isinstance(package, OperatorPackage)
    assert (residual, len(package.subpackages)) == ("00000", 3)
    assert package.subpackages[0].value == 1
    assert package.subpackages[1].value == 2
    assert package.subpackages[2].value == 3
