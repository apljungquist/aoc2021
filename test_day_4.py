#!/usr/bin/env python3
import collections
import itertools
import logging
import pathlib
from typing import Iterable, Iterator, Tuple

import more_itertools
import pytest

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


def _board(lines: Iterable[str]) -> Iterator[Tuple[Tuple[int, int], int]]:
    for row, line in enumerate(lines):
        for col, num in enumerate(line.split()):
            yield (row, col), int(num)


def _read_boards(path: pathlib.Path):
    lines = path.read_text().splitlines()[1:]
    return [dict(_board(board[1:6])) for board in more_itertools.sliced(lines, 6)]


def _read_draw(path: pathlib.Path):
    return [int(num) for num in path.read_text().splitlines()[0].split(",")]


def _bingo(board, nums):
    cols = {num: col for (row, col), num in board.items()}
    rows = {num: row for (row, col), num in board.items()}
    crossed_cols = collections.Counter(cols.get(num) for num in nums)
    crossed_rows = collections.Counter(rows.get(num) for num in nums)
    crossed_cols.pop(None, None)
    crossed_rows.pop(None, None)
    return any(
        v >= 5 for v in itertools.chain(crossed_cols.values(), crossed_rows.values())
    )


def _score(board, nums):
    unmarked = set(board.values()) - set(nums)
    return sum(unmarked)


def solution_1(path):
    draw = _read_draw(path)
    boards = _read_boards(path)
    for i in range(len(draw)):
        for board in boards:
            if _bingo(board, draw[:i]):
                return draw[i - 1] * _score(board, draw[:i])

    raise RuntimeError


def solution_2(path):
    draw = _read_draw(path)
    boards = _read_boards(path)
    for i in range(len(draw)):
        boards = [board for board in boards if not _bingo(board, draw[:i])]
        if len(boards) == 1:
            break
    else:
        raise RuntimeError

    board = more_itertools.one(boards)
    for i in range(i, len(draw)):
        if _bingo(board, draw[:i]):
            return draw[i - 1] * _score(board, draw[:i])

    raise RuntimeError


@pytest.mark.parametrize(
    "board, draw",
    [
        (
            _read_boards(INPUTS_PATH / "example.txt")[2],
            [7, 4, 9, 5, 11, 17, 23, 2, 0, 14, 21, 24],
        ),
    ],
)
def test_bingo_returns_true(board, draw):
    assert _bingo(board, draw)


@pytest.mark.parametrize(
    "board, draw",
    [
        (
            _read_boards(INPUTS_PATH / "example.txt")[0],
            [7, 4, 9, 5, 11, 17, 23, 2, 0, 14, 21, 24],
        ),
        (
            _read_boards(INPUTS_PATH / "example.txt")[1],
            [7, 4, 9, 5, 11, 17, 23, 2, 0, 14, 21, 24],
        ),
        (
            _read_boards(INPUTS_PATH / "example.txt")[2],
            [7, 4, 9, 5, 11, 17, 23, 2, 0, 14, 21],
        ),
    ],
)
def test_bingo_returns_false(board, draw):
    assert not _bingo(board, draw)


def test_example_1():
    assert solution_1(INPUTS_PATH / "example.txt") == 4512


def test_input_1():
    assert solution_1(INPUTS_PATH / "input.txt") == 22680


def test_example_2():
    assert solution_2(INPUTS_PATH / "example.txt") == 1924


def test_input_2():
    assert solution_2(INPUTS_PATH / "input.txt") == 16168
