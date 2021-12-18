import functools
import itertools
import logging
import math
import operator
import pathlib
import textwrap

import pytest

logger = logging.getLogger(__name__)


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def _deflated(obj):
    if isinstance(obj, int):
        return [obj]
    return ["["] + functools.reduce(operator.add, map(_deflated, obj)) + ["]"]


def _inflated(deflated, first=True):
    if first:
        deflated = iter(deflated)
        next(deflated)
    result = []
    for token in deflated:
        if token == "[":
            result.append(_inflated(deflated, False))
        elif token == "]":
            break
        else:
            assert isinstance(token, int)
            result.append(token)
    return result


def _exploded(tokens):
    depth = 0
    for i, token in enumerate(tokens):
        if token == "[":
            depth += 1
            continue

        if token == "]":
            depth -= 1
            continue

        if depth < 5:
            continue

        assert depth == 5
        assert isinstance(token, int)
        result = tokens.copy()

        for j in range(i - 1, -1, -1):
            if isinstance(tokens[j], int):
                result[j] = tokens[j] + tokens[i]
                break

        for j in range(i + 2, len(tokens)):
            if isinstance(tokens[j], int):
                result[j] = tokens[j] + tokens[i + 1]
                break

        return result[: i - 1] + [0] + result[i + 3:]

    return tokens


def _split(tokens):
    for i, token in enumerate(tokens):
        if isinstance(token, int) and 9 < token:
            return tokens[:i] + ["[", int(math.floor(token / 2)), int(math.ceil(token / 2)), "]"] + tokens[i + 1:]
    return tokens


def _added(left, right):
    x = ["["] + left + right + ["]"]
    while True:
        y = _exploded(x)
        if x != y:
            x = y
            continue
        y = _split(x)
        if x != y:
            x = y
            continue
        break
    return x


def _magnitude(number):
    if isinstance(number, int):
        return number
    assert len(number) == 2
    return 3 * _magnitude(number[0]) + 2 * _magnitude(number[1])


def _parse_input(text):
    return [
        [
            int(c) if c in "0123456789"
            else c
            for c in line
            if c != ","
        ]
        for line in text.splitlines()
    ]


def solution_1(puzzle_input: str):
    numbers = _parse_input(puzzle_input)
    left = numbers[0]
    for right in numbers[1:]:
        left = _added(left, right)

    return _magnitude(_inflated(left))


def solution_2(puzzle_input: str):
    numbers = _parse_input(puzzle_input)
    magnitudes = sum(
        ([(_magnitude(_inflated(_added(*v))), v), (_magnitude(_inflated(_added(*v[::-1]))), v)]
         for v in itertools.combinations(numbers, 2)), start=[]
    )

    return max(map(operator.itemgetter(0), magnitudes))


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
        ("example", 3993),
        ("input", 4695),
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
    assert _inflated(_exploded(_deflated(number))) == expected


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
    assert _inflated(_split(_deflated(number))) == expected


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
    assert _inflated(_added(_deflated(left), _deflated(right))) == expected


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
