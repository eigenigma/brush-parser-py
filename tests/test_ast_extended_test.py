import pytest

from brush_parser import _core as core
from tests._helpers import first_command, narrow, span, word

UNARY = {
    "-e": core.UnaryPredicate.FileExists,
    "-b": core.UnaryPredicate.FileExistsAndIsBlockSpecialFile,
    "-c": core.UnaryPredicate.FileExistsAndIsCharSpecialFile,
    "-d": core.UnaryPredicate.FileExistsAndIsDir,
    "-f": core.UnaryPredicate.FileExistsAndIsRegularFile,
    "-g": core.UnaryPredicate.FileExistsAndIsSetgid,
    "-h": core.UnaryPredicate.FileExistsAndIsSymlink,
    "-k": core.UnaryPredicate.FileExistsAndHasStickyBit,
    "-p": core.UnaryPredicate.FileExistsAndIsFifo,
    "-r": core.UnaryPredicate.FileExistsAndIsReadable,
    "-s": core.UnaryPredicate.FileExistsAndIsNotZeroLength,
    "-t": core.UnaryPredicate.FdIsOpenTerminal,
    "-u": core.UnaryPredicate.FileExistsAndIsSetuid,
    "-w": core.UnaryPredicate.FileExistsAndIsWritable,
    "-x": core.UnaryPredicate.FileExistsAndIsExecutable,
    "-G": core.UnaryPredicate.FileExistsAndOwnedByEffectiveGroupId,
    "-N": core.UnaryPredicate.FileExistsAndModifiedSinceLastRead,
    "-O": core.UnaryPredicate.FileExistsAndOwnedByEffectiveUserId,
    "-S": core.UnaryPredicate.FileExistsAndIsSocket,
    "-o": core.UnaryPredicate.ShellOptionEnabled,
    "-v": core.UnaryPredicate.ShellVariableIsSetAndAssigned,
    "-R": core.UnaryPredicate.ShellVariableIsSetAndNameRef,
    "-z": core.UnaryPredicate.StringHasZeroLength,
    "-n": core.UnaryPredicate.StringHasNonZeroLength,
}

BINARY = {
    "-ef": core.BinaryPredicate.FilesReferToSameDeviceAndInodeNumbers,
    "-nt": core.BinaryPredicate.LeftFileIsNewerOrExistsWhenRightDoesNot,
    "-ot": core.BinaryPredicate.LeftFileIsOlderOrDoesNotExistWhenRightDoes,
    "==": core.BinaryPredicate.StringExactlyMatchesPattern,
    "=": core.BinaryPredicate.StringExactlyMatchesPattern,
    "!=": core.BinaryPredicate.StringDoesNotExactlyMatchPattern,
    "=~": core.BinaryPredicate.StringMatchesRegex,
    "<": core.BinaryPredicate.LeftSortsBeforeRight,
    ">": core.BinaryPredicate.LeftSortsAfterRight,
    "-eq": core.BinaryPredicate.ArithmeticEqualTo,
    "-ne": core.BinaryPredicate.ArithmeticNotEqualTo,
    "-lt": core.BinaryPredicate.ArithmeticLessThan,
    "-le": core.BinaryPredicate.ArithmeticLessThanOrEqualTo,
    "-gt": core.BinaryPredicate.ArithmeticGreaterThan,
    "-ge": core.BinaryPredicate.ArithmeticGreaterThanOrEqualTo,
}


def extended_test(text: str) -> core.ExtendedTestExprCommand:
    return narrow(first_command(text), core.Command.ExtendedTest).command


def expr(text: str) -> core.ExtendedTestExpr:
    return extended_test(text).expr


def binary(text: str) -> core.ExtendedTestExpr.BinaryTest:
    return narrow(expr(text), core.ExtendedTestExpr.BinaryTest)


def test_command_carries_span_of_the_brackets():
    assert extended_test("[[ -n x ]]").loc == span(0, 10)


@pytest.mark.parametrize(("operator", "predicate"), UNARY.items())
def test_unary_predicates(operator, predicate):
    assert expr(f"[[ {operator} x ]]") == core.ExtendedTestExpr.UnaryTest(
        predicate, word("x", 6)
    )


@pytest.mark.parametrize(("operator", "predicate"), BINARY.items())
def test_binary_predicates(operator, predicate):
    parsed = expr(f"[[ a {operator} b ]]")
    right = word("b", 6 + len(operator))
    if operator == "=~":
        right = core.Word("b", None)
    assert parsed == core.ExtendedTestExpr.BinaryTest(predicate, word("a", 3), right)


def test_regex_operand_has_no_location_upstream():
    assert binary("[[ a =~ b ]]").right.loc is None


def test_quoted_regex_is_substring_containment():
    parsed = binary("[[ a =~ 'b c' ]]")
    assert parsed.predicate == core.BinaryPredicate.StringContainsSubstring
    assert parsed.right == core.Word("'b c'", None)


def test_string_match_predicates_are_constructible():
    for predicate in (
        core.BinaryPredicate.StringExactlyMatchesString,
        core.BinaryPredicate.StringDoesNotExactlyMatchString,
    ):
        node = core.ExtendedTestExpr.BinaryTest(
            predicate, core.Word("a", None), core.Word("b", None)
        )
        assert node.predicate == predicate


def test_logical_structure():
    parsed = narrow(expr("[[ ! -e x || ( -d y ) && -z z ]]"), core.ExtendedTestExpr.Or)
    assert parsed.left == core.ExtendedTestExpr.Not(
        core.ExtendedTestExpr.UnaryTest(core.UnaryPredicate.FileExists, word("x", 8))
    )
    conjunction = narrow(parsed.right, core.ExtendedTestExpr.And)
    assert isinstance(conjunction.left, core.ExtendedTestExpr.Parenthesized)
    assert conjunction.right == core.ExtendedTestExpr.UnaryTest(
        core.UnaryPredicate.StringHasZeroLength, word("z", 28)
    )
