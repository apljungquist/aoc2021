#!/usr/bin/env python3
import logging
import pathlib
import sys

import more_itertools
import numpy as np

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]

np.set_printoptions(threshold=sys.maxsize, linewidth=sys.maxsize)


def read_height_map(path: pathlib.Path):
    return np.asarray(
        [[int(cell) for cell in row] for row in path.read_text().splitlines()]
    )


def _row_mins(heights):
    results = np.zeros_like(heights)
    for i in range(heights.shape[0]):
        src = heights[i, :]
        dst = results[i, :]
        if src[0] < src[1]:
            dst[0] = 1
        if src[-1] < src[-2]:
            dst[-1] = 1
        for j, (a, b, c) in enumerate(more_itertools.triplewise(src), 1):
            if b < a and b < c:
                dst[j] = 1
    return results


def solution_1(path):
    heights = read_height_map(path)
    row_mins = _row_mins(heights)
    col_mins = _row_mins(heights.T).T
    four_mins = row_mins * col_mins
    risk = four_mins * (heights + 1)
    return np.sum(risk)


def solution_2(path):
    heights = read_height_map(path)
    h, w = heights.shape
    h2, w2 = h + 2, w + 2
    heights2 = np.full((h2, w2), 9)
    heights2[1:-1, 1:-1] = heights
    walls2 = (heights2 == 9) * 1
    basins2 = np.arange(h2 * w2).reshape(walls2.shape) * (walls2 == 0)
    making_progress = True
    while making_progress:
        making_progress = False
        if not np.isin(0, basins2):
            break

        for r in range(1, h + 1):
            for c in range(1, w + 1):
                if walls2[r, c] == 1:
                    continue

                b = max(basins2[r, c], basins2[r, c - 1], basins2[r, c + 1], basins2[r - 1, c], basins2[r + 1, c])
                if b and basins2[r, c] != b:
                    making_progress = True
                    basins2[r, c] = b

    basins_nums = set(int(x) for x in np.nditer(basins2))
    basins_nums.remove(0)
    by_num = {n: np.sum(basins2 == n) for n in basins_nums}
    sizes = sorted(by_num.values(), reverse=True)
    return sizes[0] * sizes[1] * sizes[2]


def test_example_1():
    actual = solution_1(INPUTS_PATH / "example.txt")
    expected = 15
    assert actual == expected


def test_input_1():
    actual = solution_1(INPUTS_PATH / "input.txt")
    expected = 526
    assert actual == expected


def test_example_2():
    actual = solution_2(INPUTS_PATH / "example.txt")
    expected = 1134
    assert actual == expected


def test_input_2_bound():
    actual = solution_2(INPUTS_PATH / "input.txt")
    assert actual > 585648


def test_input_2():
    actual = solution_2(INPUTS_PATH / "input.txt")
    expected = 585648
    assert actual == expected
