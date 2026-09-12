from typing import ClassVar, Self, final

from ._ast_commands import UnexpandedArithmeticExpr
from ._word_expressions import ParameterExpr

@final
class WordPieceWithSource:
    __match_args__ = ("piece", "start", "end")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, piece: WordPiece, start: int, end: int) -> Self: ...
    @property
    def piece(self) -> WordPiece: ...
    @property
    def start(self) -> int: ...
    @property
    def end(self) -> int: ...
    def __eq__(self, other: object, /) -> bool: ...

class WordPiece:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Text(WordPiece):
        __match_args__ = ("text",)
        def __new__(cls, text: str) -> Self: ...
        @property
        def text(self) -> str: ...

    @final
    class SingleQuotedText(WordPiece):
        __match_args__ = ("text",)
        def __new__(cls, text: str) -> Self: ...
        @property
        def text(self) -> str: ...

    @final
    class AnsiCQuotedText(WordPiece):
        __match_args__ = ("text",)
        def __new__(cls, text: str) -> Self: ...
        @property
        def text(self) -> str: ...

    @final
    class DoubleQuotedSequence(WordPiece):
        __match_args__ = ("pieces",)
        def __new__(cls, pieces: tuple[WordPieceWithSource, ...]) -> Self: ...
        @property
        def pieces(self) -> tuple[WordPieceWithSource, ...]: ...

    @final
    class GettextDoubleQuotedSequence(WordPiece):
        __match_args__ = ("pieces",)
        def __new__(cls, pieces: tuple[WordPieceWithSource, ...]) -> Self: ...
        @property
        def pieces(self) -> tuple[WordPieceWithSource, ...]: ...

    @final
    class TildeExpansion(WordPiece):
        __match_args__ = ("expr",)
        def __new__(cls, expr: TildeExpr) -> Self: ...
        @property
        def expr(self) -> TildeExpr: ...

    @final
    class ParameterExpansion(WordPiece):
        __match_args__ = ("expr",)
        def __new__(cls, expr: ParameterExpr) -> Self: ...
        @property
        def expr(self) -> ParameterExpr: ...

    @final
    class CommandSubstitution(WordPiece):
        __match_args__ = ("command",)
        def __new__(cls, command: str) -> Self: ...
        @property
        def command(self) -> str: ...

    @final
    class BackquotedCommandSubstitution(WordPiece):
        __match_args__ = ("command",)
        def __new__(cls, command: str) -> Self: ...
        @property
        def command(self) -> str: ...

    @final
    class EscapeSequence(WordPiece):
        __match_args__ = ("text",)
        def __new__(cls, text: str) -> Self: ...
        @property
        def text(self) -> str: ...

    @final
    class ArithmeticExpression(WordPiece):
        __match_args__ = ("expr",)
        def __new__(cls, expr: UnexpandedArithmeticExpr) -> Self: ...
        @property
        def expr(self) -> UnexpandedArithmeticExpr: ...

class TildeExpr:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Home(TildeExpr):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class UserHome(TildeExpr):
        __match_args__ = ("user",)
        def __new__(cls, user: str) -> Self: ...
        @property
        def user(self) -> str: ...

    @final
    class WorkingDir(TildeExpr):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class OldWorkingDir(TildeExpr):
        __match_args__ = ()
        def __new__(cls) -> Self: ...

    @final
    class NthDirFromTopOfDirStack(TildeExpr):
        __match_args__ = ("n", "plus_used")
        def __new__(cls, n: int, plus_used: bool) -> Self: ...
        @property
        def n(self) -> int: ...
        @property
        def plus_used(self) -> bool: ...

    @final
    class NthDirFromBottomOfDirStack(TildeExpr):
        __match_args__ = ("n",)
        def __new__(cls, n: int) -> Self: ...
        @property
        def n(self) -> int: ...

class BraceExpressionOrText:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Expr(BraceExpressionOrText):
        __match_args__ = ("members",)
        def __new__(cls, members: tuple[BraceExpressionMember, ...]) -> Self: ...
        @property
        def members(self) -> tuple[BraceExpressionMember, ...]: ...

    @final
    class Text(BraceExpressionOrText):
        __match_args__ = ("text",)
        def __new__(cls, text: str) -> Self: ...
        @property
        def text(self) -> str: ...

class BraceExpressionMember:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class NumberSequence(BraceExpressionMember):
        __match_args__ = ("start", "end", "increment")
        def __new__(cls, start: int, end: int, increment: int) -> Self: ...
        @property
        def start(self) -> int: ...
        @property
        def end(self) -> int: ...
        @property
        def increment(self) -> int: ...

    @final
    class CharSequence(BraceExpressionMember):
        __match_args__ = ("start", "end", "increment")
        def __new__(cls, start: str, end: str, increment: int) -> Self: ...
        @property
        def start(self) -> str: ...
        @property
        def end(self) -> str: ...
        @property
        def increment(self) -> int: ...

    @final
    class Child(BraceExpressionMember):
        __match_args__ = ("items",)
        def __new__(cls, items: tuple[BraceExpressionOrText, ...]) -> Self: ...
        @property
        def items(self) -> tuple[BraceExpressionOrText, ...]: ...
