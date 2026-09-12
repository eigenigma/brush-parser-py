from ._source import SourcePosition

class ParseError(ValueError):
    position: SourcePosition | None

class WordParseError(ValueError):
    input: str
