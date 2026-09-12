from typing import ClassVar, Self, final

from ._ast_commands import ProcessSubstitutionKind, Word
from ._ast_compound import SubshellCommand

@final
class RedirectList:
    __match_args__ = ("items",)
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(cls, items: tuple[IoRedirect, ...]) -> Self: ...
    @property
    def items(self) -> tuple[IoRedirect, ...]: ...
    def __eq__(self, other: object, /) -> bool: ...

class IoRedirect:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class File(IoRedirect):
        __match_args__ = ("fd", "kind", "target")
        def __new__(
            cls, fd: int | None, kind: IoFileRedirectKind, target: IoFileRedirectTarget
        ) -> Self: ...
        @property
        def fd(self) -> int | None: ...
        @property
        def kind(self) -> IoFileRedirectKind: ...
        @property
        def target(self) -> IoFileRedirectTarget: ...

    @final
    class HereDocument(IoRedirect):
        __match_args__ = ("fd", "document")
        def __new__(cls, fd: int | None, document: IoHereDocument) -> Self: ...
        @property
        def fd(self) -> int | None: ...
        @property
        def document(self) -> IoHereDocument: ...

    @final
    class HereString(IoRedirect):
        __match_args__ = ("fd", "word")
        def __new__(cls, fd: int | None, word: Word) -> Self: ...
        @property
        def fd(self) -> int | None: ...
        @property
        def word(self) -> Word: ...

    @final
    class OutputAndError(IoRedirect):
        __match_args__ = ("target", "append")
        def __new__(cls, target: Word, append: bool) -> Self: ...
        @property
        def target(self) -> Word: ...
        @property
        def append(self) -> bool: ...

@final
class IoFileRedirectKind:
    Read: ClassVar[IoFileRedirectKind]
    Write: ClassVar[IoFileRedirectKind]
    Append: ClassVar[IoFileRedirectKind]
    ReadAndWrite: ClassVar[IoFileRedirectKind]
    Clobber: ClassVar[IoFileRedirectKind]
    DuplicateInput: ClassVar[IoFileRedirectKind]
    DuplicateOutput: ClassVar[IoFileRedirectKind]
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...

class IoFileRedirectTarget:
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __eq__(self, other: object, /) -> bool: ...
    @final
    class Filename(IoFileRedirectTarget):
        __match_args__ = ("word",)
        def __new__(cls, word: Word) -> Self: ...
        @property
        def word(self) -> Word: ...

    @final
    class Fd(IoFileRedirectTarget):
        __match_args__ = ("fd",)
        def __new__(cls, fd: int) -> Self: ...
        @property
        def fd(self) -> int: ...

    @final
    class ProcessSubstitution(IoFileRedirectTarget):
        __match_args__ = ("kind", "command")
        def __new__(
            cls, kind: ProcessSubstitutionKind, command: SubshellCommand
        ) -> Self: ...
        @property
        def kind(self) -> ProcessSubstitutionKind: ...
        @property
        def command(self) -> SubshellCommand: ...

    @final
    class Duplicate(IoFileRedirectTarget):
        __match_args__ = ("word",)
        def __new__(cls, word: Word) -> Self: ...
        @property
        def word(self) -> Word: ...

@final
class IoHereDocument:
    __match_args__ = ("remove_tabs", "requires_expansion", "here_end", "doc")
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __new__(
        cls, remove_tabs: bool, requires_expansion: bool, here_end: Word, doc: Word
    ) -> Self: ...
    @property
    def remove_tabs(self) -> bool: ...
    @property
    def requires_expansion(self) -> bool: ...
    @property
    def here_end(self) -> Word: ...
    @property
    def doc(self) -> Word: ...
    def __eq__(self, other: object, /) -> bool: ...
