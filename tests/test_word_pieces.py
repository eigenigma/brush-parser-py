import pytest

from brush_parser import _core as core
from tests._helpers import narrow


def piece(text: str, **options: bool) -> core.WordPieceWithSource:
    pieces = core.parse_word(text, **options)
    assert len(pieces) == 1
    return pieces[0]


def named(name: str) -> core.WordPiece:
    return core.WordPiece.ParameterExpansion(
        core.ParameterExpr.Parameter(core.Parameter.Named(name), indirect=False)
    )


def test_plain_text():
    assert core.parse_word("abc") == (
        core.WordPieceWithSource(core.WordPiece.Text("abc"), 0, 3),
    )


def test_offsets_are_char_indices_into_the_word():
    text = 'echo "héllo $X" x'
    pieces = core.parse_word(text)
    assert [(p.start, p.end) for p in pieces] == [(0, 5), (5, 15), (15, 17)]
    inner = narrow(pieces[1].piece, core.WordPiece.DoubleQuotedSequence).pieces
    assert [(p.start, p.end) for p in inner] == [(6, 12), (12, 14)]
    assert text[inner[0].start : inner[0].end] == "héllo "
    assert text[inner[1].start : inner[1].end] == "$X"
    assert pieces[1] == core.WordPieceWithSource(
        core.WordPiece.DoubleQuotedSequence(
            (
                core.WordPieceWithSource(core.WordPiece.Text("héllo "), 6, 12),
                core.WordPieceWithSource(named("X"), 12, 14),
            )
        ),
        5,
        15,
    )


def test_end_of_word_offset_after_multibyte_text():
    assert [(p.start, p.end) for p in core.parse_word('"é" $x')] == [
        (0, 3),
        (3, 4),
        (4, 6),
    ]


def test_offsets_stay_char_indices_across_many_multibyte_pieces():
    text = "é$x" * 1000
    pieces = core.parse_word(text)
    assert len(pieces) == 2000
    assert [(p.start, p.end) for p in pieces[-2:]] == [(2997, 2998), (2998, 3000)]
    assert text[pieces[-1].start : pieces[-1].end] == "$x"


def test_quoting_forms():
    assert core.parse_word("a'b c'\\ d$'e\\n'") == (
        core.WordPieceWithSource(core.WordPiece.Text("a"), 0, 1),
        core.WordPieceWithSource(core.WordPiece.SingleQuotedText("b c"), 1, 6),
        core.WordPieceWithSource(core.WordPiece.EscapeSequence("\\ "), 6, 8),
        core.WordPieceWithSource(core.WordPiece.Text("d"), 8, 9),
        core.WordPieceWithSource(core.WordPiece.AnsiCQuotedText("e\\n"), 9, 15),
    )


def test_gettext_double_quotes():
    assert piece('$"x $y"').piece == core.WordPiece.GettextDoubleQuotedSequence(
        (
            core.WordPieceWithSource(core.WordPiece.Text("x "), 2, 4),
            core.WordPieceWithSource(named("y"), 4, 6),
        )
    )


@pytest.mark.parametrize(
    ("text", "expr"),
    [
        ("~", core.TildeExpr.Home()),
        ("~+", core.TildeExpr.WorkingDir()),
        ("~-", core.TildeExpr.OldWorkingDir()),
        ("~+2", core.TildeExpr.NthDirFromTopOfDirStack(2, plus_used=True)),
        ("~3", core.TildeExpr.NthDirFromTopOfDirStack(3, plus_used=False)),
        ("~-2", core.TildeExpr.NthDirFromBottomOfDirStack(2)),
    ],
)
def test_tilde_forms(text, expr):
    assert piece(text) == core.WordPieceWithSource(
        core.WordPiece.TildeExpansion(expr), 0, len(text)
    )


def test_tilde_user_then_text():
    assert core.parse_word("~bob/x") == (
        core.WordPieceWithSource(
            core.WordPiece.TildeExpansion(core.TildeExpr.UserHome("bob")), 0, 4
        ),
        core.WordPieceWithSource(core.WordPiece.Text("/x"), 4, 6),
    )


def test_tilde_options():
    assert piece("~", tilde_expansion_at_word_start=False).piece == (
        core.WordPiece.Text("~")
    )
    assert core.parse_word("a:~b")[0].piece == core.WordPiece.Text("a:~b")
    assert core.parse_word("a:~b", tilde_expansion_after_colon=True) == (
        core.WordPieceWithSource(core.WordPiece.Text("a:"), 0, 2),
        core.WordPieceWithSource(
            core.WordPiece.TildeExpansion(core.TildeExpr.UserHome("b")), 2, 4
        ),
    )


def test_substitutions_keep_unparsed_text():
    assert core.parse_word("$(ls -l)`date`$((1+2))") == (
        core.WordPieceWithSource(core.WordPiece.CommandSubstitution("ls -l"), 0, 8),
        core.WordPieceWithSource(
            core.WordPiece.BackquotedCommandSubstitution("date"), 8, 14
        ),
        core.WordPieceWithSource(
            core.WordPiece.ArithmeticExpression(core.UnexpandedArithmeticExpr("1+2")),
            14,
            22,
        ),
    )


def test_heredoc_treats_quotes_as_text():
    body = "a 'b' \"c\" $x"
    assert core.parse_heredoc(body) == (
        core.WordPieceWithSource(core.WordPiece.Text("a 'b' \"c\" "), 0, 10),
        core.WordPieceWithSource(named("x"), 10, 12),
    )
    as_word = core.parse_word(body)
    assert len(as_word) == 6
    assert as_word[1].piece == core.WordPiece.SingleQuotedText("b")


def test_lone_surrogate_is_rejected_at_the_boundary():
    with pytest.raises(UnicodeEncodeError):
        core.parse_word("\udc80")
    with pytest.raises(UnicodeEncodeError):
        core.parse_program("echo \udc80")


def test_pieces_are_tuples_of_frozen_nodes():
    pieces = core.parse_word("a$b")
    assert isinstance(pieces, tuple)
    attribute = "start"
    with pytest.raises(AttributeError):
        setattr(pieces[0], attribute, 3)
    with pytest.raises(TypeError):
        hash(pieces[0])
