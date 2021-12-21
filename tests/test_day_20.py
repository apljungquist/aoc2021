import collections
import dataclasses
import functools
import logging
import operator
import pathlib
from typing import Mapping, Sequence, Tuple

import more_itertools
import pytest

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=512)
def _int_from_digits(digits: Sequence[bool]) -> int:
    result = 0
    for digit in digits:
        result = (result << 1) + digit
    return result


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def _parse_lut(line):
    result = [c == "#" for c in line]
    assert len(result) == 512
    return result


def _parse_img(lines):
    result = collections.defaultdict(lambda: False)
    for row_num, line in enumerate(lines):
        for col_num, pixel in enumerate(line):
            result[(row_num, col_num)] = pixel == "#"

    return result


@dataclasses.dataclass(frozen=True)
class Image:
    pixels: Mapping[Tuple[int, int], bool]
    padding: bool
    min_row: int
    max_row: int
    min_col: int
    max_col: int


def _enhanced_1(img: Image, lut):
    if img.padding:
        new_padding = lut[-1]
    else:
        new_padding = lut[0]

    old_pixels = img.pixels
    new_pixels = collections.defaultdict(lambda: new_padding)
    for row_num in range(img.min_row - 1, img.max_row + 2):
        for col_num in range(img.min_col - 1, img.max_col + 2):
            digits = (
                old_pixels[row_num - 1, col_num - 1],
                old_pixels[row_num - 1, col_num],
                old_pixels[row_num - 1, col_num + 1],
                old_pixels[row_num, col_num - 1],
                old_pixels[row_num, col_num],
                old_pixels[row_num, col_num + 1],
                old_pixels[row_num + 1, col_num - 1],
                old_pixels[row_num + 1, col_num],
                old_pixels[row_num + 1, col_num + 1],
            )
            index = _int_from_digits(digits)
            new_pixels[row_num, col_num] = lut[index]

    return Image(
        pixels=new_pixels,
        padding=new_padding,
        min_row=img.min_row - 1,
        max_row=img.max_row + 1,
        min_col=img.min_col - 1,
        max_col=img.max_col + 1,
    )


def _enhanced_n(pixels, lut, n):
    min_row, max_row = more_itertools.minmax(map(operator.itemgetter(0), pixels))
    min_col, max_col = more_itertools.minmax(map(operator.itemgetter(1), pixels))
    assert len(pixels) == (max_row - min_row + 1) * (max_col - min_col + 1)
    img = Image(
        pixels=pixels,
        padding=False,
        min_row=min_row,
        max_row=max_row,
        min_col=min_col,
        max_col=max_col,
    )
    for _ in range(n):
        img = _enhanced_1(img, lut)
    assert img.padding is False  # or counting light pixels would not make sense
    return img.pixels


def _parse_input(text):
    lines = text.splitlines()
    return _parse_lut(lines[0]), _parse_img(lines[2:])


def solution_1(puzzle_input: str):
    lut, img_in = _parse_input(puzzle_input)
    img_out = _enhanced_n(img_in, lut, 2)
    return sum(img_out.values())


def solution_2(puzzle_input: str):
    lut, img_in = _parse_input(puzzle_input)
    img_out = _enhanced_n(img_in, lut, 50)
    return sum(img_out.values())


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example", 35),
        # ("input", 5571),  # not 5619, 6225
    ],
)
def test_part_1_on_file_examples(stem, expected):
    assert solution_1(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [({1: 4, 2: 8}, 739785)],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example", 3351),
        # ("input", 17965),
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
