import logging
import pathlib
import re

import pytest

logger = logging.getLogger(__name__)


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def _target_area(text: str):
    match = re.match(r"^target area: x=(\d+)..(\d+), y=(-?\d+)..(-?\d+)$", text)
    assert match is not None
    result = [
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        int(match.group(4)),
    ]
    assert result[0] < result[1]
    assert result[2] < result[3]
    return result


def _simulate(dx, dy, tgt):
    x, y = 0, 0
    tgt_x_min, tgt_x_max, tgt_y_min, tgt_y_max = tgt
    y_max = 0
    while True:
        x += dx
        y += dy
        dx = max(0, dx - 1)
        dy -= 1
        y_max = max(y, y_max)
        if tgt_x_min <= x <= tgt_x_max and tgt_y_min <= y <= tgt_y_max:
            return y_max
        if tgt_x_max <= x:
            return None
        if y <= tgt_y_min:
            return None
        if dx == 0 and x < tgt_x_min:
            return None


def solution_1(puzzle_input: str):
    tgt = _target_area(puzzle_input)
    h_max = -1
    for dx in range(1, tgt[1]):
        for dy in range(1000):
            try:
                h = _simulate(dx, dy, tgt)
            except RuntimeError:
                pass
            if h is not None:
                if h_max <= h:
                    h_max = h
    return h_max


def solution_2(puzzle_input: str):
    tgt = _target_area(puzzle_input)
    num_h = 0
    for dx in range(1, tgt[1] + 1):
        for dy in range(tgt[2] - 1, 1000):
            try:
                h = _simulate(dx, dy, tgt)
            except RuntimeError:
                pass
            if h is not None:
                num_h += 1
    return num_h


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 45),
        ("input", 15931),  # not 1176
    ],
)
def test_part_1_on_file_examples(stem, expected):
    assert solution_1(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 112),
        ("input", 2555),
    ],
)
def test_part_2_on_file_examples(stem, expected):
    assert solution_2(_read_input(stem)) == expected
