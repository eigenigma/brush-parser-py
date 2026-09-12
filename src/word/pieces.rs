use brush_parser::word as upstream;
use pyo3::prelude::*;

use crate::ast::words::UnexpandedArithmeticExpr;
use crate::value::{FromRust, Seq, enum_node, node_enum, node_struct};
use crate::word::expressions::ParameterExpr;

node_struct! {
    /// `start` and `end` are char offsets into the whole string handed to the
    /// word parser, `end` exclusive, for nested pieces too.
    WordPieceWithSource { piece: Py<WordPiece>, start: usize, end: usize }
}

node_enum! {
    WordPiece {
        /// Unquoted and unescaped.
        Text {
            text: String
        },
        /// `'...'`, quotes excluded.
        SingleQuotedText {
            text: String
        },
        /// `$'...'`, quotes excluded.
        AnsiCQuotedText {
            text: String
        },
        /// `"..."`, quotes excluded.
        DoubleQuotedSequence {
            pieces: Seq<WordPieceWithSource>
        },
        /// `$"..."`, quotes excluded.
        GettextDoubleQuotedSequence {
            pieces: Seq<WordPieceWithSource>
        },
        TildeExpansion {
            expr: Py<TildeExpr>
        },
        ParameterExpansion {
            expr: Py<ParameterExpr>
        },
        /// `$(...)`, holding the command text unparsed.
        CommandSubstitution {
            command: String
        },
        /// `` `...` ``, holding the command text unparsed.
        BackquotedCommandSubstitution {
            command: String
        },
        EscapeSequence {
            text: String
        },
        /// `$((...))`.
        ArithmeticExpression {
            expr: Py<UnexpandedArithmeticExpr>
        },
    }
}

node_enum! {
    TildeExpr {
        /// `~`
        Home {},
        /// `~user`
        UserHome {
            user: String
        },
        /// `~+`
        WorkingDir {},
        /// `~-`
        OldWorkingDir {},
        /// `~+N` or `~N`.
        NthDirFromTopOfDirStack {
            /// 0-based from the top of the directory stack.
            n: usize,
            plus_used: bool
        },
        /// `~-N`.
        NthDirFromBottomOfDirStack {
            /// 0-based from the bottom of the directory stack.
            n: usize
        },
    }
}

/// Byte-index to char-index table for one word, built once per parse so every
/// piece resolves its offsets in constant time.
struct CharOffsets {
    /// `None` when the word is ASCII and byte indices are char indices.
    by_byte: Option<Vec<usize>>,
}

impl CharOffsets {
    fn new(word: &str) -> Self {
        if word.is_ascii() {
            return Self { by_byte: None };
        }
        let mut by_byte = vec![0; word.len() + 1];
        let mut chars = 0;
        for (byte, ch) in word.char_indices() {
            by_byte[byte] = chars;
            by_byte[byte + 1..byte + ch.len_utf8()].fill(chars + 1);
            chars += 1;
        }
        by_byte[word.len()] = chars;
        Self {
            by_byte: Some(by_byte),
        }
    }

    /// Char index of the char starting at `byte_index`; a byte inside a
    /// multi-byte char maps to the following char, and the end of the word to
    /// the char count.
    fn get(&self, byte_index: usize) -> usize {
        match &self.by_byte {
            None => byte_index,
            Some(by_byte) => by_byte[byte_index],
        }
    }
}

/// Translates the upstream byte offsets into char offsets of `word`.
pub fn pieces_from_rust(
    py: Python<'_>,
    word: &str,
    pieces: &[upstream::WordPieceWithSource],
) -> PyResult<Seq<WordPieceWithSource>> {
    pieces_with_offsets(py, &CharOffsets::new(word), pieces)
}

fn pieces_with_offsets(
    py: Python<'_>,
    offsets: &CharOffsets,
    pieces: &[upstream::WordPieceWithSource],
) -> PyResult<Seq<WordPieceWithSource>> {
    let items = pieces
        .iter()
        .map(|piece| piece_with_source(py, offsets, piece))
        .collect::<PyResult<Vec<_>>>()?;
    Seq::from_items(py, items)
}

fn piece_with_source(
    py: Python<'_>,
    offsets: &CharOffsets,
    value: &upstream::WordPieceWithSource,
) -> PyResult<Py<WordPieceWithSource>> {
    Py::new(
        py,
        WordPieceWithSource {
            piece: word_piece(py, offsets, &value.piece)?,
            start: offsets.get(value.start_index),
            end: offsets.get(value.end_index),
        },
    )
}

fn word_piece(
    py: Python<'_>,
    offsets: &CharOffsets,
    value: &upstream::WordPiece,
) -> PyResult<Py<WordPiece>> {
    let node = match value {
        upstream::WordPiece::Text(text) => WordPiece::Text { text: text.clone() },
        upstream::WordPiece::SingleQuotedText(text) => {
            WordPiece::SingleQuotedText { text: text.clone() }
        }
        upstream::WordPiece::AnsiCQuotedText(text) => {
            WordPiece::AnsiCQuotedText { text: text.clone() }
        }
        upstream::WordPiece::DoubleQuotedSequence(pieces) => WordPiece::DoubleQuotedSequence {
            pieces: pieces_with_offsets(py, offsets, pieces)?,
        },
        upstream::WordPiece::GettextDoubleQuotedSequence(pieces) => {
            WordPiece::GettextDoubleQuotedSequence {
                pieces: pieces_with_offsets(py, offsets, pieces)?,
            }
        }
        upstream::WordPiece::TildeExpansion(expr) => WordPiece::TildeExpansion {
            expr: FromRust::from_rust(py, expr)?,
        },
        upstream::WordPiece::ParameterExpansion(expr) => WordPiece::ParameterExpansion {
            expr: FromRust::from_rust(py, expr)?,
        },
        upstream::WordPiece::CommandSubstitution(command) => WordPiece::CommandSubstitution {
            command: command.clone(),
        },
        upstream::WordPiece::BackquotedCommandSubstitution(command) => {
            WordPiece::BackquotedCommandSubstitution {
                command: command.clone(),
            }
        }
        upstream::WordPiece::EscapeSequence(text) => {
            WordPiece::EscapeSequence { text: text.clone() }
        }
        upstream::WordPiece::ArithmeticExpression(expr) => WordPiece::ArithmeticExpression {
            expr: FromRust::from_rust(py, expr)?,
        },
    };
    enum_node(py, node)
}

impl FromRust<upstream::TildeExpr> for Py<TildeExpr> {
    fn from_rust(py: Python<'_>, value: &upstream::TildeExpr) -> PyResult<Self> {
        let node = match value {
            upstream::TildeExpr::Home => TildeExpr::Home {},
            upstream::TildeExpr::UserHome(user) => TildeExpr::UserHome { user: user.clone() },
            upstream::TildeExpr::WorkingDir => TildeExpr::WorkingDir {},
            upstream::TildeExpr::OldWorkingDir => TildeExpr::OldWorkingDir {},
            upstream::TildeExpr::NthDirFromTopOfDirStack { n, plus_used } => {
                TildeExpr::NthDirFromTopOfDirStack {
                    n: *n,
                    plus_used: *plus_used,
                }
            }
            upstream::TildeExpr::NthDirFromBottomOfDirStack { n } => {
                TildeExpr::NthDirFromBottomOfDirStack { n: *n }
            }
        };
        enum_node(py, node)
    }
}

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<WordPieceWithSource>()?;
    module.add_class::<WordPiece>()?;
    module.add_class::<TildeExpr>()
}
