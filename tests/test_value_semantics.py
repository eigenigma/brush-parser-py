"""Nodes, members and errors survive copy and process boundaries."""

import copy
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from unittest.mock import ANY

import pytest

from brush_parser import _core as core

NODES = [
    core.parse_program('a=(1 [k]=v); echo "héllo $x" | wc'),
    core.parse_word('~bob/"$x"')[0],
    core.parse_parameter("x[1]"),
    core.SourceSpan(core.SourcePosition(0, 1, 1), core.SourcePosition(1, 1, 2)),
    core.SeparatorOperator.Async,
]


def identity(value: object) -> object:
    return value


@pytest.fixture(scope="module")
def worker() -> Iterator[ProcessPoolExecutor]:
    with ProcessPoolExecutor(max_workers=1) as pool:
        yield pool


@pytest.mark.parametrize("node", NODES, ids=lambda node: type(node).__qualname__)
def test_copy_and_deepcopy_rebuild_an_equal_node(node):
    assert copy.copy(node) == node
    assert copy.deepcopy(node) == node


@pytest.mark.parametrize("node", NODES, ids=lambda node: type(node).__qualname__)
def test_node_crosses_a_process_boundary(worker, node):
    assert worker.submit(identity, node).result() == node


def test_member_comes_back_as_the_class_attribute(worker):
    member = core.SeparatorOperator.Async
    assert copy.deepcopy(member) is member
    assert worker.submit(identity, member).result() is member


def test_parse_error_with_position_propagates_from_a_worker(worker):
    with pytest.raises(core.ParseError) as caught:
        worker.submit(core.parse_program, "echo )").result()
    assert str(caught.value) == "syntax error at line 1 col 6"
    assert caught.value.position == core.SourcePosition(5, 1, 6)


def test_word_parse_error_propagates_from_a_worker(worker):
    with pytest.raises(core.WordParseError) as caught:
        worker.submit(core.parse_parameter, "${").result()
    assert caught.value.input == "${"


@pytest.mark.parametrize(
    "node",
    [core.SourcePosition(1, 1, 1), core.TildeExpr.Home(), core.SeparatorOperator.Async],
    ids=lambda node: type(node).__qualname__,
)
def test_foreign_operand_gets_the_reflected_comparison(node):
    assert node == ANY
    assert (node != ANY) is False
    assert [node] == [ANY]


def test_different_node_classes_compare_unequal():
    assert core.SourcePosition(1, 1, 1) != core.Word("x", None)
    assert core.TildeExpr.Home() != core.TildeExpr.WorkingDir()
    assert core.SourcePosition(1, 1, 1) != (1, 1, 1)
