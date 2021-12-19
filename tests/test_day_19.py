import logging
import pathlib
import re
import textwrap
from pprint import pprint
from typing import NamedTuple

import more_itertools
import pytest

logger = logging.getLogger(__name__)


def _fingerprint(scanner):
    return {p - q for p in scanner for q in scanner}


def _fingerprints(scanner):
    unique = {rotation: _rotated(scanner, *rotation) for rotation in _rotations()}
    return {rotation: _fingerprint(rotated) for rotation, rotated in unique.items()}


def _match_one_on_fingerprint(references, candidates):
    for reference_num, (reference, reference_fp) in references.items():
        for candidate_num, (candidate, fingerprints) in candidates.items():
            for rotation, candidate_fp in fingerprints.items():
                if len(reference_fp & candidate_fp) < 133:
                    continue

                try:
                    rotation, translation, result = _pose(reference, candidate)
                except ValueError:
                    continue
                return candidate_num, result, candidate_fp, translation
    raise ValueError


def _match_all_on_fingerprint(scanners):
    done = {0: (scanners[0], _fingerprint(scanners[0]))}
    remaining = {k: (v, _fingerprints(v)) for k, v in scanners.items() if k != 0}
    translations = []
    aggregate = scanners[0]
    while remaining:
        candidate_num, candidate, fingerprint, translation = _match_one_on_fingerprint(
            done, remaining
        )
        translations.append(translation)
        aggregate = aggregate | candidate
        done[candidate_num] = (candidate, fingerprint)
        del remaining[candidate_num]
    return aggregate, done, translations


class Point(NamedTuple):
    x: int
    y: int
    z: int

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def manhattan(self):
        return sum(map(abs, self))


def _read_input(stem: str) -> str:
    return (pathlib.Path(__file__).with_suffix("") / f"{stem}.txt").read_text()


def _parse_header(line):
    return int(re.match("--- scanner (\d+) ---", line).group(1))


def _parse_body(lines):
    return {Point(*map(int, line.split(","))) for line in lines}


def _parse_input(text):
    return {
        _parse_header(lines[0]): _parse_body(lines[1:])
        for lines in more_itertools.split_at(text.splitlines(), lambda line: not line)
    }


def _rotated_one(scanner, axis, steps):
    match steps:
        case 0:
            return scanner
        case 1:
            scales = -1, 1
            swap = True
        case 2:
            scales = -1, -1
            swap = False
        case 3:
            scales = 1, -1
            swap = True
        case _:
            assert False

    other = [i for i in range(3) if i != axis]
    scales = {
        axis: 1,
        other[0]: scales[0],
        other[1]: scales[1],
    }
    if swap:
        mapping = {
            axis: axis,
            other[0]: other[1],
            other[1]: other[0],
        }
    else:
        mapping = {i: i for i in range(3)}

    return {
        Point(
            p[mapping[0]] * scales[0],
            p[mapping[1]] * scales[1],
            p[mapping[2]] * scales[2],
        )
        for p in scanner
    }


def _rotated(scanner, x, y, z):
    scanner = _rotated_one(scanner, 0, x)
    scanner = _rotated_one(scanner, 1, y)
    scanner = _rotated_one(scanner, 2, z)
    return scanner


def _rotations():
    # Will result in some duplicates but should not matter
    for x in range(4):
        for y in range(4):
            for z in range(4):
                yield x, y, z


def _translated(scanner, t):
    return {p - t for p in scanner}


def _pose(reference, candidate, threshold=12):
    for rotation in _rotations():
        rotated = _rotated(candidate, *rotation)
        for l_anchor in reference:
            for r_anchor in rotated:
                translation = r_anchor - l_anchor
                translated = _translated(rotated, translation)
                overlap = reference & translated
                if len(overlap) >= threshold:
                    return rotation, translation, translated
    raise ValueError


def _match_one(references, candidates):
    for reference_num, reference in references.items():
        for candidate_num, candidate in candidates.items():
            try:
                rotation, translation, result = _pose(reference, candidate)
            except ValueError:
                continue
            return candidate_num, result
    raise ValueError


def _match_all(scanners):
    done = {0: scanners[0]}
    remaining = {k: v for k, v in scanners.items() if k != 0}
    aggregate = scanners[0]
    while remaining:
        print(len(aggregate))
        candidate_num, candidate = _match_one(done, remaining)
        aggregate = aggregate | candidate
        done[candidate_num] = candidate
        del remaining[candidate_num]
    return aggregate, done


def solution_1(puzzle_input: str):
    scanners = _parse_input(puzzle_input)
    # aggregate, done = _match_all(scanners)
    aggregate, done, _ = _match_all_on_fingerprint(scanners)
    return len(aggregate)


def solution_2(puzzle_input: str):
    scanners = _parse_input(puzzle_input)
    # aggregate, done = _match_all(scanners)
    aggregate, done, translations = _match_all_on_fingerprint(scanners)
    distances = [(p - q).manhattan() for p in translations for q in translations]
    return max(distances)


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 79),
        ("input", 335),
    ],
)
def test_part_1_on_file_examples(stem, expected):
    assert solution_1(_read_input(stem)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [],
)
def test_part_1_on_text_examples(text, expected):
    assert solution_1(text) == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 3621),
        ("input", 10864),
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
    "candidate_text",
    [
        textwrap.dedent(
            """\
        --- scanner 0 ---
        -1,-1,1
        -2,-2,2
        -3,-3,3
        -2,-3,1
        5,6,-4
        8,0,7
        """
        ),
        textwrap.dedent(
            """\
        --- scanner 0 ---
        1,-1,1
        2,-2,2
        3,-3,3
        2,-1,3
        -5,4,-6
        -8,-7,0
        """
        ),
        textwrap.dedent(
            """\
        --- scanner 0 ---
        -1,-1,-1
        -2,-2,-2
        -3,-3,-3
        -1,-3,-2
        4,6,5
        -7,0,8
        """
        ),
        textwrap.dedent(
            """\
        --- scanner 0 ---
        1,1,-1
        2,2,-2
        3,3,-3
        1,3,-2
        -4,-6,5
        7,0,8
        """
        ),
        textwrap.dedent(
            """\
        --- scanner 0 ---
        1,1,1
        2,2,2
        3,3,3
        3,1,2
        -6,-4,-5
        0,7,-8
        """
        ),
    ],
)
def test_rotate(candidate_text):
    reference_text = textwrap.dedent(
        """\
        --- scanner 0 ---
        -1,-1,1
        -2,-2,2
        -3,-3,3
        -2,-3,1
        5,6,-4
        8,0,7
        """
    )
    reference = _parse_input(reference_text)[0]
    candidate = _parse_input(candidate_text)[0]
    rotation, translation, result = _pose(reference, candidate, threshold=6)
    assert translation == (0, 0, 0)
    assert reference == result


def test_there_are_24_unique_rotations():
    # assert len(set(_rotations())) == 24
    # assert more_itertools.ilen(_rotations()) == 24
    print(sorted(_rotations()))
    reference_text = textwrap.dedent(
        """\
        --- scanner 0 ---
        -1,-1,1
        -2,-2,2
        -3,-3,3
        -2,-3,1
        5,6,-4
        8,0,7
        """
    )
    reference = _parse_input(reference_text)[0]
    candidates = {
        frozenset(_rotated(reference, *rotation)) for rotation in _rotations()
    }
    assert len(candidates) == 24
