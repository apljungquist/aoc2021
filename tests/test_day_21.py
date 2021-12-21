import collections
import itertools
import logging
import pathlib

import more_itertools
import pytest

logger = logging.getLogger(__name__)


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


DIE = collections.Counter(
    i + j + k for i in range(1, 4) for j in range(1, 4) for k in range(1, 4)
)  # len 7
assert sum(DIE.values()) == 27


def _play2(positions, scores, hero, num_universe):
    for num_step, multiplier in DIE.items():
        assert 0 < multiplier
        assert 3 <= num_step <= 9
        new_num_universe = multiplier * num_universe

        position = positions[hero] + num_step
        while position > 10:
            position -= 10
        assert 1 <= position <= 10

        score = scores[hero] + position
        if 21 <= score:
            yield hero, new_num_universe
            continue

        new_positions = {hero: position, not hero: positions[not hero]}
        new_scores = {
            hero: score,
            not hero: scores[not hero],
        }
        yield from _play2(new_positions, new_scores, not hero, new_num_universe)


def solution_1(puzzle_input: str):
    dice = (i % 100 + 1 for i in itertools.count())
    positions = list(puzzle_input)
    scores = [0, 0]
    for i in itertools.count():
        player = i % 2
        steps = sum(more_itertools.take(3, dice))
        positions[player] = positions[player] + steps
        while positions[player] > 10:
            positions[player] -= 10
        scores[player] += positions[player]
        if scores[player] >= 1000:
            break
    return (i + 1) * 3 * scores[(i + 1) % 2]


def solution_2(puzzle_input: str):
    wins = {
        False: 0,
        True: 0,
    }
    positions = {
        False: puzzle_input[0],
        True: puzzle_input[1],
    }
    scores = {
        False: 0,
        True: 0,
    }
    for winner, num_universe in _play2(positions, scores, False, 1):
        wins[winner] += num_universe
    print(wins)
    return max(wins.values())


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
    [
        ((4, 8), 739785),
        ((10, 2), 916083),
    ],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [],
)
def test_part_2_on_file_examples(stem, expected):
    assert solution_2(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ((4, 8), 444356092776315),
        ((10, 2), 49982165861983),
    ],
)
def test_part_2_on_text_examples(text, expected):
    assert solution_2(text) == expected
