#!/usr/bin/env python3
import dataclasses
import enum
import functools
import logging
import operator
import pathlib
from typing import Sequence, Union

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
    digits, version = _take_int_fix_len(digits, 3)
    digits, type_id = _take_int_fix_len(digits, 3)
    if type_id == TypeId.LITERAL.value:
        return _take_literal(version, type_id, digits)
    else:
        return _take_operator(version, type_id, digits)


def _take_int_fix_len(digits, num_digit):
    return digits[num_digit:], int(digits[:num_digit], 2)


def _take_int_var_len(digits):
    segments = []
    for segment in more_itertools.chunked(digits, 5):
        segments.append("".join(segment[1:]))
        if segment[0] == "0":
            break

    value = int("".join(segments), 2)
    digits = digits[len(segments) * 5 :]
    return digits, value


def _take_literal(version, type_id, digits):
    digits, value = _take_int_var_len(digits)
    return digits, LiteralPackage(version, type_id, value)


def _take_packages_num_bit(digits, num_bit):
    allotment, digits = digits[:num_bit], digits[num_bit:]
    subpackages = []
    while allotment:
        allotment, subpackage = _take_package(allotment)
        subpackages.append(subpackage)
    return digits, subpackages


def _take_packages_num_package(digits, num_package):
    subpackages = []
    for i in range(num_package):
        digits, subpackage = _take_package(digits)
        subpackages.append(subpackage)
    return digits, subpackages


def _take_operator(version, type_id, digits):
    digits, length_type_id = _take_int_fix_len(digits, 1)
    if length_type_id == 0:
        digits, length = _take_int_fix_len(digits, 15)
        digits, subpackages = _take_packages_num_bit(digits, length)
    else:
        digits, num_subpackage = _take_int_fix_len(digits, 11)
        digits, subpackages = _take_packages_num_package(digits, num_subpackage)

    return digits, OperatorPackage(version, type_id, subpackages)


def solution_1(path):
    digits = _binary_digits(_read_input(path))
    _, package = _take_package(digits)
    return sum(package.version_numbers())


def solution_2(arg: Union[str, pathlib.Path]):
    if isinstance(arg, pathlib.Path):
        digits = _binary_digits(_read_input(arg))
    else:
        digits = _binary_digits(arg)

    _, package = _take_package(digits)
    return package.value


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
        ("input", 2536453523344),
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


@pytest.mark.parametrize(
    "digits, expected",
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
def test_part_2_on_text_examples(digits, expected):
    assert solution_2(digits) == expected
