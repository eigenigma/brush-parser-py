import pytest

from brush_parser import _core as core
from tests._helpers import narrow

X = core.Parameter.Named("x")
UNSET_OR_NULL = core.ParameterTestType.UnsetOrNull
UNSET = core.ParameterTestType.Unset

PARAMETERS = {
    "$1": core.Parameter.Positional(1),
    "$?": core.Parameter.Special(core.SpecialParameter.LastExitStatus()),
    "$@": core.Parameter.Special(
        core.SpecialParameter.AllPositionalParameters(concatenate=False)
    ),
    "$*": core.Parameter.Special(
        core.SpecialParameter.AllPositionalParameters(concatenate=True)
    ),
    "$#": core.Parameter.Special(core.SpecialParameter.PositionalParameterCount()),
    "$-": core.Parameter.Special(core.SpecialParameter.CurrentOptionFlags()),
    "$$": core.Parameter.Special(core.SpecialParameter.ProcessId()),
    "$!": core.Parameter.Special(core.SpecialParameter.LastBackgroundProcessId()),
    "$0": core.Parameter.Special(core.SpecialParameter.ShellName()),
    "$x": X,
    "${x[1]}": core.Parameter.NamedWithIndex("x", "1"),
    "${x[@]}": core.Parameter.NamedWithAllIndices("x", concatenate=False),
    "${x[*]}": core.Parameter.NamedWithAllIndices("x", concatenate=True),
}

DIRECT_X = {"parameter": X, "indirect": False}
ONE = core.UnexpandedArithmeticExpr("1")

EXPRESSIONS = {
    "${!x}": core.ParameterExpr.Parameter(X, indirect=True),
    "${x:-d}": core.ParameterExpr.UseDefaultValues(
        **DIRECT_X, test_type=UNSET_OR_NULL, default_value="d"
    ),
    "${x-d}": core.ParameterExpr.UseDefaultValues(
        **DIRECT_X, test_type=UNSET, default_value="d"
    ),
    "${x:=d}": core.ParameterExpr.AssignDefaultValues(
        **DIRECT_X, test_type=UNSET_OR_NULL, default_value="d"
    ),
    "${x:?m}": core.ParameterExpr.IndicateErrorIfNullOrUnset(
        **DIRECT_X, test_type=UNSET_OR_NULL, error_message="m"
    ),
    "${x:+a}": core.ParameterExpr.UseAlternativeValue(
        **DIRECT_X, test_type=UNSET_OR_NULL, alternative_value="a"
    ),
    "${#x}": core.ParameterExpr.ParameterLength(**DIRECT_X),
    "${x%p}": core.ParameterExpr.RemoveSmallestSuffixPattern(**DIRECT_X, pattern="p"),
    "${x%%p}": core.ParameterExpr.RemoveLargestSuffixPattern(**DIRECT_X, pattern="p"),
    "${x#p}": core.ParameterExpr.RemoveSmallestPrefixPattern(**DIRECT_X, pattern="p"),
    "${x##p}": core.ParameterExpr.RemoveLargestPrefixPattern(**DIRECT_X, pattern="p"),
    "${x:1}": core.ParameterExpr.Substring(**DIRECT_X, offset=ONE, length=None),
    "${x:1:2}": core.ParameterExpr.Substring(
        **DIRECT_X, offset=ONE, length=core.UnexpandedArithmeticExpr("2")
    ),
    "${x^p}": core.ParameterExpr.UppercaseFirstChar(**DIRECT_X, pattern="p"),
    "${x^^p}": core.ParameterExpr.UppercasePattern(**DIRECT_X, pattern="p"),
    "${x,p}": core.ParameterExpr.LowercaseFirstChar(**DIRECT_X, pattern="p"),
    "${x,,p}": core.ParameterExpr.LowercasePattern(**DIRECT_X, pattern="p"),
    "${x/p/r}": core.ParameterExpr.ReplaceSubstring(
        **DIRECT_X,
        pattern="p",
        replacement="r",
        match_kind=core.SubstringMatchKind.FirstOccurrence,
    ),
    "${x//p/r}": core.ParameterExpr.ReplaceSubstring(
        **DIRECT_X,
        pattern="p",
        replacement="r",
        match_kind=core.SubstringMatchKind.Anywhere,
    ),
    "${x/#p/r}": core.ParameterExpr.ReplaceSubstring(
        **DIRECT_X,
        pattern="p",
        replacement="r",
        match_kind=core.SubstringMatchKind.Prefix,
    ),
    "${x/%p}": core.ParameterExpr.ReplaceSubstring(
        **DIRECT_X,
        pattern="p",
        replacement=None,
        match_kind=core.SubstringMatchKind.Suffix,
    ),
    "${!pre@}": core.ParameterExpr.VariableNames("pre", concatenate=False),
    "${!pre*}": core.ParameterExpr.VariableNames("pre", concatenate=True),
    "${!arr[@]}": core.ParameterExpr.MemberKeys("arr", concatenate=False),
    "${!arr[*]}": core.ParameterExpr.MemberKeys("arr", concatenate=True),
}

TRANSFORMS = {
    "u": core.ParameterTransformOp.CapitalizeInitial(),
    "E": core.ParameterTransformOp.ExpandEscapeSequences(),
    "K": core.ParameterTransformOp.PossiblyQuoteWithArraysExpanded(
        separate_words=False
    ),
    "k": core.ParameterTransformOp.PossiblyQuoteWithArraysExpanded(separate_words=True),
    "P": core.ParameterTransformOp.PromptExpand(),
    "Q": core.ParameterTransformOp.Quoted(),
    "A": core.ParameterTransformOp.ToAssignmentLogic(),
    "a": core.ParameterTransformOp.ToAttributeFlags(),
    "L": core.ParameterTransformOp.ToLowerCase(),
    "U": core.ParameterTransformOp.ToUpperCase(),
}


def expansion(text: str) -> core.ParameterExpr:
    pieces = core.parse_word(text)
    assert len(pieces) == 1
    assert isinstance(pieces[0].piece, core.WordPiece.ParameterExpansion)
    return pieces[0].piece.expr


@pytest.mark.parametrize(("text", "parameter"), PARAMETERS.items())
def test_parameter_forms(text, parameter):
    assert expansion(text) == core.ParameterExpr.Parameter(parameter, indirect=False)


@pytest.mark.parametrize(("text", "expr"), EXPRESSIONS.items())
def test_parameter_expressions(text, expr):
    assert expansion(text) == expr


@pytest.mark.parametrize(("letter", "op"), TRANSFORMS.items())
def test_transform_operators(letter, op):
    assert expansion(f"${{x@{letter}}}") == core.ParameterExpr.Transform(
        X, indirect=False, op=op
    )


def test_parse_parameter_takes_the_reference_text():
    assert core.parse_parameter("x") == X
    assert core.parse_parameter("x[1]") == core.Parameter.NamedWithIndex("x", "1")
    assert core.parse_parameter("@") == core.Parameter.Special(
        core.SpecialParameter.AllPositionalParameters(concatenate=False)
    )
    assert core.parse_parameter("3") == core.Parameter.Positional(3)


def test_unit_variants_match_by_class_and_value():
    match narrow(expansion("$?"), core.ParameterExpr.Parameter).parameter:
        case core.Parameter.Special(parameter=core.SpecialParameter.LastExitStatus()):
            pass
        case _:
            pytest.fail("expected $?")
    match expansion("${x-d}"):
        case core.ParameterExpr.UseDefaultValues(
            test_type=core.ParameterTestType.Unset
        ):
            pass
        case _:
            pytest.fail("expected unset-only test")
