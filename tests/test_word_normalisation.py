"""`Word.value` is tokenizer output, so piece offsets are not source offsets."""

from brush_parser import _core as core
from tests._helpers import narrow, suffix_items


def test_backslash_newline_is_dropped_from_word_value():
    item = suffix_items("echo a\\\nb")[0]
    word = narrow(item, core.CommandPrefixOrSuffixItem.Word).word
    assert word.value == "ab"
    assert word.loc is not None
    assert (word.loc.start.index, word.loc.end.index) == (5, 9)
    assert core.parse_word(word.value) == (
        core.WordPieceWithSource(core.WordPiece.Text("ab"), 0, 2),
    )
    assert core.parse_word("a\\\nb")[1].piece == core.WordPiece.EscapeSequence("\\\n")


def test_heredoc_tabs_are_removed_from_body_value():
    item = suffix_items("cat <<-EOF\n\tx\nEOF\n")[0]
    redirect = narrow(item, core.CommandPrefixOrSuffixItem.IoRedirect).redirect
    document = narrow(redirect, core.IoRedirect.HereDocument).document
    assert document.doc.value == "x\n"
    assert document.doc.loc is not None
    assert (document.doc.loc.start.index, document.doc.loc.end.index) == (11, 18)
    assert core.parse_heredoc(document.doc.value) == (
        core.WordPieceWithSource(core.WordPiece.Text("x\n"), 0, 2),
    )


def test_backquote_escape_is_unescaped_inside_the_substitution():
    text = "`a\\`b`"
    assert core.parse_word(text) == (
        core.WordPieceWithSource(
            core.WordPiece.BackquotedCommandSubstitution("a`b"), 0, len(text)
        ),
    )
