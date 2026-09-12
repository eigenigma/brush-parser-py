from typing import ClassVar, Self, final

from ._ast_compound import CompoundCommand, FunctionDefinition, SubshellCommand
from ._ast_extended_test import ExtendedTestExprCommand
from ._ast_redirects import IoRedirect, RedirectList
from ._source import SourceSpan

class Command:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Simple(Command):
        __match_args__ = ("command",)
        def __new__(cls, command: SimpleCommand) -> Self: ...
        @property
        def command(self) -> SimpleCommand: ...

    @final
    class Compound(Command):
        __match_args__ = ("command", "redirects")
        def __new__(
            cls, command: CompoundCommand, redirects: RedirectList | None
        ) -> Self: ...
        @property
        def command(self) -> CompoundCommand: ...
        @property
        def redirects(self) -> RedirectList | None: ...

    @final
    class Function(Command):
        __match_args__ = ("definition",)
        def __new__(cls, definition: FunctionDefinition) -> Self: ...
        @property
        def definition(self) -> FunctionDefinition: ...

    @final
    class ExtendedTest(Command):
        __match_args__ = ("command", "redirects")
        def __new__(
            cls, command: ExtendedTestExprCommand, redirects: RedirectList | None
        ) -> Self: ...
        @property
        def command(self) -> ExtendedTestExprCommand: ...
        @property
        def redirects(self) -> RedirectList | None: ...

@final
class SimpleCommand:
    __match_args__ = ("prefix", "word_or_name", "suffix")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls,
        prefix: CommandPrefix | None,
        word_or_name: Word | None,
        suffix: CommandSuffix | None,
    ) -> Self: ...
    @property
    def prefix(self) -> CommandPrefix | None: ...
    @property
    def word_or_name(self) -> Word | None: ...
    @property
    def suffix(self) -> CommandSuffix | None: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class CommandPrefix:
    __match_args__ = ("items",)
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, items: tuple[CommandPrefixOrSuffixItem, ...]) -> Self: ...
    @property
    def items(self) -> tuple[CommandPrefixOrSuffixItem, ...]: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class CommandSuffix:
    __match_args__ = ("items",)
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, items: tuple[CommandPrefixOrSuffixItem, ...]) -> Self: ...
    @property
    def items(self) -> tuple[CommandPrefixOrSuffixItem, ...]: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class ProcessSubstitutionKind:
    Read: ClassVar[ProcessSubstitutionKind]
    Write: ClassVar[ProcessSubstitutionKind]
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...

class CommandPrefixOrSuffixItem:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class IoRedirect(CommandPrefixOrSuffixItem):
        __match_args__ = ("redirect",)
        def __new__(cls, redirect: IoRedirect) -> Self: ...
        @property
        def redirect(self) -> IoRedirect: ...

    @final
    class Word(CommandPrefixOrSuffixItem):
        __match_args__ = ("word",)
        def __new__(cls, word: Word) -> Self: ...
        @property
        def word(self) -> Word: ...

    @final
    class AssignmentWord(CommandPrefixOrSuffixItem):
        __match_args__ = ("assignment", "word")
        def __new__(cls, assignment: Assignment, word: Word) -> Self: ...
        @property
        def assignment(self) -> Assignment: ...
        @property
        def word(self) -> Word: ...

    @final
    class ProcessSubstitution(CommandPrefixOrSuffixItem):
        __match_args__ = ("kind", "command")
        def __new__(
            cls, kind: ProcessSubstitutionKind, command: SubshellCommand
        ) -> Self: ...
        @property
        def kind(self) -> ProcessSubstitutionKind: ...
        @property
        def command(self) -> SubshellCommand: ...

@final
class Assignment:
    __match_args__ = ("name", "value", "append", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls, name: AssignmentName, value: AssignmentValue, append: bool, loc: SourceSpan
    ) -> Self: ...
    @property
    def name(self) -> AssignmentName: ...
    @property
    def value(self) -> AssignmentValue: ...
    @property
    def append(self) -> bool: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

class AssignmentName:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class VariableName(AssignmentName):
        __match_args__ = ("name",)
        def __new__(cls, name: str) -> Self: ...
        @property
        def name(self) -> str: ...

    @final
    class ArrayElementName(AssignmentName):
        __match_args__ = ("name", "index")
        def __new__(cls, name: str, index: str) -> Self: ...
        @property
        def name(self) -> str: ...
        @property
        def index(self) -> str: ...

class AssignmentValue:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Scalar(AssignmentValue):
        __match_args__ = ("word",)
        def __new__(cls, word: Word) -> Self: ...
        @property
        def word(self) -> Word: ...

    @final
    class Array(AssignmentValue):
        __match_args__ = ("elements",)
        def __new__(cls, elements: tuple[tuple[Word | None, Word], ...]) -> Self: ...
        @property
        def elements(self) -> tuple[tuple[Word | None, Word], ...]: ...

@final
class Word:
    __match_args__ = ("value", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, value: str, loc: SourceSpan | None) -> Self: ...
    @property
    def value(self) -> str: ...
    @property
    def loc(self) -> SourceSpan | None: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class UnexpandedArithmeticExpr:
    __match_args__ = ("value",)
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, value: str) -> Self: ...
    @property
    def value(self) -> str: ...
    def __eq__(self, other: object, /) -> bool: ...
