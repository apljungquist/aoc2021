#!/usr/bin/env python3
import dataclasses
import enum
import functools
import logging
import operator
import pathlib
from typing import Sequence

import more_itertools
import pytest

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")


def _binary_digits(hex_digits) -> str:
    return "".join(f"{int(digit, 16):04b}" for digit in hex_digits.strip())


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

    @property
    def value(self):
        values = [p.value for p in self.subpackages]
        if self.type_id == 0:
            return sum(values)
        elif self.type_id == 1:
            return functools.reduce(operator.mul, values)
        elif self.type_id == 2:
            return min(values)
        elif self.type_id == 3:
            return max(values)
        elif self.type_id == 5:
            return int(operator.gt(*values))
        elif self.type_id == 6:
            return int(operator.lt(*values))
        elif self.type_id == 7:
            return int(operator.eq(*values))
        else:
            assert False


class TypeId(enum.IntEnum):
    SUM = 0
    PRODUCT = 1
    MINIMUM = 2
    MAXIMUM = 3
    LITERAL = 4
    GREATER_THAN = 5
    LESS_THAN = 6
    EQUAL_TO = 7


def _take_package(digits):
    digits = iter(digits)
    version = _take_int_fix_len(digits, 3)
    type_id = _take_int_fix_len(digits, 3)
    if type_id == TypeId.LITERAL.value:
        return _take_literal(version, type_id, digits)
    else:
        return _take_operator(version, type_id, digits)


def _take_int_fix_len(digits, num_digit):
    return int("".join(more_itertools.take(num_digit, digits)), 2)


def _take_int_var_len(digits):
    segments = []
    for segment in more_itertools.chunked(digits, 5):
        segments.append("".join(segment[1:]))
        if segment[0] == "0":
            break

    return int("".join(segments), 2)


def _take_literal(version, type_id, digits):
    value = _take_int_var_len(digits)
    return LiteralPackage(version, type_id, value)


def _take_packages_num_bit(digits, num_bit):
    allotment = more_itertools.peekable(more_itertools.take(num_bit, digits))
    subpackages = []
    while allotment:
        subpackage = _take_package(allotment)
        subpackages.append(subpackage)
    return subpackages


def _take_packages_num_package(digits, num_package):
    subpackages = []
    for i in range(num_package):
        subpackage = _take_package(digits)
        subpackages.append(subpackage)
    return subpackages


def _take_operator(version, type_id, digits):
    length_type_id = _take_int_fix_len(digits, 1)
    if length_type_id == 0:
        length = _take_int_fix_len(digits, 15)
        subpackages = _take_packages_num_bit(digits, length)
    else:
        num_subpackage = _take_int_fix_len(digits, 11)
        subpackages = _take_packages_num_package(digits, num_subpackage)

    return OperatorPackage(version, type_id, subpackages)


def solution_1(puzzle_input: str):
    digits = _binary_digits(puzzle_input)
    package = _take_package(digits)
    return sum(package.version_numbers())


def solution_2(puzzle_input: str):
    digits = _binary_digits(puzzle_input)
    package = _take_package(digits)
    return package.value


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("input", 917),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    path = INPUTS_PATH / f"{stem}.txt"
    text = path.read_text()
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("8A004A801A8002F478", 16),
        ("620080001611562C8802118E34", 12),
        ("C0015000016115A2E0802F182340", 23),
        ("A0016C880162017C3686B18A3D4780", 31),
    ],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("input", 2536453523344),
    ],
)
def test_part_2_on_file_examples(stem, expected):
    path = INPUTS_PATH / f"{stem}.txt"
    text = path.read_text()
    assert solution_2(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("C200B40A82", 3),
        ("04005AC33890", 54),
        ("880086C3E88112", 7),
        ("CE00C43D881120", 9),
        ("D8005AC2A8F0", 1),
        ("F600BC2D8F", 0),
        ("9C005AC2F8F0", 0),
        ("9C0141080250320F1802104A08", 1),
    ],
)
def test_part_2_on_text_examples(text, expected):
    assert solution_2(text) == expected


def test_expand_to_binary():
    assert _binary_digits("D2FE28") == "110100101111111000101000"


def test_take_literal():
    package = _take_package("110100101111111000101000")
    assert package.value == 2021


def test_take_operator_0():
    package = _take_package("00111000000000000110111101000101001010010001001000000000")
    assert isinstance(package, OperatorPackage)
    assert len(package.subpackages) == 2


def test_take_operator_1():
    package = _take_package("11101110000000001101010000001100100000100011000001100000")
    assert isinstance(package, OperatorPackage)
    assert len(package.subpackages) == 3
    assert package.subpackages[0].value == 1
    assert package.subpackages[1].value == 2
    assert package.subpackages[2].value == 3
