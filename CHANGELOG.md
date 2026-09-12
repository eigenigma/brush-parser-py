# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with the
0.x caveat below.

Version policy: this package mirrors one exact `brush-parser` release
(`BRUSH_PARSER_VERSION`). An upstream release that changes the AST shape
becomes a minor bump here while the package is 0.x; a bump that only changes
the binding keeps the upstream pin and is a patch release.

## [0.1.0] - 2026-09-10

### Added

- `parse_program`, `parse_word`, `parse_heredoc`, `parse_parameter` and
  `parse_brace_expansions` over `brush-parser` 0.4.0, each taking the five
  upstream `ParserOptions` booleans as keyword-only arguments.
- One frozen, structurally comparable class per upstream AST and word type;
  enum variants are nested `@final` subclasses usable in `match`. Nodes,
  enum members and errors support `pickle` and `copy`.
- `ParseError` with `.position` and `WordParseError` with `.input`, both
  `ValueError` subclasses carrying the upstream `Display` message.
- Hand-written type stubs checked by `mypy.stubtest`.
- `abi3-py312` wheels for macOS arm64 and manylinux x86_64 / aarch64, plus an
  sdist.

[0.1.0]: https://github.com/eigenigma/brush-parser-py/releases/tag/v0.1.0
