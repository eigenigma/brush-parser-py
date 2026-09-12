import pytest

from brush_parser import _core as core
from tests._helpers import (
    compound,
    first_command,
    narrow,
    prefix_items,
    simple_command,
    span,
    suffix_items,
    word,
)


def test_command_variants():
    assert isinstance(first_command("a"), core.Command.Simple)
    assert isinstance(first_command("{ a; }"), core.Command.Compound)
    assert isinstance(first_command("f() { a; }"), core.Command.Function)
    assert isinstance(first_command("[[ -n x ]]"), core.Command.ExtendedTest)


def test_compound_and_extended_test_carry_redirects():
    grouped = narrow(first_command("{ a; } >f"), core.Command.Compound)
    assert grouped.redirects == core.RedirectList(
        (
            core.IoRedirect.File(
                None,
                core.IoFileRedirectKind.Write,
                core.IoFileRedirectTarget.Filename(word("f", 8)),
            ),
        )
    )
    assert narrow(first_command("{ a; }"), core.Command.Compound).redirects is None

    test = narrow(first_command("[[ -n x ]] 2>e"), core.Command.ExtendedTest)
    assert test.redirects is not None
    assert narrow(test.redirects.items[0], core.IoRedirect.File).fd == 2
    bare = narrow(first_command("[[ -n x ]]"), core.Command.ExtendedTest)
    assert bare.redirects is None


def test_simple_command_prefix_name_suffix():
    command = simple_command("A=1 cmd arg")
    assert command.word_or_name == word("cmd", 4)
    assert command.prefix == core.CommandPrefix(
        (
            core.CommandPrefixOrSuffixItem.AssignmentWord(
                core.Assignment(
                    core.AssignmentName.VariableName("A"),
                    core.AssignmentValue.Scalar(core.Word("1", None)),
                    append=False,
                    loc=span(0, 3),
                ),
                word("A=1", 0),
            ),
        )
    )
    assert command.suffix == core.CommandSuffix(
        (core.CommandPrefixOrSuffixItem.Word(word("arg", 8)),)
    )


def test_assignment_only_command_has_no_name():
    command = simple_command("A=1")
    assert command.word_or_name is None
    assert command.suffix is None


def test_prefix_or_suffix_item_variants():
    items = suffix_items("A=1 cmd <(x) >(y) >f")
    assert [type(item).__qualname__ for item in items] == [
        "CommandPrefixOrSuffixItem.ProcessSubstitution",
        "CommandPrefixOrSuffixItem.ProcessSubstitution",
        "CommandPrefixOrSuffixItem.IoRedirect",
    ]
    read = narrow(items[0], core.CommandPrefixOrSuffixItem.ProcessSubstitution)
    write = narrow(items[1], core.CommandPrefixOrSuffixItem.ProcessSubstitution)
    assert read.kind == core.ProcessSubstitutionKind.Read
    assert write.kind == core.ProcessSubstitutionKind.Write
    assert read.command.loc == span(9, 12)


def test_assignment_names_values_and_append():
    array_element, appended, array = (
        narrow(item, core.CommandPrefixOrSuffixItem.AssignmentWord).assignment
        for item in prefix_items("a[1]=x b+=2 c=(1 [k]=v)")
    )
    assert array_element.name == core.AssignmentName.ArrayElementName("a", "1")
    assert array_element.append is False
    assert appended.name == core.AssignmentName.VariableName("b")
    assert appended.append is True
    assert array.value == core.AssignmentValue.Array(
        (
            (None, core.Word("1", None)),
            (core.Word("k", None), core.Word("v", None)),
        )
    )
    assert array.loc == span(12, 23)


@pytest.mark.parametrize(
    "elements",
    [
        ((None, "x"),),
        (("a",),),
        ((None, []),),
        ((None, core.Word("w", None), 3),),
        ([None, core.Word("w", None)],),
    ],
    ids=["str-word", "one-item", "list-word", "three-items", "list-pair"],
)
def test_array_elements_are_checked_as_word_pairs(elements):
    with pytest.raises((TypeError, ValueError)):
        core.AssignmentValue.Array(elements)


def test_array_elements_are_stored_as_a_tuple_of_pairs():
    pair = (None, core.Word("w", None))
    assert core.AssignmentValue.Array((pair,)).elements == (pair,)


def test_assignment_value_words_have_no_location():
    item = narrow(prefix_items("a=b")[0], core.CommandPrefixOrSuffixItem.AssignmentWord)
    scalar = narrow(item.assignment.value, core.AssignmentValue.Scalar)
    assert scalar.word.loc is None
    assert item.word.loc == span(0, 3)


def test_function_definition_bodies():
    brace = narrow(first_command("function f { a; }"), core.Command.Function)
    assert brace.definition.fname == word("f", 9)
    assert isinstance(brace.definition.body.command, core.CompoundCommand.BraceGroup)
    assert brace.definition.body.redirects is None

    subshell = narrow(first_command("f() ( a ) 2>e"), core.Command.Function)
    assert subshell.definition.fname == word("f", 0)
    assert isinstance(subshell.definition.body.command, core.CompoundCommand.Subshell)
    redirects = subshell.definition.body.redirects
    assert redirects is not None
    assert narrow(redirects.items[0], core.IoRedirect.File).fd == 2


def test_unexpanded_arithmetic_expr():
    arithmetic = compound("(( x+1 ))", core.CompoundCommand.Arithmetic)
    assert arithmetic.command.expr == core.UnexpandedArithmeticExpr("x+1")
