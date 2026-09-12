"""Consumer code `ty` must accept: variant fields only after narrowing."""

import brush_parser as bp


def command_kind(command: bp.Command) -> str:
    match command:
        case bp.Command.Simple(command=simple):
            name = simple.word_or_name
            return "simple:" + (name.value if name is not None else "")
        case bp.Command.Compound(command=compound, redirects=redirects):
            return "compound:" + compound_kind(compound) + str(redirects is not None)
        case bp.Command.Function(definition=definition):
            return "function:" + definition.fname.value
        case bp.Command.ExtendedTest(command=test):
            return "test:" + type(test.expr).__name__
    return "unreachable"


def compound_kind(compound: bp.CompoundCommand) -> str:
    match compound:
        case bp.CompoundCommand.Subshell(command=subshell):
            return f"subshell@{subshell.loc.start.index}"
        case bp.CompoundCommand.IfClause(command=clause):
            return f"if:{len(clause.elses or ())}"
        case (
            bp.CompoundCommand.WhileClause(command=loop)
            | bp.CompoundCommand.UntilClause(command=loop)
        ):
            return f"loop@{loop.loc.start.index}"
        case _:
            return type(compound).__name__


def piece_text(piece: bp.WordPiece) -> str:
    match piece:
        case bp.WordPiece.Text(text=text) | bp.WordPiece.SingleQuotedText(text=text):
            return text
        case bp.WordPiece.DoubleQuotedSequence(pieces=pieces):
            return "".join(piece_text(inner.piece) for inner in pieces)
        case bp.WordPiece.ParameterExpansion(expr=expr):
            return parameter_name(expr)
        case _:
            return ""


def parameter_name(expr: bp.ParameterExpr) -> str:
    match expr:
        case bp.ParameterExpr.Parameter(parameter=bp.Parameter.Named(name=name)):
            return name
        case bp.ParameterExpr.UseDefaultValues(default_value=default):
            return default or ""
        case bp.ParameterExpr.VariableNames(prefix=prefix):
            return prefix
        case _:
            return ""


def first_command(text: str) -> bp.Command:
    return bp.parse_program(text).complete_commands[0].items[0].list.first.seq[0]


def test_command_kinds():
    assert command_kind(first_command("echo hi")) == "simple:echo"
    assert command_kind(first_command("( a ) >f")) == "compound:subshell@0True"
    assert command_kind(first_command("f() { a; }")) == "function:f"
    assert command_kind(first_command("[[ -n x ]]")) == "test:UnaryTest"


def test_compound_kinds():
    assert command_kind(first_command("if a; then b; else c; fi")) == (
        "compound:if:1False"
    )
    assert command_kind(first_command("until a; do b; done")) == (
        "compound:loop@0False"
    )
    assert command_kind(first_command("{ a; }")) == "compound:BraceGroupFalse"


def test_piece_text():
    pieces = bp.parse_word("a'b'\"c${x:-d}\"$y")
    assert "".join(piece_text(item.piece) for item in pieces) == "abcdy"


def test_error_attributes_are_typed():
    try:
        bp.parse_program("echo )")
    except bp.ParseError as error:
        position: bp.SourcePosition | None = error.position
        assert position is not None
        assert position.column == 6
    try:
        bp.parse_parameter("${")
    except bp.WordParseError as error:
        text: str = error.input
        assert text == "${"
