from typing import ClassVar, Self, final

from ._ast_commands import Command
from ._source import SourceSpan

@final
class Program:
    __match_args__ = ("complete_commands",)
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, complete_commands: tuple[CompoundList, ...]) -> Self: ...
    @property
    def complete_commands(self) -> tuple[CompoundList, ...]: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class CompoundList:
    __match_args__ = ("items",)
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, items: tuple[CompoundListItem, ...]) -> Self: ...
    @property
    def items(self) -> tuple[CompoundListItem, ...]: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class CompoundListItem:
    __match_args__ = ("list", "separator")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, list: AndOrList, separator: SeparatorOperator) -> Self: ...  # noqa: A002
    @property
    def list(self) -> AndOrList: ...
    @property
    def separator(self) -> SeparatorOperator: ...
    def __eq__(self, other: object, /) -> bool: ...

@final
class SeparatorOperator:
    Async: ClassVar[SeparatorOperator]
    Sequence: ClassVar[SeparatorOperator]
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...

@final
class AndOrList:
    __match_args__ = ("first", "additional")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, first: Pipeline, additional: tuple[AndOr, ...]) -> Self: ...
    @property
    def first(self) -> Pipeline: ...
    @property
    def additional(self) -> tuple[AndOr, ...]: ...
    def __eq__(self, other: object, /) -> bool: ...

class AndOr:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class And(AndOr):
        __match_args__ = ("pipeline",)
        def __new__(cls, pipeline: Pipeline) -> Self: ...
        @property
        def pipeline(self) -> Pipeline: ...

    @final
    class Or(AndOr):
        __match_args__ = ("pipeline",)
        def __new__(cls, pipeline: Pipeline) -> Self: ...
        @property
        def pipeline(self) -> Pipeline: ...

class PipelineTimed:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Timed(PipelineTimed):
        __match_args__ = ("loc",)
        def __new__(cls, loc: SourceSpan) -> Self: ...
        @property
        def loc(self) -> SourceSpan: ...

    @final
    class TimedWithPosixOutput(PipelineTimed):
        __match_args__ = ("loc",)
        def __new__(cls, loc: SourceSpan) -> Self: ...
        @property
        def loc(self) -> SourceSpan: ...

@final
class Pipeline:
    __match_args__ = ("timed", "bang", "seq")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls, timed: PipelineTimed | None, bang: bool, seq: tuple[Command, ...]
    ) -> Self: ...
    @property
    def timed(self) -> PipelineTimed | None: ...
    @property
    def bang(self) -> bool: ...
    @property
    def seq(self) -> tuple[Command, ...]: ...
    def __eq__(self, other: object, /) -> bool: ...
