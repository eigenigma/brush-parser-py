# brush-parser-py

Python binding for [brush-parser](https://crates.io/crates/brush-parser), the
POSIX/bash parser behind the `brush` shell. The binding mirrors the crate's
AST one type per class and adds nothing of its own.

Import name: `brush_parser`. Wrapped crate version:
`brush_parser.BRUSH_PARSER_VERSION`.

## Install

```sh
uv add brush-parser-py
```

Prebuilt wheels cover CPython 3.12 and later on common platforms; anything
else builds from the sdist with a Rust toolchain.

```python
import brush_parser

program = brush_parser.parse_program("echo hi | wc -l")
match program.complete_commands[0].items[0].list.first.seq[0]:
    case brush_parser.Command.Simple(command=simple):
        print(simple.word_or_name)
```

## API

- `parse_program(text, **options)` returns a `Program`.
- `parse_word(word, **options)` and `parse_heredoc(word, **options)` return a
  tuple of `WordPieceWithSource`.
- `parse_parameter(word, **options)` returns a `Parameter`.
- `parse_brace_expansions(word, **options)` returns a tuple of
  `BraceExpressionOrText`, or `None` when there is nothing to expand.

`options` are the upstream `ParserOptions` booleans as keyword-only arguments
with upstream defaults; the type stubs list them.

Every class is frozen, compares structurally with `==`, and is unhashable.
Enum variants are nested classes usable in `match`.

Positions are in characters, not bytes. `SourceSpan` on AST nodes indexes the
text given to `parse_program`; `WordPieceWithSource.start` / `.end` index the
string given to the word function. Ranges are end-exclusive.

## Errors

`ParseError` (with `.position`) and `WordParseError` (with `.input`) are
`ValueError` subclasses. There is no time or recursion guard; callers that
need a bound run the parse in a subprocess.

## Versioning

Each release pins one exact `brush-parser` version. See `CHANGELOG.md` for
the version policy and release notes.

## Development

```sh
uv sync
cargo test
cargo clippy --all-targets -- -D warnings
uv run ruff check .
uv run ty check .
uv run pytest
```
