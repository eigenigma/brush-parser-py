from typing import ClassVar, Self, final

from ._ast_commands import UnexpandedArithmeticExpr
from ._word_parameters import (
    Parameter,
    ParameterTestType,
    ParameterTransformOp,
    SubstringMatchKind,
)

class ParameterExpr:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Parameter(ParameterExpr):
        __match_args__ = ("parameter", "indirect")
        def __new__(cls, parameter: Parameter, indirect: bool) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...

    @final
    class UseDefaultValues(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "test_type", "default_value")
        def __new__(
            cls,
            parameter: Parameter,
            indirect: bool,
            test_type: ParameterTestType,
            default_value: str | None,
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def test_type(self) -> ParameterTestType: ...
        @property
        def default_value(self) -> str | None: ...

    @final
    class AssignDefaultValues(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "test_type", "default_value")
        def __new__(
            cls,
            parameter: Parameter,
            indirect: bool,
            test_type: ParameterTestType,
            default_value: str | None,
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def test_type(self) -> ParameterTestType: ...
        @property
        def default_value(self) -> str | None: ...

    @final
    class IndicateErrorIfNullOrUnset(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "test_type", "error_message")
        def __new__(
            cls,
            parameter: Parameter,
            indirect: bool,
            test_type: ParameterTestType,
            error_message: str | None,
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def test_type(self) -> ParameterTestType: ...
        @property
        def error_message(self) -> str | None: ...

    @final
    class UseAlternativeValue(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "test_type", "alternative_value")
        def __new__(
            cls,
            parameter: Parameter,
            indirect: bool,
            test_type: ParameterTestType,
            alternative_value: str | None,
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def test_type(self) -> ParameterTestType: ...
        @property
        def alternative_value(self) -> str | None: ...

    @final
    class ParameterLength(ParameterExpr):
        __match_args__ = ("parameter", "indirect")
        def __new__(cls, parameter: Parameter, indirect: bool) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...

    @final
    class RemoveSmallestSuffixPattern(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "pattern")
        def __new__(
            cls, parameter: Parameter, indirect: bool, pattern: str | None
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str | None: ...

    @final
    class RemoveLargestSuffixPattern(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "pattern")
        def __new__(
            cls, parameter: Parameter, indirect: bool, pattern: str | None
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str | None: ...

    @final
    class RemoveSmallestPrefixPattern(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "pattern")
        def __new__(
            cls, parameter: Parameter, indirect: bool, pattern: str | None
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str | None: ...

    @final
    class RemoveLargestPrefixPattern(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "pattern")
        def __new__(
            cls, parameter: Parameter, indirect: bool, pattern: str | None
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str | None: ...

    @final
    class Substring(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "offset", "length")
        def __new__(
            cls,
            parameter: Parameter,
            indirect: bool,
            offset: UnexpandedArithmeticExpr,
            length: UnexpandedArithmeticExpr | None,
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def offset(self) -> UnexpandedArithmeticExpr: ...
        @property
        def length(self) -> UnexpandedArithmeticExpr | None: ...

    @final
    class Transform(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "op")
        def __new__(
            cls, parameter: Parameter, indirect: bool, op: ParameterTransformOp
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def op(self) -> ParameterTransformOp: ...

    @final
    class UppercaseFirstChar(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "pattern")
        def __new__(
            cls, parameter: Parameter, indirect: bool, pattern: str | None
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str | None: ...

    @final
    class UppercasePattern(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "pattern")
        def __new__(
            cls, parameter: Parameter, indirect: bool, pattern: str | None
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str | None: ...

    @final
    class LowercaseFirstChar(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "pattern")
        def __new__(
            cls, parameter: Parameter, indirect: bool, pattern: str | None
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str | None: ...

    @final
    class LowercasePattern(ParameterExpr):
        __match_args__ = ("parameter", "indirect", "pattern")
        def __new__(
            cls, parameter: Parameter, indirect: bool, pattern: str | None
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str | None: ...

    @final
    class ReplaceSubstring(ParameterExpr):
        __match_args__ = (
            "parameter",
            "indirect",
            "pattern",
            "replacement",
            "match_kind",
        )
        def __new__(
            cls,
            parameter: Parameter,
            indirect: bool,
            pattern: str,
            replacement: str | None,
            match_kind: SubstringMatchKind,
        ) -> Self: ...
        @property
        def parameter(self) -> Parameter: ...
        @property
        def indirect(self) -> bool: ...
        @property
        def pattern(self) -> str: ...
        @property
        def replacement(self) -> str | None: ...
        @property
        def match_kind(self) -> SubstringMatchKind: ...

    @final
    class VariableNames(ParameterExpr):
        __match_args__ = ("prefix", "concatenate")
        def __new__(cls, prefix: str, concatenate: bool) -> Self: ...
        @property
        def prefix(self) -> str: ...
        @property
        def concatenate(self) -> bool: ...

    @final
    class MemberKeys(ParameterExpr):
        __match_args__ = ("variable_name", "concatenate")
        def __new__(cls, variable_name: str, concatenate: bool) -> Self: ...
        @property
        def variable_name(self) -> str: ...
        @property
        def concatenate(self) -> bool: ...
