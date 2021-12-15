#!/usr/bin/env python3
import heapq
import logging
import pathlib
import textwrap

import pytest

logger = logging.getLogger(__name__)
INPUTS_PATH = pathlib.Path(__file__).with_suffix("")


def _read_levels(path: pathlib.Path):
    return {
        (row_num, col_num): int(cell)
        for row_num, row in enumerate(path.read_text().splitlines())
        for col_num, cell in enumerate(row)
    }


def _neighbors(row_num, col_num, max_row, max_col):
    if row_num > 0:
        yield row_num - 1, col_num

    if col_num > 0:
        yield row_num, col_num - 1

    if col_num < max_col:
        yield row_num, col_num + 1

    if row_num < max_row:
        yield row_num + 1, col_num


def _optimal_path_risk(levels):
    frontier = []
    heapq.heappush(frontier, (0, (0, 0)))
    optima = {(0, 0): 0}
    dst = max(levels)
    while dst not in optima:
        prev_v, prev_k = heapq.heappop(frontier)
        for curr_k in _neighbors(*prev_k, *dst):
            if curr_k not in optima or prev_v + levels[curr_k] < optima[curr_k]:
                curr_v = prev_v + levels[curr_k]
                optima[curr_k] = curr_v
                heapq.heappush(frontier, (curr_v, curr_k))
    return optima[dst]


def _augmented(levels):
    max_row, max_col = max(levels)
    num_row, num_col = max_row + 1, max_col + 1
    result = {}
    for i in range(5):
        for j in range(5):
            for (row_num, col_num), v in levels.items():
                new_k = row_num + i * num_row, col_num + j * num_col
                new_v = v + i + j
                assert new_k not in result
                result[new_k] = new_v % 10 + new_v // 10
    return result


def _format_levels(levels):
    max_row = max(y for _, y in levels)
    max_col = max(x for x, _ in levels)
    return "\n".join(
        "".join(str(levels[row_num, col_num]) for col_num in range(max_col + 1))
        for row_num in range(max_row + 1)
    )


def solution_1(path):
    levels = _read_levels(path)
    return _optimal_path_risk(levels)


def solution_2(path):
    levels = _augmented(_read_levels(path))
    return _optimal_path_risk(levels)


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 40),
        ("input", 553),
    ],
)
def test_part_1_on_examples(stem, expected):
    assert solution_1(INPUTS_PATH / f"{stem}.txt") == expected


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("example", 315),
        ("input", 2858),
    ],
)
def test_part_2_on_examples(stem, expected):
    assert solution_2(INPUTS_PATH / f"{stem}.txt") == expected


def test_augment_on_example():
    expected = textwrap.dedent(
        """\
        11637517422274862853338597396444961841755517295286
        13813736722492484783351359589446246169155735727126
        21365113283247622439435873354154698446526571955763
        36949315694715142671582625378269373648937148475914
        74634171118574528222968563933317967414442817852555
        13191281372421239248353234135946434524615754563572
        13599124212461123532357223464346833457545794456865
        31254216394236532741534764385264587549637569865174
        12931385212314249632342535174345364628545647573965
        23119445813422155692453326671356443778246755488935
        22748628533385973964449618417555172952866628316397
        24924847833513595894462461691557357271266846838237
        32476224394358733541546984465265719557637682166874
        47151426715826253782693736489371484759148259586125
        85745282229685639333179674144428178525553928963666
        24212392483532341359464345246157545635726865674683
        24611235323572234643468334575457944568656815567976
        42365327415347643852645875496375698651748671976285
        23142496323425351743453646285456475739656758684176
        34221556924533266713564437782467554889357866599146
        33859739644496184175551729528666283163977739427418
        35135958944624616915573572712668468382377957949348
        43587335415469844652657195576376821668748793277985
        58262537826937364893714847591482595861259361697236
        96856393331796741444281785255539289636664139174777
        35323413594643452461575456357268656746837976785794
        35722346434683345754579445686568155679767926678187
        53476438526458754963756986517486719762859782187396
        34253517434536462854564757396567586841767869795287
        45332667135644377824675548893578665991468977611257
        44961841755517295286662831639777394274188841538529
        46246169155735727126684683823779579493488168151459
        54698446526571955763768216687487932779859814388196
        69373648937148475914825958612593616972361472718347
        17967414442817852555392896366641391747775241285888
        46434524615754563572686567468379767857948187896815
        46833457545794456865681556797679266781878137789298
        64587549637569865174867197628597821873961893298417
        45364628545647573965675868417678697952878971816398
        56443778246755488935786659914689776112579188722368
        55172952866628316397773942741888415385299952649631
        57357271266846838237795794934881681514599279262561
        65719557637682166874879327798598143881961925499217
        71484759148259586125936169723614727183472583829458
        28178525553928963666413917477752412858886352396999
        57545635726865674683797678579481878968159298917926
        57944568656815567976792667818781377892989248891319
        75698651748671976285978218739618932984172914319528
        56475739656758684176786979528789718163989182927419
        67554889357866599146897761125791887223681299833479"""
    )
    actual = _format_levels(_augmented(_read_levels(INPUTS_PATH / "example.txt")))
    assert actual == expected
