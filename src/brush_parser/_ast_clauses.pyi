from typing import ClassVar, Self, final

from ._ast_commands import UnexpandedArithmeticExpr, Word
from ._ast_compound import DoGroupCommand
from ._ast_lists import CompoundList
from ._source import SourceSpan

@final
class ForClauseCommand:
    __match_args__ = ("variable_name", "values", "body", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls,
        variable_name: str,
        values: tuple[Word, ...] | None,
        body: DoGroupCommand,
        loc: SourceSpan,
    ) -> Self: ...
    @property
    def variable_name(self) -> str: ...
    @property
    def values(self) -> tuple[Word, ...] | None: ...
    @property
    def body(self) -> DoGroupCommand: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class ArithmeticForClauseCommand:
    __match_args__ = ("initializer", "condition", "updater", "body", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls,
        initializer: UnexpandedArithmeticExpr | None,
        condition: UnexpandedArithmeticExpr | None,
        updater: UnexpandedArithmeticExpr | None,
        body: DoGroupCommand,
        loc: SourceSpan,
    ) -> Self: ...
    @property
    def initializer(self) -> UnexpandedArithmeticExpr | None: ...
    @property
    def condition(self) -> UnexpandedArithmeticExpr | None: ...
    @property
    def updater(self) -> UnexpandedArithmeticExpr | None: ...
    @property
    def body(self) -> DoGroupCommand: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class CaseClauseCommand:
    __match_args__ = ("value", "cases", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls, value: Word, cases: tuple[CaseItem, ...], loc: SourceSpan
    ) -> Self: ...
    @property
    def value(self) -> Word: ...
    @property
    def cases(self) -> tuple[CaseItem, ...]: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class CaseItem:
    __match_args__ = ("patterns", "cmd", "post_action", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls,
        patterns: tuple[Word, ...],
        cmd: CompoundList | None,
        post_action: CaseItemPostAction,
        loc: SourceSpan | None,
    ) -> Self: ...
    @property
    def patterns(self) -> tuple[Word, ...]: ...
    @property
    def cmd(self) -> CompoundList | None: ...
    @property
    def post_action(self) -> CaseItemPostAction: ...
    @property
    def loc(self) -> SourceSpan | None: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class CaseItemPostAction:
    ExitCase: ClassVar[CaseItemPostAction]
    UnconditionallyExecuteNextCaseItem: ClassVar[CaseItemPostAction]
    ContinueEvaluatingCases: ClassVar[CaseItemPostAction]
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...

@final
class IfClauseCommand:
    __match_args__ = ("condition", "then", "elses", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls,
        condition: CompoundList,
        then: CompoundList,
        elses: tuple[ElseClause, ...] | None,
        loc: SourceSpan,
    ) -> Self: ...
    @property
    def condition(self) -> CompoundList: ...
    @property
    def then(self) -> CompoundList: ...
    @property
    def elses(self) -> tuple[ElseClause, ...] | None: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class ElseClause:
    __match_args__ = ("condition", "body")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, condition: CompoundList | None, body: CompoundList) -> Self: ...
    @property
    def condition(self) -> CompoundList | None: ...
    @property
    def body(self) -> CompoundList: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class WhileOrUntilClauseCommand:
    __match_args__ = ("condition", "body", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls, condition: CompoundList, body: DoGroupCommand, loc: SourceSpan
    ) -> Self: ...
    @property
    def condition(self) -> CompoundList: ...
    @property
    def body(self) -> DoGroupCommand: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...
