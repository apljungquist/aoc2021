#!/usr/bin/env python3
import collections
import dataclasses
import itertools
import logging
import pathlib
from typing import Iterable, Iterator, Tuple

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")


@dataclasses.dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclasses.dataclass(frozen=True)
class Line:
    tail: Point
    head: Point

    def is_horizontal(self):
        return self.tail.y == self.head.y

    def is_vertical(self):
        return self.tail.x == self.head.x

    def points(self, include_diagonal: bool):
        result = list(self._points(include_diagonal))
        return result

    def _points(self, include_diagonal: bool):
        if self.is_horizontal():
            y = self.tail.y
            start = min(self.tail.x, self.head.x)
            stop = max(self.tail.x, self.head.x) + 1
            for x in range(start, stop):
                yield Point(x, y)
        elif self.is_vertical():
            x = self.tail.x
            start = min(self.tail.y, self.head.y)
            stop = max(self.tail.y, self.head.y) + 1
            for y in range(start, stop):
                yield Point(x, y)
        else:
            if not include_diagonal:
                return
            if self.tail.x < self.head.x:
                xs = range(self.tail.x, self.head.x + 1)
            elif self.tail.x > self.head.x:
                xs = range(self.tail.x, self.head.x - 1, -1)
            else:
                assert False
            if self.tail.y < self.head.y:
                ys = range(self.tail.y, self.head.y + 1)
            elif self.tail.y > self.head.y:
                ys = range(self.tail.y, self.head.y - 1, -1)
            else:
                assert False
            for x, y in zip(xs, ys):
                yield Point(x, y)


def _board(lines: Iterable[str]) -> Iterator[Tuple[Tuple[int, int], int]]:
    for row, line in enumerate(lines):
        for col, num in enumerate(line.split()):
            yield (row, col), int(num)


def _point(text: str) -> Point:
    x, y = text.split(",")
    return Point(int(x), int(y.strip()))


def _line(text) -> Line:
    tail, head = text.split("->")
    return Line(_point(tail), _point(head))


def _read_lines(path: pathlib.Path):
    return [_line(line) for line in path.read_text().splitlines()]


def num_zone(lines, include_diagonal):
    counts = collections.Counter(
        itertools.chain.from_iterable(line.points(include_diagonal) for line in lines)
    )
    return sum(1 if v >= 2 else 0 for v in counts.values())


def solution_1(path):
    return num_zone(_read_lines(path), False)


def solution_2(path):
    return num_zone(_read_lines(path), True)


def test_example_1():
    assert solution_1(INPUTS_PATH / "example.txt") == 5


def test_input_1():
    assert solution_1(INPUTS_PATH / "input.txt") == 6225


def test_example_2():
    assert solution_2(INPUTS_PATH / "example.txt") == 12


def test_input_2():
    assert solution_2(INPUTS_PATH / "input.txt") == 22116
