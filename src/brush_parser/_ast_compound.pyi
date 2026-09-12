from typing import ClassVar, Self, final

from ._ast_clauses import (
    ArithmeticForClauseCommand,
    CaseClauseCommand,
    ForClauseCommand,
    IfClauseCommand,
    WhileOrUntilClauseCommand,
)
from ._ast_commands import Command, UnexpandedArithmeticExpr, Word
from ._ast_lists import CompoundList
from ._ast_redirects import RedirectList
from ._source import SourceSpan

class CompoundCommand:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Arithmetic(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: ArithmeticCommand) -> Self: ...
        @property
        def command(self) -> ArithmeticCommand: ...

    @final
    class ArithmeticForClause(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: ArithmeticForClauseCommand) -> Self: ...
        @property
        def command(self) -> ArithmeticForClauseCommand: ...

    @final
    class BraceGroup(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: BraceGroupCommand) -> Self: ...
        @property
        def command(self) -> BraceGroupCommand: ...

    @final
    class Subshell(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: SubshellCommand) -> Self: ...
        @property
        def command(self) -> SubshellCommand: ...

    @final
    class ForClause(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: ForClauseCommand) -> Self: ...
        @property
        def command(self) -> ForClauseCommand: ...

    @final
    class CaseClause(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: CaseClauseCommand) -> Self: ...
        @property
        def command(self) -> CaseClauseCommand: ...

    @final
    class IfClause(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: IfClauseCommand) -> Self: ...
        @property
        def command(self) -> IfClauseCommand: ...

    @final
    class WhileClause(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: WhileOrUntilClauseCommand) -> Self: ...
        @property
        def command(self) -> WhileOrUntilClauseCommand: ...

    @final
    class UntilClause(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: WhileOrUntilClauseCommand) -> Self: ...
        @property
        def command(self) -> WhileOrUntilClauseCommand: ...

    @final
    class Coprocess(CompoundCommand):
        __match_args__ = ("command",)
        def __new__(cls, command: CoprocessCommand) -> Self: ...
        @property
        def command(self) -> CoprocessCommand: ...

@final
class ArithmeticCommand:
    __match_args__ = ("expr", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, expr: UnexpandedArithmeticExpr, loc: SourceSpan) -> Self: ...
    @property
    def expr(self) -> UnexpandedArithmeticExpr: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class SubshellCommand:
    __match_args__ = ("list", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, list: CompoundList, loc: SourceSpan) -> Self: ...  # noqa: A002
    @property
    def list(self) -> CompoundList: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class BraceGroupCommand:
    __match_args__ = ("list", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, list: CompoundList, loc: SourceSpan) -> Self: ...  # noqa: A002
    @property
    def list(self) -> CompoundList: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class DoGroupCommand:
    __match_args__ = ("list", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, list: CompoundList, loc: SourceSpan) -> Self: ...  # noqa: A002
    @property
    def list(self) -> CompoundList: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class CoprocessCommand:
    __match_args__ = ("name", "body", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, name: Word | None, body: Command, loc: SourceSpan) -> Self: ...
    @property
    def name(self) -> Word | None: ...
    @property
    def body(self) -> Command: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class FunctionDefinition:
    __match_args__ = ("fname", "body")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, fname: Word, body: FunctionBody) -> Self: ...
    @property
    def fname(self) -> Word: ...
    @property
    def body(self) -> FunctionBody: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class FunctionBody:
    __match_args__ = ("command", "redirects")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls, command: CompoundCommand, redirects: RedirectList | None
    ) -> Self: ...
    @property
    def command(self) -> CompoundCommand: ...
    @property
    def redirects(self) -> RedirectList | None: ...
    def __eq__(self, other: object, /) -> bool: ...
