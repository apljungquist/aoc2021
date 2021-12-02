#!/usr/bin/env python3
import collections
import logging
import pathlib

logger = logging.getLogger(__name__)
PROJECT_ROOT = pathlib.Path(__file__).parent
INPUTS_PATH = PROJECT_ROOT / "day" / __file__.split(".")[0].split("_")[-1]


def test_example_1():
    assert solution_1(INPUTS_PATH / "example.txt") == 150


def test_input_1():
    assert solution_1(INPUTS_PATH / "input.txt") == 2187380


def test_example_2():
    assert solution_2(INPUTS_PATH / "example.txt") == 900


def test_input_2():
    assert solution_2(INPUTS_PATH / "input.txt") == 2086357770


def _commands(text: str):
    for line in text.splitlines():
        if not line:
            logger.warning("Skipping line %s", line)
            continue

        direction, distance = line.strip().split()
        yield direction, int(distance)


def solution_1(path):
    aggregate = collections.defaultdict(int)
    for direction, distance in _commands(path.read_text()):
        aggregate[direction] += distance

    net_forward = aggregate.pop("forward", 0)
    net_down = aggregate.pop("down", 0) - aggregate.pop("up", 0)
    assert not aggregate
    return net_forward * net_down


def solution_2(path):
    aim = 0
    net_forward = 0
    net_down = 0
    for direction, x in _commands(path.read_text()):
        if direction == "down":
            aim += x
        elif direction == "up":
            aim -= x
        elif direction == "forward":
            net_forward += x
            net_down += aim * x
        else:
            assert False
        logger.info("After %s %d we are at %d, %d", direction, x, net_forward, net_down)

    return net_forward * net_down
