"""One class per upstream `ast.rs` type reachable from `parse_program`."""

import inspect

import brush_parser
from brush_parser import _core as core

SOURCE_CLASSES = {"SourcePosition", "SourceSpan"}
ERROR_CLASSES = {"ParseError", "WordParseError"}
AST_CLASSES = {
    "AndOr",
    "AndOrList",
    "ArithmeticCommand",
    "ArithmeticForClauseCommand",
    "Assignment",
    "AssignmentName",
    "AssignmentValue",
    "BinaryPredicate",
    "BraceGroupCommand",
    "CaseClauseCommand",
    "CaseItem",
    "CaseItemPostAction",
    "Command",
    "CommandPrefix",
    "CommandPrefixOrSuffixItem",
    "CommandSuffix",
    "CompoundCommand",
    "CompoundList",
    "CompoundListItem",
    "CoprocessCommand",
    "DoGroupCommand",
    "ElseClause",
    "ExtendedTestExpr",
    "ExtendedTestExprCommand",
    "ForClauseCommand",
    "FunctionBody",
    "FunctionDefinition",
    "IfClauseCommand",
    "IoFileRedirectKind",
    "IoFileRedirectTarget",
    "IoHereDocument",
    "IoRedirect",
    "Pipeline",
    "PipelineTimed",
    "ProcessSubstitutionKind",
    "Program",
    "RedirectList",
    "SeparatorOperator",
    "SimpleCommand",
    "SubshellCommand",
    "UnaryPredicate",
    "UnexpandedArithmeticExpr",
    "WhileOrUntilClauseCommand",
    "Word",
}
WORD_CLASSES = {
    "BraceExpressionMember",
    "BraceExpressionOrText",
    "Parameter",
    "ParameterExpr",
    "ParameterTestType",
    "ParameterTransformOp",
    "SpecialParameter",
    "SubstringMatchKind",
    "TildeExpr",
    "WordPiece",
    "WordPieceWithSource",
}
CLASSES = SOURCE_CLASSES | ERROR_CLASSES | AST_CLASSES | WORD_CLASSES
FUNCTIONS = {
    "parse_program",
    "parse_word",
    "parse_heredoc",
    "parse_parameter",
    "parse_brace_expansions",
}
CONSTANTS = {"BRUSH_PARSER_VERSION"}


def public_names(module: object) -> set[str]:
    return {name for name in dir(module) if not name.startswith("_")}


def test_core_exports_exactly_the_registered_names():
    assert public_names(core) == CLASSES | FUNCTIONS | CONSTANTS


def test_package_reexports_everything():
    assert public_names(brush_parser) >= public_names(core) - {"core"}
    assert set(brush_parser.__all__) == public_names(core)


def test_every_class_reports_the_core_module():
    for name in CLASSES:
        cls = getattr(core, name)
        assert inspect.isclass(cls), name
        assert cls.__module__ == "brush_parser._core", name


def test_variant_classes_report_the_core_module():
    for name in AST_CLASSES | WORD_CLASSES:
        cls = getattr(core, name)
        for attribute in vars(cls).values():
            if inspect.isclass(attribute) and issubclass(attribute, cls):
                assert attribute.__module__ == "brush_parser._core", attribute


def test_version_constant():
    assert core.BRUSH_PARSER_VERSION == "0.4.0"
