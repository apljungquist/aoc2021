from __future__ import annotations

import collections
import logging
import math
import pathlib
from typing import Dict, Tuple

import pytest

logger = logging.getLogger(__name__)
door_locations = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8,
}


def _left_locations():
    result = {}
    for room in "ABCD":
        start = door_locations[room]
        result[room] = [
            i for i in range(start - 1, -1, -1) if i not in door_locations.values()
        ]
    return result


def _right_locations():
    result = {}
    for room in "ABCD":
        start = door_locations[room]
        result[room] = [
            i for i in range(start + 1, 11) if i not in door_locations.values()
        ]
    return result


LEFT_LOCATIONS = _left_locations()
RIGHT_LOCATIONS = _right_locations()


def _blocking():
    result = collections.defaultdict(set)
    for room in "ABCD":
        for location in range(11):
            if location in door_locations.values():
                continue

            for blocking in range(location + 1, door_locations[room]):
                if blocking in door_locations.values():
                    continue
                result[room, location].add(blocking)

            for blocking in range(door_locations[room], location):
                if blocking in door_locations.values():
                    continue
                result[room, location].add(blocking)
    return result


def _distances():
    result = {}
    for room in "ABCD":
        for room2 in "ABCD":
            result[room, room2] = max(
                4, abs(door_locations[room] - door_locations[room2]) + 2
            )
        for location in range(11):
            if location in {2, 4, 6, 8}:
                continue
            result[(room, location)] = abs(door_locations[room] - location) + 1
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
    for location in LEFT_LOCATIONS[room]:
        if location in hallway:
            break
        yield location
    for location in RIGHT_LOCATIONS[room]:
        if location in hallway:
            break
        yield location


def _move_from_hallway(hallway: Dict[int, str], rooms: Dict[str, Tuple[str, ...]]):
    while True:
        # Can only move to one room so the amphipod is the destination
        for src, dst in hallway.items():
            if _blocked(hallway, src, dst):
                continue

            occupants = rooms[dst]
            if occupants and any(occupant != dst for occupant in occupants):
                continue  # Can only move into room with similar

            break
        else:
            return

        rooms[dst] = (hallway.pop(src),) + rooms[dst]


def _min_cost_from_hallway(
    hallway: Dict[int, str],
    rooms: Dict[str, Tuple[str, ...]],
    cache,
    upstream_cost=0,
    best_total_cost=math.inf,
) -> int:
    cache_key = tuple(hallway.items()) + tuple(rooms.values())
    try:
        return cache[cache_key]
    except KeyError:
        pass

    _move_from_hallway(hallway, rooms)
    if not hallway and all(v == k for k, vs in rooms.items() for v in vs):
        return 0

    best_cost = math.inf
    for src, occupants in rooms.items():
        if all(src == occupant for occupant in occupants):
            continue  # Do not move amphipods out of ordered rooms

        amphipod = occupants[0]
        for location in _possible_hallway_locations(hallway, src):
            new_rooms = rooms | {src: rooms[src][1:]}
            # Cost of returning is already determined once we move into the corridor
            # By adding more cost early we should be able to prune paths earlier
            marginal_cost = (
                DISTANCES[src, location] + DISTANCES[amphipod, location]
            ) * MULTIPLIERS[amphipod]
            # In addition to the move we are about to make, all remaining amphipods
            # that are in the wrong room must at least move the distance to the
            # correct room. The bound could be made tighter by accounting for amphipods
            # that are in the right room but will need to move to let out other
            # amphipods. That is however a lot more fiddly and more expensive, so I do
            # not bother.
            min_downstream_cost = sum(
                DISTANCES[k, v] * MULTIPLIERS[v]
                for k, vs in new_rooms.items()
                for v in vs
                if v != k
            )
            min_total_cost = upstream_cost + marginal_cost + min_downstream_cost
            if best_total_cost <= min_total_cost:
                continue

            new_hallway = hallway | {location: amphipod}
            downstream_cost = _min_cost_from_hallway(
                new_hallway,
                new_rooms,
                cache,
                upstream_cost + marginal_cost,
                best_total_cost,
            )
            cost = marginal_cost + downstream_cost
            if cost < best_cost:
                best_cost = cost
                best_total_cost = upstream_cost + cost

    cache[cache_key] = best_cost
    return best_cost


def _departure_penalty(occupants, room):
    """Return cost of moving to front of room

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


def _min_cost_from_rooms(rooms):
    """Return cost of moving to and from front of room

    >>> _min_cost_from_rooms({"A":list("BDDA"),"B":list("CCBD"),"C":list("BBAC"),"D":list("DACA")})
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
    rooms = {k: tuple(vs) for k, vs in rooms.items()}
    # Observe that all amphipods that are not in the correct position at the outset will
    # at least have to move to the door (actually outside the door but for some reason
    # I cannot get the costs right).
    rooms_cost = _min_cost_from_rooms(rooms)
    # Solve the rest of the problem as if the rooms are a single spot with room for
    # multiple amphipods.
    hallway_cost = _min_cost_from_hallway({}, rooms, {})
    return rooms_cost + hallway_cost


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
        ("input_1", 11332),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    actual = solution_1(_read_input(stem))
    assert actual == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 44169),
        ("input", 49180),
        ("input_1", 49936),
    ],
)
def test_part_2_on_file_examples(stem, expected):
    assert solution_2(_read_input(stem)) == expected
