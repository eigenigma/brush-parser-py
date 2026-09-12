import inspect

import pytest

from brush_parser import _core as core


def test_parse_error_is_a_value_error_with_module():
    assert issubclass(core.ParseError, ValueError)
    assert issubclass(core.WordParseError, ValueError)
    assert core.ParseError.__module__ == "brush_parser._core"


def test_error_near_a_token_carries_its_position():
    with pytest.raises(core.ParseError) as caught:
        core.parse_program("echo )")
    assert str(caught.value) == "syntax error at line 1 col 6"
    assert caught.value.position == core.SourcePosition(5, 1, 6)


def test_error_at_end_of_input_has_no_position():
    with pytest.raises(core.ParseError) as caught:
        core.parse_program("echo (")
    assert str(caught.value) == "syntax error at end of input"
    assert caught.value.position is None


def test_tokenizer_error_carries_its_position_and_message():
    with pytest.raises(core.ParseError) as caught:
        core.parse_program("echo $(")
    assert str(caught.value) == "unterminated expansion (detected near line 1 col 8)"
    assert caught.value.position == core.SourcePosition(7, 1, 8)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("echo 'x", "unterminated single quote at 1,6"),
        ('echo "x', "unterminated double quote at 1,6"),
        ("echo `x", "unterminated backquote near 1,6"),
        ("cat <<EOF\nx\n", "unterminated here document sequence; tag(s) [EOF]"),
    ],
)
def test_tokenizer_messages_are_upstream_display_text(text, message):
    with pytest.raises(core.ParseError) as caught:
        core.parse_program(text)
    assert str(caught.value).startswith(message)


def test_position_is_a_real_source_position_object():
    with pytest.raises(core.ParseError) as caught:
        core.parse_program("echo ;;")
    position = caught.value.position
    assert isinstance(position, core.SourcePosition)
    assert (position.index, position.line, position.column) == (5, 1, 6)


def test_word_parse_error_carries_input_and_peg_diagnostic():
    with pytest.raises(core.WordParseError) as caught:
        core.parse_parameter("${")
    assert str(caught.value) == (
        "failed to parse parameter '${': error at 1:2: expected EOF"
    )
    assert caught.value.input == "${"


def test_brace_parse_error_names_the_word():
    with pytest.raises(core.WordParseError) as caught:
        core.parse_parameter("a{1..")
    assert str(caught.value).startswith("failed to parse parameter 'a{1..': error at")
    assert caught.value.input == "a{1.."


@pytest.mark.parametrize(
    ("function", "first"),
    [
        (core.parse_program, "text"),
        (core.parse_word, "word"),
        (core.parse_heredoc, "word"),
        (core.parse_parameter, "word"),
        (core.parse_brace_expansions, "word"),
    ],
)
def test_options_are_keyword_only_with_upstream_defaults(function, first):
    parameters = inspect.signature(function).parameters
    assert next(iter(parameters)) == first
    assert parameters[first].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    options = {
        name: parameter.default
        for name, parameter in parameters.items()
        if parameter.kind is inspect.Parameter.KEYWORD_ONLY
    }
    assert options == {
        "enable_extended_globbing": True,
        "posix_mode": False,
        "sh_mode": False,
        "tilde_expansion_at_word_start": True,
        "tilde_expansion_after_colon": False,
    }


def test_options_reach_the_tokenizer_and_parser():
    core.parse_program("echo @(a|b)")
    with pytest.raises(core.ParseError):
        core.parse_program("echo @(a|b)", enable_extended_globbing=False)
    core.parse_program("a=(1 2)")
    with pytest.raises(core.ParseError):
        core.parse_program("a=(1 2)", sh_mode=True)
