from __future__ import annotations

import collections
import logging
import math
import pathlib
from typing import Any, Dict, Iterator, List

import more_itertools
import pytest

logger = logging.getLogger(__name__)

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


def _solve(
    hallway: Dict[int, str],
    rooms: Dict[str, List[str]],
    cost: int,
    best,
    path,
) -> Iterator[Any]:
    _move_from_hallway(hallway, rooms, path)
    if not hallway and all(v == k for k, vs in rooms.items() for v in vs):
        yield path, cost
        return

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
            for returning_path, returning_best in _solve(
                new_hallway, new_rooms, new_cost, best, new_path
            ):
                if returning_best < best:
                    best = returning_best
                    yield returning_path, returning_best


def _departure_penalty(occupants, room):
    """Return cost of moving to fron of room

    >>> _departure_penalty(list("BDDA"), "A")
    3000
    >>> _departure_penalty(list("CCBD"), "B")
    3120
    >>> _departure_penalty(list("BBAC"), "C")
    12
    >>> _departure_penalty(list("DACA"), "D")
    204
    """
    result = 0
    for i, curr in enumerate(occupants):
        if all(late == room for late in occupants[i:]):
            continue
        result += MULTIPLIERS[curr] * i
    return result


def _arrival_penalty(occupants, room):
    """Return cost of moving from front of room

    >>> _arrival_penalty(list("BDDA"), "A")
    3
    >>> _arrival_penalty(list("CCBD"), "B")
    60
    >>> _arrival_penalty(list("BBAC"), "C")
    300
    >>> _arrival_penalty(list("DACA"), "D")
    6000
    """
    result = 0
    for i, curr in enumerate(occupants):
        if all(late == room for late in occupants[i:]):
            continue
        result += MULTIPLIERS[room] * i
    return result


def _penalty(rooms):
    """Return cost of moving to and from front of room

    >>> _penalty({"A":list("BDDA"),"B":list("CCBD"),"C":list("BBAC"),"D":list("DACA")})
    12699
    """
    departure_penalties = {
        room: _departure_penalty(occupants, room)
        for room, occupants in rooms.items()
        if room != occupants[1]
    }
    arrival_penalties = {
        room: _arrival_penalty(occupants, room)
        for room, occupants in rooms.items()
        if room != occupants[1]
    }
    return sum(departure_penalties.values()) + sum(arrival_penalties.values())


def _min_cost_of_solution(rooms):
    penalty = _penalty(rooms)
    _, cost = more_itertools.last(_solve({}, rooms, 0, math.inf, []))
    return cost + penalty


def _rooms(text: str):
    lines = text.splitlines()[2:-1]
    result = {
        "A": [],
        "B": [],
        "C": [],
        "D": [],
    }
    for line in lines:
        result["A"].append(line[3])
        result["B"].append(line[5])
        result["C"].append(line[7])
        result["D"].append(line[9])
    return result


def solution_1(puzzle_input: str):
    rooms = _rooms(puzzle_input)
    return _min_cost_of_solution(rooms)


def solution_2(puzzle_input: str):
    rooms = _rooms(puzzle_input)
    infixes = {
        "A": "DD",
        "B": "CB",
        "C": "BA",
        "D": "AC",
    }
    for room, infix in infixes.items():
        rooms[room][1:1] = list(infix)
    return _min_cost_of_solution(rooms)


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 12521),
        ("input", 14510),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    actual = solution_1(_read_input(stem))
    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 44169),
        ("input", 49180),
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
