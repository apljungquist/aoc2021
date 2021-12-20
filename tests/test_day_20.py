import logging
import operator
import pathlib

import more_itertools
import pytest

logger = logging.getLogger(__name__)


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def _parse_lut(line):
    result = [c == "#" for c in line]
    assert len(result) == 512
    return result


def _parse_img(lines):
    return {
        (row_num, col_num): pixel == "#"
        for row_num, line in enumerate(lines)
        for col_num, pixel in enumerate(line)
    }


def _neighbors(row, col):
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            yield row + dr, col + dc


def _enhanced_1(img, lut, padding):
    min_row, max_row = more_itertools.minmax(map(operator.itemgetter(0), img))
    min_col, max_col = more_itertools.minmax(map(operator.itemgetter(1), img))
    assert len(img) == (max_row - min_row + 1) * (max_col - min_col + 1)
    new_img = {}
    for row_num in range(min_row - 1, max_row + 2):
        for col_num in range(min_col - 1, max_col + 2):
            digits = [img.get(k, padding) for k in _neighbors(row_num, col_num)]
            index = int("".join("1" if d else "0" for d in digits), 2)
            new_img[row_num, col_num] = lut[index]

    if padding:
        new_padding = lut[-1]
    else:
        new_padding = lut[0]

    return new_img, new_padding


def _enhanced_n(img, lut, n):
    padding = False
    for _ in range(n):
        img, padding = _enhanced_1(img, lut, padding)
    assert padding is False  # or counting light pixels would not make sense
    return img


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
        ("example", 35),
        ("input", 5571),  # not 5619, 6225
    ],
)
def test_part_1_on_file_examples(stem, expected):
    assert solution_1(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 3351),
        ("input", 17965),
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
