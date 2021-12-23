from __future__ import annotations

import collections
import logging
import math
import pathlib
from pprint import pprint
from typing import Any, Dict, Iterator, List

import pytest

logger = logging.getLogger(__name__)

# #############
# #01234567890#
# ###A#B#C#D###
#   #A#B#C#D#
#   #########


LOCATIONS = [i for i in range(11) if i not in {2, 4, 6, 8}]


def _blocking():
    lut = {
        "A": 2,
        "B": 4,
        "C": 6,
        "D": 8,
    }
    result = collections.defaultdict(set)
    for room in "ABCD":
        for location in range(11):
            if location in {2, 4, 6, 8}:
                continue
            for blocking in range(location + 1, lut[room]):
                result[room, location].add(blocking)
            for blocking in range(lut[room], location):
                result[room, location].add(blocking)
    return result


def _distances():
    lut = {
        "A": 2,
        "B": 4,
        "C": 6,
        "D": 8,
    }
    result = {}
    for room in "ABCD":
        for location in range(11):
            if location in {2, 4, 6, 8}:
                continue
            result[(room, location)] = abs(lut[room] - location) + 1
    return result


DISTANCES = _distances()
BLOCKING = _blocking()
MULTIPLIERS = {
    "A": 1,
    "B": 10,
    "C": 100,
    "D": 1000,
}


# BLOCKING = {
#     (room, hallway): set(range(hallway+1, LUT[room])) | set(range(LUT[room]+1, hallway))
#     for room in "ABCD"
#     for hallway in range(11)
# }


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def _blocked(hallway, location, room):
    for blocking in BLOCKING[room, location]:
        if blocking in hallway:
            return True
    return False


def _possible_hallway_locations(hallway, room):
    for location in LOCATIONS:
        if location in hallway:
            continue  # occupied
        if _blocked(hallway, location, room):
            continue
        yield location


def _cost(location, room, amphipod):
    return DISTANCES[(room, location)] * MULTIPLIERS[amphipod]


def _solve(
    hallway: Dict[int, str], rooms: Dict[str, str], path=(), cost=0, best=math.inf
):
    assert len(path) <= 16
    if not hallway and all(v == k for k, vs in rooms.items() for v in vs):
        yield path, cost
        return

    # Move into rooms

    # Move into hallway
    for room, occupants in rooms.items():
        if not occupants:
            continue
        if all(room == v for v in occupants):
            continue
        amphipod = occupants[0]
        for location in _possible_hallway_locations(hallway, room):
            new_hallway = hallway | {location: amphipod}
            new_rooms = {k: v if k != room else v[1:] for k, v in rooms.items()}
            marginal_cost = _cost(location, room, amphipod)
            new_cost = cost + marginal_cost
            projected_cost = new_cost + sum(
                _cost(rooms, k, v, v) for k, v in new_hallway.items()
            )
            new_path = path + (
                (
                    amphipod,
                    room,
                    str(location),
                    marginal_cost,
                    new_cost,
                    projected_cost,
                ),
            )
            if best < projected_cost:
                continue
            for returning_path, returning_best in _solve(
                new_hallway, new_rooms, new_path, new_cost, best
            ):
                best = min(best, returning_best)
                yield returning_path, best


def _move_from_hallway(hallway: Dict[int, str], rooms: Dict[str, List[str]], path):
    making_progress = True
    while making_progress:
        making_progress = False
        for src, amphipod in list(hallway.items()):
            dst = amphipod  # Can only move to one room
            occupants = rooms[dst]

            if occupants and any(occupant != amphipod for occupant in occupants):
                continue  # Can only move into room with similar

            if _blocked(hallway, src, dst):
                continue

            path.append((amphipod, str(src), dst, _cost(src, dst, amphipod)))
            rooms[dst].insert(0, hallway.pop(src))
            making_progress = True


def _solve2(
    hallway: Dict[int, str],
    rooms: Dict[str, List[str]],
    cost: int = 0,
    best=math.inf,
    path=[],
) -> Iterator[Any]:
    _move_from_hallway(hallway, rooms, path)
    if not hallway and all(v == k for k, vs in rooms.items() for v in vs):
        yield path, cost
        return

    # First result should be optimal
    # items = sorted([(k, v) for k, v in rooms.items() if v], key=lambda obj: obj[1][0])

    for src, occupants in rooms.items():
        if all(src == occupant for occupant in occupants):
            continue  # Do not touch completed rooms

        amphipod = occupants[0]
        for location in _possible_hallway_locations(hallway, src):
            new_hallway = hallway | {location: amphipod}
            new_rooms = {k: v[:] if k != src else v[1:] for k, v in rooms.items()}
            cost_out = _cost(location, src, amphipod)
            cost_in = _cost(location, amphipod, amphipod)
            new_cost = cost + cost_out + cost_in
            new_path = path + [
                (amphipod, src, str(location), cost_out, cost_in, new_cost)
            ]
            if best <= new_cost:
                continue
            for returning_path, returning_best in _solve2(
                new_hallway, new_rooms, new_cost, best, new_path
            ):
                if returning_best < best:
                    best = returning_best
                    yield returning_path, returning_best


def _penalty(rooms):
    departure_penalties = {
        room: MULTIPLIERS[occupants[1]]
        for room, occupants in rooms.items()
        if room != occupants[1]
    }
    arrival_penalties = {
        room: MULTIPLIERS[room]
        for room, occupants in rooms.items()
        if room != occupants[1]
    }
    return sum(departure_penalties.values()) + sum(arrival_penalties.values())


def solution_1(puzzle_input: str):
    print()
    penalty = _penalty(puzzle_input)
    print(penalty)
    for path, cost in _solve2({}, puzzle_input):
        pprint(cost)
    pprint(path)
    return cost + penalty


def solution_2(puzzle_input: str):
    ...


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example", 590784),
        # ("input", 527915),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    actual = solution_1(_read_input(stem))
    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ({"A": ["B", "A"], "B": ["C", "D"], "C": ["B", "C"], "D": ["D", "A"]}, 12521),
        ({"A": ["B", "C"], "B": ["A", "D"], "C": ["B", "D"], "D": ["C", "A"]}, 14510),
    ],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        # ("example_l", 2758514936282235),
        # ("input", 1218645427221987),
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
