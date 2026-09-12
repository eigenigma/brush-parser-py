"""Shared builders and narrowing helpers for hand-written expected trees."""

from brush_parser import _core as core


def span(start: int, end: int) -> core.SourceSpan:
    """Span on line 1 from char index `start` to `end` (exclusive)."""
    return core.SourceSpan(
        core.SourcePosition(start, 1, start + 1),
        core.SourcePosition(end, 1, end + 1),
    )


def word(value: str, start: int) -> core.Word:
    """Word `value` located at char index `start` on line 1."""
    return core.Word(value, span(start, start + len(value)))


def simple(name: core.Word, *args: core.CommandPrefixOrSuffixItem) -> core.Command:
    """`Command.Simple` with no prefix and the given suffix items."""
    suffix = core.CommandSuffix(args) if args else None
    return core.Command.Simple(core.SimpleCommand(None, name, suffix))


def pipeline(*commands: core.Command) -> core.Pipeline:
    return core.Pipeline(None, bang=False, seq=commands)


def list_item(
    first: core.Pipeline,
    *additional: core.AndOr,
    separator: core.SeparatorOperator = core.SeparatorOperator.Sequence,
) -> core.CompoundListItem:
    return core.CompoundListItem(core.AndOrList(first, additional), separator)


def program(*items: core.CompoundListItem) -> core.Program:
    """Program of one complete command holding `items`."""
    return core.Program((core.CompoundList(items),))


def narrow[T](node: object, cls: type[T]) -> T:
    assert isinstance(node, cls), f"expected {cls.__qualname__}, got {node!r}"
    return node


def first_command(text: str, **options: bool) -> core.Command:
    """The first command of the first pipeline of `text`."""
    return (
        core.parse_program(text, **options)
        .complete_commands[0]
        .items[0]
        .list.first.seq[0]
    )


def compound[T](text: str, variant: type[T]) -> T:
    """The payload of the first command, a compound of class `variant`."""
    command = narrow(first_command(text), core.Command.Compound)
    return narrow(command.command, variant)


def simple_command(text: str) -> core.SimpleCommand:
    return narrow(first_command(text), core.Command.Simple).command


def prefix_items(text: str) -> tuple[core.CommandPrefixOrSuffixItem, ...]:
    prefix = simple_command(text).prefix
    assert prefix is not None
    return prefix.items


def suffix_items(text: str) -> tuple[core.CommandPrefixOrSuffixItem, ...]:
    suffix = simple_command(text).suffix
    assert suffix is not None
    return suffix.items
