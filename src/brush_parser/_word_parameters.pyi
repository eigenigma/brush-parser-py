from typing import ClassVar, Self, final

@final
class ParameterTestType:
    UnsetOrNull: ClassVar[ParameterTestType]
    Unset: ClassVar[ParameterTestType]
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...

class Parameter:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Positional(Parameter):
        __match_args__ = ("index",)
        def __new__(cls, index: int) -> Self: ...
        @property
        def index(self) -> int: ...

    @final
    class Special(Parameter):
        __match_args__ = ("parameter",)
        def __new__(cls, parameter: SpecialParameter) -> Self: ...
        @property
        def parameter(self) -> SpecialParameter: ...

    @final
    class Named(Parameter):
        __match_args__ = ("name",)
        def __new__(cls, name: str) -> Self: ...
        @property
        def name(self) -> str: ...

    @final
    class NamedWithIndex(Parameter):
        __match_args__ = ("name", "index")
        def __new__(cls, name: str, index: str) -> Self: ...
        @property
        def name(self) -> str: ...
        @property
        def index(self) -> str: ...

    @final
    class NamedWithAllIndices(Parameter):
        __match_args__ = ("name", "concatenate")
        def __new__(cls, name: str, concatenate: bool) -> Self: ...
        @property
        def name(self) -> str: ...
        @property
        def concatenate(self) -> bool: ...

class SpecialParameter:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class AllPositionalParameters(SpecialParameter):
        __match_args__ = ("concatenate",)
        def __new__(cls, concatenate: bool) -> Self: ...
        @property
        def concatenate(self) -> bool: ...

    @final
    class PositionalParameterCount(SpecialParameter):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class LastExitStatus(SpecialParameter):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class CurrentOptionFlags(SpecialParameter):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class ProcessId(SpecialParameter):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class LastBackgroundProcessId(SpecialParameter):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class ShellName(SpecialParameter):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

@final
class SubstringMatchKind:
    Prefix: ClassVar[SubstringMatchKind]
    Suffix: ClassVar[SubstringMatchKind]
    FirstOccurrence: ClassVar[SubstringMatchKind]
    Anywhere: ClassVar[SubstringMatchKind]
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...

class ParameterTransformOp:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class CapitalizeInitial(ParameterTransformOp):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class ExpandEscapeSequences(ParameterTransformOp):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class PossiblyQuoteWithArraysExpanded(ParameterTransformOp):
        __match_args__ = ("separate_words",)
        def __new__(cls, separate_words: bool) -> Self: ...
        @property
        def separate_words(self) -> bool: ...

    @final
    class PromptExpand(ParameterTransformOp):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class Quoted(ParameterTransformOp):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class ToAssignmentLogic(ParameterTransformOp):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class ToAttributeFlags(ParameterTransformOp):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class ToLowerCase(ParameterTransformOp):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class ToUpperCase(ParameterTransformOp):
        __match_args__ = ()
        def __new__(cls) -> Self: ...
