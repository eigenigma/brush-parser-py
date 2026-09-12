from brush_parser import _core as core
from tests._helpers import narrow

Text = core.BraceExpressionOrText.Text
Expr = core.BraceExpressionOrText.Expr
Child = core.BraceExpressionMember.Child


def test_nested_expressions_and_sequences():
    assert core.parse_brace_expansions("a{b,c{d,e}}f{1..5..2}{a..c}") == (
        Text("a"),
        Expr(
            (
                Child((Text("b"),)),
                Child(
                    (
                        Text("c"),
                        Expr((Child((Text("d"),)), Child((Text("e"),)))),
                    )
                ),
            )
        ),
        Text("f"),
        Expr((core.BraceExpressionMember.NumberSequence(1, 5, 2),)),
        Expr((core.BraceExpressionMember.CharSequence("a", "c", 1),)),
    )


def test_word_without_braces_is_a_single_text():
    assert core.parse_brace_expansions("plain") == (Text("plain"),)


def test_char_sequence_bounds_are_one_char_strings():
    expansions = core.parse_brace_expansions("{a..c}")
    assert expansions is not None
    members = narrow(expansions[0], Expr).members
    member = narrow(members[0], core.BraceExpressionMember.CharSequence)
    assert (member.start, member.end, member.increment) == ("a", "c", 1)
