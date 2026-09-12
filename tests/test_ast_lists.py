import pytest

from brush_parser import _core as core
from tests._helpers import (
    first_command,
    list_item,
    narrow,
    pipeline,
    program,
    simple,
    span,
    word,
)


def test_full_tree_for_a_simple_command():
    expected = program(
        list_item(
            pipeline(
                simple(
                    word("echo", 0),
                    core.CommandPrefixOrSuffixItem.Word(word("hi", 5)),
                )
            )
        )
    )
    assert core.parse_program("echo hi") == expected


def test_separators_and_newlines():
    parsed = core.parse_program("a; b &\nc")
    first, second = parsed.complete_commands
    assert [item.separator for item in first.items] == [
        core.SeparatorOperator.Sequence,
        core.SeparatorOperator.Async,
    ]
    assert [item.separator for item in second.items] == [
        core.SeparatorOperator.Sequence
    ]


def test_and_or_chain():
    parsed = core.parse_program("a && b || c")
    and_or = parsed.complete_commands[0].items[0].list
    assert and_or.first == pipeline(simple(word("a", 0)))
    assert and_or.additional == (
        core.AndOr.And(pipeline(simple(word("b", 5)))),
        core.AndOr.Or(pipeline(simple(word("c", 10)))),
    )


def test_pipeline_bang_and_timing():
    parsed = core.parse_program("time ! a | b")
    pipe = parsed.complete_commands[0].items[0].list.first
    assert pipe.timed == core.PipelineTimed.Timed(span(0, 4))
    assert pipe.bang is True
    names = [
        narrow(command, core.Command.Simple).command.word_or_name
        for command in pipe.seq
    ]
    assert names == [word("a", 7), word("b", 11)]

    posix = core.parse_program("time -p a").complete_commands[0].items[0].list.first
    assert posix.timed == core.PipelineTimed.TimedWithPosixOutput(span(0, 7))
    assert posix.bang is False


def test_sequences_are_tuples_materialised_once():
    parsed = core.parse_program("a | b")
    seq = parsed.complete_commands[0].items[0].list.first.seq
    assert isinstance(seq, tuple)
    assert parsed.complete_commands is parsed.complete_commands
    assert parsed.complete_commands[0].items[0].list.first.seq is seq


def test_structural_equality_and_inequality():
    left = core.parse_program("echo a")
    assert left == core.parse_program("echo a")
    assert left != core.parse_program("echo b")
    assert left != core.parse_program("echo  a")
    assert left != "echo a"
    assert word("a", 0) != core.Word("a", None)


def test_repr_names_class_and_fields():
    assert repr(word("hi", 5)) == (
        "Word(value='hi', loc=SourceSpan("
        "start=SourcePosition(index=5, line=1, column=6), "
        "end=SourcePosition(index=7, line=1, column=8)))"
    )
    assert repr(core.AndOr.And(pipeline(simple(core.Word("a", None))))) == (
        "AndOr.And(pipeline=Pipeline(timed=None, bang=False, seq=("
        "Command.Simple(command=SimpleCommand(prefix=None, "
        "word_or_name=Word(value='a', loc=None), suffix=None)),)))"
    )
    assert repr(core.SeparatorOperator.Async) == "SeparatorOperator.Async"
    assert repr(core.AssignmentValue.Array(((None, core.Word("1", None)),))) == (
        "AssignmentValue.Array(elements=((None, Word(value='1', loc=None)),))"
    )


def test_nodes_are_unhashable():
    with pytest.raises(TypeError):
        hash(core.Word("a", None))
    with pytest.raises(TypeError):
        hash(core.SeparatorOperator.Async)
    with pytest.raises(TypeError):
        hash(first_command("a"))


def test_nodes_are_frozen():
    node = core.Word("a", None)
    attribute = "value"
    with pytest.raises(AttributeError):
        setattr(node, attribute, "b")


def test_match_on_variant_class():
    match first_command("echo hi"):
        case core.Command.Simple(command=core.SimpleCommand(word_or_name=name)):
            assert name is not None
            assert name.value == "echo"
        case _:
            pytest.fail("expected Command.Simple")


def test_variant_classes_are_subclasses():
    command = first_command("echo")
    assert isinstance(command, core.Command)
    assert isinstance(command, core.Command.Simple)
    assert type(command).__qualname__ == "Command.Simple"
    assert core.Command.Simple.__match_args__ == ("command",)
    assert core.Word.__match_args__ == ("value", "loc")


def test_source_positions():
    parsed = core.parse_program("true;\n  echo hi")
    second = parsed.complete_commands[1].items[0].list.first.seq[0]
    suffix = narrow(second, core.Command.Simple).command.suffix
    assert suffix is not None
    name = narrow(suffix.items[0], core.CommandPrefixOrSuffixItem.Word).word
    assert name.loc == core.SourceSpan(
        core.SourcePosition(13, 2, 8), core.SourcePosition(15, 2, 10)
    )
