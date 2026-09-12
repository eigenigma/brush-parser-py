from typing import ClassVar, Self, final

from ._ast_commands import Word
from ._source import SourceSpan

@final
class ExtendedTestExprCommand:
    __match_args__ = ("expr", "loc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, expr: ExtendedTestExpr, loc: SourceSpan) -> Self: ...
    @property
    def expr(self) -> ExtendedTestExpr: ...
    @property
    def loc(self) -> SourceSpan: ...
    def __eq__(self, other: object, /) -> bool: ...

class ExtendedTestExpr:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class And(ExtendedTestExpr):
        __match_args__ = ("left", "right")
        def __new__(cls, left: ExtendedTestExpr, right: ExtendedTestExpr) -> Self: ...
        @property
        def left(self) -> ExtendedTestExpr: ...
        @property
        def right(self) -> ExtendedTestExpr: ...

    @final
    class Or(ExtendedTestExpr):
        __match_args__ = ("left", "right")
        def __new__(cls, left: ExtendedTestExpr, right: ExtendedTestExpr) -> Self: ...
        @property
        def left(self) -> ExtendedTestExpr: ...
        @property
        def right(self) -> ExtendedTestExpr: ...

    @final
    class Not(ExtendedTestExpr):
        __match_args__ = ("expr",)
        def __new__(cls, expr: ExtendedTestExpr) -> Self: ...
        @property
        def expr(self) -> ExtendedTestExpr: ...

    @final
    class Parenthesized(ExtendedTestExpr):
        __match_args__ = ("expr",)
        def __new__(cls, expr: ExtendedTestExpr) -> Self: ...
        @property
        def expr(self) -> ExtendedTestExpr: ...

    @final
    class UnaryTest(ExtendedTestExpr):
        __match_args__ = ("predicate", "operand")
        def __new__(cls, predicate: UnaryPredicate, operand: Word) -> Self: ...
        @property
        def predicate(self) -> UnaryPredicate: ...
        @property
        def operand(self) -> Word: ...

    @final
    class BinaryTest(ExtendedTestExpr):
        __match_args__ = ("predicate", "left", "right")
        def __new__(
            cls, predicate: BinaryPredicate, left: Word, right: Word
        ) -> Self: ...
        @property
        def predicate(self) -> BinaryPredicate: ...
        @property
        def left(self) -> Word: ...
        @property
        def right(self) -> Word: ...

@final
class UnaryPredicate:
    FileExists: ClassVar[UnaryPredicate]
    FileExistsAndIsBlockSpecialFile: ClassVar[UnaryPredicate]
    FileExistsAndIsCharSpecialFile: ClassVar[UnaryPredicate]
    FileExistsAndIsDir: ClassVar[UnaryPredicate]
    FileExistsAndIsRegularFile: ClassVar[UnaryPredicate]
    FileExistsAndIsSetgid: ClassVar[UnaryPredicate]
    FileExistsAndIsSymlink: ClassVar[UnaryPredicate]
    FileExistsAndHasStickyBit: ClassVar[UnaryPredicate]
    FileExistsAndIsFifo: ClassVar[UnaryPredicate]
    FileExistsAndIsReadable: ClassVar[UnaryPredicate]
    FileExistsAndIsNotZeroLength: ClassVar[UnaryPredicate]
    FdIsOpenTerminal: ClassVar[UnaryPredicate]
    FileExistsAndIsSetuid: ClassVar[UnaryPredicate]
    FileExistsAndIsWritable: ClassVar[UnaryPredicate]
    FileExistsAndIsExecutable: ClassVar[UnaryPredicate]
    FileExistsAndOwnedByEffectiveGroupId: ClassVar[UnaryPredicate]
    FileExistsAndModifiedSinceLastRead: ClassVar[UnaryPredicate]
    FileExistsAndOwnedByEffectiveUserId: ClassVar[UnaryPredicate]
    FileExistsAndIsSocket: ClassVar[UnaryPredicate]
    ShellOptionEnabled: ClassVar[UnaryPredicate]
    ShellVariableIsSetAndAssigned: ClassVar[UnaryPredicate]
    ShellVariableIsSetAndNameRef: ClassVar[UnaryPredicate]
    StringHasZeroLength: ClassVar[UnaryPredicate]
    StringHasNonZeroLength: ClassVar[UnaryPredicate]
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...

@final
class BinaryPredicate:
    FilesReferToSameDeviceAndInodeNumbers: ClassVar[BinaryPredicate]
    LeftFileIsNewerOrExistsWhenRightDoesNot: ClassVar[BinaryPredicate]
    LeftFileIsOlderOrDoesNotExistWhenRightDoes: ClassVar[BinaryPredicate]
    StringExactlyMatchesPattern: ClassVar[BinaryPredicate]
    StringDoesNotExactlyMatchPattern: ClassVar[BinaryPredicate]
    StringMatchesRegex: ClassVar[BinaryPredicate]
    StringExactlyMatchesString: ClassVar[BinaryPredicate]
    StringDoesNotExactlyMatchString: ClassVar[BinaryPredicate]
    StringContainsSubstring: ClassVar[BinaryPredicate]
    LeftSortsBeforeRight: ClassVar[BinaryPredicate]
    LeftSortsAfterRight: ClassVar[BinaryPredicate]
    ArithmeticEqualTo: ClassVar[BinaryPredicate]
    ArithmeticNotEqualTo: ClassVar[BinaryPredicate]
    ArithmeticLessThan: ClassVar[BinaryPredicate]
    ArithmeticLessThanOrEqualTo: ClassVar[BinaryPredicate]
    ArithmeticGreaterThan: ClassVar[BinaryPredicate]
    ArithmeticGreaterThanOrEqualTo: ClassVar[BinaryPredicate]
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
