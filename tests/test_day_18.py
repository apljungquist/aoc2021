import logging
import math
import pathlib
import textwrap

import pytest

logger = logging.getLogger(__name__)


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def _deflated(inflated):
    if isinstance(inflated, int):
        yield None, inflated
        return

    yield True, None
    for x in inflated:
        yield from _deflated(x)
    yield False, None


def _inflated(deflated, first=True):
    if first:
        deflated = iter(deflated)
        next(deflated)
    result = []
    for increase, number in deflated:
        if number is None:
            if increase:
                result.append(_inflated(deflated, False))
            else:
                break
        else:
            result.append(number)
    return result


def _exploded(number):
    before = list(_deflated(number))

    depth = 0
    after = before
    for i, (increase, _) in enumerate(before):
        if increase is not None:
            if increase:
                depth += 1
            else:
                depth -= 1
            continue

        if depth < 5:
            continue

        assert depth == 5
        assert increase is None or increase is False

        for j in range(i - 1, -1, -1):
            if after[j][1] is not None:
                after[j] = (None, after[j][1] + after[i][1])
                l = 0
                break
        else:
            l = 0

        for j in range(i + 2, len(after)):
            if after[j][1] is not None:
                after[j] = (None, after[j][1] + after[i + 1][1])
                r = 0
                break
        else:
            r = 0

        if l is r is None:
            infix = []
        else:
            infix = [(None, l)]

        after = before[: i - 1] + infix + before[i + 3:]
        break

    result = _inflated(after)
    return result


def _split(number):
    if isinstance(number, int):
        if number <= 9:
            return number
        return [int(math.floor(number / 2)), int(math.ceil(number / 2))]
    assert isinstance(number, list)
    for i, x in enumerate(number):
        y = _split(x)
        if x != y:
            return number[:i] + [y] + number[i + 1:]
    return number


def _added(left, right):
    x = [left, right]
    # print()
    # print("x", x)
    while True:
        y = _exploded(x)
        if x != y:
            x = y
            # print("e", y)
            continue
        y = _split(x)
        if x != y:
            x = y
            # print("s", y)
            continue
        break
    return x


def _magnitude(number):
    if isinstance(number, int):
        return number
    assert len(number) == 2
    return 3 * _magnitude(number[0]) + 2 * _magnitude(number[1])


def _parse_input(text):
    lut = {
        "[": (True, None),
        "]": (False, None),
    }
    result = []
    for line in text.splitlines():
        deflated = [
            lut[v] if v in lut else
            (None, int(v))
            for v in line.strip()
            if v != ","
        ]
        result.append(_inflated(deflated))
    return result


def solution_1(puzzle_input: str):
    numbers = _parse_input(puzzle_input)
    left = numbers[0]
    for right in numbers[1:]:
        left = _added(left, right)

    return _magnitude(left)


def solution_2(puzzle_input: str):
    ...


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 4140),
        ("input", 3793),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    assert solution_1(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        (textwrap.dedent(
            """\
            [[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]]
            [7,[[[3,7],[4,3]],[[6,3],[8,8]]]]
            [[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]]
            [[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]]
            [7,[5,[[3,8],[1,4]]]]
            [[2,[2,2]],[8,[8,1]]]
            [2,9]
            [1,[[[9,3],9],[[9,0],[0,7]]]]
            [[[5,[7,4]],7],1]
            [[[[4,2],2],6],[8,7]]"""),
        3488,),
    ],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example", 112),
        # ("input", 2555),
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


@pytest.mark.parametrize(
    "number, expected",
    [
        (
                [[[[[9, 8], 1], 2], 3], 4],
                [[[[0, 9], 2], 3], 4],
        ),
        (
                [7, [6, [5, [4, [3, 2]]]]],
                [7, [6, [5, [7, 0]]]],
        ),
        (
                [[6, [5, [4, [3, 2]]]], 1],
                [[6, [5, [7, 0]]], 3],
        ),
        (
                [[3, [2, [1, [7, 3]]]], [6, [5, [4, [3, 2]]]]],
                [[3, [2, [8, 0]]], [9, [5, [4, [3, 2]]]]],
        ),
        (
                [[3, [2, [8, 0]]], [9, [5, [4, [3, 2]]]]],
                [[3, [2, [8, 0]]], [9, [5, [7, 0]]]],
        ),
    ],
)
def test_exploded(number, expected):
    assert _exploded(number) == expected


@pytest.mark.parametrize(
    "number",
    [
        [[9, 8], 1],
        [[[[[9, 8], 1], 2], 3], 4],
        [[[[0, 9], 2], 3], 4],
        [7, [6, [5, [4, [3, 2]]]]],
        [7, [6, [5, [7, 0]]]],
        [[6, [5, [4, [3, 2]]]], 1],
        [[6, [5, [7, 0]]], 3],
        [[3, [2, [1, [7, 3]]]], [6, [5, [4, [3, 2]]]]],
        [[3, [2, [8, 0]]], [9, [5, [4, [3, 2]]]]],
        [[3, [2, [8, 0]]], [9, [5, [4, [3, 2]]]]],
        [[3, [2, [8, 0]]], [9, [5, [7, 0]]]],
    ],
)
def test_deflated_inflated(number):
    assert _inflated(list(_deflated(number))) == number


@pytest.mark.parametrize(
    "number, expected",
    [
        (
                [[[[0, 7], 4], [15, [0, 13]]], [1, 1]],
                [[[[0, 7], 4], [[7, 8], [0, 13]]], [1, 1]],
        ),
        (
                [[[[0, 7], 4], [[7, 8], [0, 13]]], [1, 1]],
                [[[[0, 7], 4], [[7, 8], [0, [6, 7]]]], [1, 1]],
        ),
    ],
)
def test_split(number, expected):
    assert _split(number) == expected


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (
                [[[[4, 3], 4], 4], [7, [[8, 4], 9]]],
                [1, 1],
                [[[[0, 7], 4], [[7, 8], [6, 0]]], [8, 1]],
        )
    ],
)
def test_added(left, right, expected):
    assert _added(left, right) == expected


@pytest.mark.parametrize(
    "number, expected",
    [
        ([9, 1], 29),
        ([1, 9], 21),
        ([[9, 1], [1, 9]], 129),
        ([[1, 2], [[3, 4], 5]], 143),
        ([[[[0, 7], 4], [[7, 8], [6, 0]]], [8, 1]], 1384),
        ([[[[1, 1], [2, 2]], [3, 3]], [4, 4]], 445),
        ([[[[3, 0], [5, 3]], [4, 4]], [5, 5]], 791),
        ([[[[5, 0], [7, 4]], [5, 5]], [6, 6]], 1137),
        ([[[[8, 7], [7, 7]], [[8, 6], [7, 7]]], [[[0, 7], [6, 6]], [8, 7]]], 3488),
    ],
)
def test_magnitude(number, expected):
    assert _magnitude(number) == expected
