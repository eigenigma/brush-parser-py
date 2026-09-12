import pytest

from brush_parser import _core as core
from tests._helpers import compound, first_command, narrow, span, word


@pytest.mark.parametrize(
    ("text", "variant"),
    [
        ("(( x ))", core.CompoundCommand.Arithmetic),
        ("for (( ; ; )); do a; done", core.CompoundCommand.ArithmeticForClause),
        ("{ a; }", core.CompoundCommand.BraceGroup),
        ("( a )", core.CompoundCommand.Subshell),
        ("for x in a; do b; done", core.CompoundCommand.ForClause),
        ("case x in a) ;; esac", core.CompoundCommand.CaseClause),
        ("if a; then b; fi", core.CompoundCommand.IfClause),
        ("while a; do b; done", core.CompoundCommand.WhileClause),
        ("until a; do b; done", core.CompoundCommand.UntilClause),
        ("coproc a", core.CompoundCommand.Coprocess),
    ],
)
def test_compound_command_variants(text, variant):
    assert isinstance(compound(text, variant), variant)


def test_arithmetic_command():
    command = compound("(( x+1 ))", core.CompoundCommand.Arithmetic).command
    assert command == core.ArithmeticCommand(
        core.UnexpandedArithmeticExpr("x+1"), span(0, 9)
    )


def test_arithmetic_for_clause():
    loop = core.CompoundCommand.ArithmeticForClause
    command = compound("for ((i=0; i<3; i++)); do a; done", loop).command
    assert command.initializer == core.UnexpandedArithmeticExpr("i=0")
    assert command.condition == core.UnexpandedArithmeticExpr("i<3")
    assert command.updater == core.UnexpandedArithmeticExpr("i++")
    assert command.body.loc == span(23, 33)
    assert command.loc == span(0, 33)

    empty = compound("for (( ; ; )); do a; done", loop).command
    blank = core.UnexpandedArithmeticExpr("")
    assert (empty.initializer, empty.condition, empty.updater) == (blank, blank, blank)


def test_upstream_rejects_unspaced_empty_arithmetic_for():
    with pytest.raises(core.ParseError):
        core.parse_program("for ((;;)); do a; done")


def test_brace_group_and_subshell():
    group = compound("{ a; }", core.CompoundCommand.BraceGroup).command
    assert group.loc == span(0, 6)
    first = narrow(group.list.items[0].list.first.seq[0], core.Command.Simple)
    assert first.command.word_or_name == word("a", 2)

    subshell = compound("( a )", core.CompoundCommand.Subshell).command
    assert subshell.loc == span(0, 5)


def test_for_clause_values():
    command = compound("for x in a b; do c; done", core.CompoundCommand.ForClause)
    assert command.command.variable_name == "x"
    assert command.command.values == (word("a", 9), word("b", 11))
    assert isinstance(command.command.body, core.DoGroupCommand)

    positional = compound("for x; do c; done", core.CompoundCommand.ForClause)
    assert positional.command.values is None


def test_case_clause_items_and_post_actions():
    text = "case $x in a|b) echo;;& *) ;; c) ;& esac"
    command = compound(text, core.CompoundCommand.CaseClause).command
    assert command.value == word("$x", 5)
    first, second, third = command.cases
    assert first.patterns == (word("a", 11), word("b", 13))
    assert first.cmd is not None
    assert first.post_action == core.CaseItemPostAction.ContinueEvaluatingCases
    assert second.patterns == (word("*", 24),)
    assert second.cmd is None
    assert second.post_action == core.CaseItemPostAction.ExitCase
    assert (
        third.post_action == core.CaseItemPostAction.UnconditionallyExecuteNextCaseItem
    )
    assert third.loc == span(30, 35)


def test_if_clause_with_elif_and_else():
    text = "if a; then b; elif c; then d; else e; fi"
    command = compound(text, core.CompoundCommand.IfClause).command
    assert isinstance(command.condition, core.CompoundList)
    assert isinstance(command.then, core.CompoundList)
    assert command.elses is not None
    elif_clause, else_clause = command.elses
    assert elif_clause.condition is not None
    assert else_clause.condition is None
    plain = compound("if a; then b; fi", core.CompoundCommand.IfClause)
    assert plain.command.elses is None


def test_while_and_until_share_one_shape():
    loop = compound("until a; do b; done", core.CompoundCommand.UntilClause).command
    assert isinstance(loop, core.WhileOrUntilClauseCommand)
    condition = narrow(loop.condition.items[0].list.first.seq[0], core.Command.Simple)
    assert condition.command.word_or_name == word("a", 6)
    assert loop.body.loc == span(9, 19)
    assert loop.loc == span(0, 19)


def test_coprocess_with_and_without_name():
    unnamed = compound("coproc a", core.CompoundCommand.Coprocess).command
    assert unnamed.name is None
    assert isinstance(unnamed.body, core.Command.Simple)
    assert unnamed.loc == span(0, 8)

    named = compound("coproc n { a; }", core.CompoundCommand.Coprocess).command
    assert named.name == word("n", 7)
    assert isinstance(named.body, core.Command.Compound)


def test_function_body_is_a_compound_command_with_redirects():
    command = narrow(first_command("f() { a; } >o"), core.Command.Function)
    body = command.definition.body
    assert body == core.FunctionBody(body.command, body.redirects)
    assert isinstance(body.command, core.CompoundCommand.BraceGroup)
    assert body.redirects is not None
    redirect = narrow(body.redirects.items[0], core.IoRedirect.File)
    assert redirect.target == core.IoFileRedirectTarget.Filename(word("o", 12))
