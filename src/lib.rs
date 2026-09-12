//! Python binding for the `brush-parser` crate: every module below mirrors an
//! upstream module with one class per upstream type.

mod ast;
mod errors;
mod options;
mod source;
mod value;
mod word;

use std::io::BufReader;

use brush_parser::Parser;
use pyo3::prelude::*;

use crate::ast::lists::Program;
use crate::value::{FromRust, Seq};
use crate::word::brace::BraceExpressionOrText;
use crate::word::parameters::Parameter;
use crate::word::pieces::{WordPieceWithSource, pieces_from_rust};

/// Exact, because `Cargo.toml` pins `brush-parser` with `=`.
pub const BRUSH_PARSER_VERSION: &str = "0.4.0";

/// Raises `ParseError`. The keyword options mirror upstream `ParserOptions`
/// and its defaults, as they do on every entry point here.
#[pyfunction]
#[pyo3(signature = (
    text,
    *,
    enable_extended_globbing = true,
    posix_mode = false,
    sh_mode = false,
    tilde_expansion_at_word_start = true,
    tilde_expansion_after_colon = false,
))]
fn parse_program(
    py: Python<'_>,
    text: &str,
    enable_extended_globbing: bool,
    posix_mode: bool,
    sh_mode: bool,
    tilde_expansion_at_word_start: bool,
    tilde_expansion_after_colon: bool,
) -> PyResult<Py<Program>> {
    let options = options::parser_options(
        enable_extended_globbing,
        posix_mode,
        sh_mode,
        tilde_expansion_at_word_start,
        tilde_expansion_after_colon,
    );
    let parsed = py.detach(|| {
        let mut parser = Parser::new(BufReader::new(text.as_bytes()), &options);
        parser.parse_program()
    });
    match parsed {
        Ok(program) => Py::<Program>::from_rust(py, &program),
        Err(error) => Err(errors::parse_error(py, &error)),
    }
}

/// Piece offsets are char indices into `word`. Raises `WordParseError` with
/// `input` set to `word`. Upstream caches the last 64 results globally.
#[pyfunction]
#[pyo3(signature = (
    word,
    *,
    enable_extended_globbing = true,
    posix_mode = false,
    sh_mode = false,
    tilde_expansion_at_word_start = true,
    tilde_expansion_after_colon = false,
))]
fn parse_word(
    py: Python<'_>,
    word: &str,
    enable_extended_globbing: bool,
    posix_mode: bool,
    sh_mode: bool,
    tilde_expansion_at_word_start: bool,
    tilde_expansion_after_colon: bool,
) -> PyResult<Seq<WordPieceWithSource>> {
    let options = options::parser_options(
        enable_extended_globbing,
        posix_mode,
        sh_mode,
        tilde_expansion_at_word_start,
        tilde_expansion_after_colon,
    );
    let parsed = py.detach(|| brush_parser::word::parse(word, &options));
    word_pieces(py, word, parsed)
}

/// Quotes in `word` are literal characters. Raises `WordParseError` with
/// `input` set to `word`.
#[pyfunction]
#[pyo3(signature = (
    word,
    *,
    enable_extended_globbing = true,
    posix_mode = false,
    sh_mode = false,
    tilde_expansion_at_word_start = true,
    tilde_expansion_after_colon = false,
))]
fn parse_heredoc(
    py: Python<'_>,
    word: &str,
    enable_extended_globbing: bool,
    posix_mode: bool,
    sh_mode: bool,
    tilde_expansion_at_word_start: bool,
    tilde_expansion_after_colon: bool,
) -> PyResult<Seq<WordPieceWithSource>> {
    let options = options::parser_options(
        enable_extended_globbing,
        posix_mode,
        sh_mode,
        tilde_expansion_at_word_start,
        tilde_expansion_after_colon,
    );
    let parsed = py.detach(|| brush_parser::word::parse_heredoc(word, &options));
    word_pieces(py, word, parsed)
}

/// `word` is the text inside a `${...}` reference. Raises `WordParseError`
/// with `input` set to `word`.
#[pyfunction]
#[pyo3(signature = (
    word,
    *,
    enable_extended_globbing = true,
    posix_mode = false,
    sh_mode = false,
    tilde_expansion_at_word_start = true,
    tilde_expansion_after_colon = false,
))]
fn parse_parameter(
    py: Python<'_>,
    word: &str,
    enable_extended_globbing: bool,
    posix_mode: bool,
    sh_mode: bool,
    tilde_expansion_at_word_start: bool,
    tilde_expansion_after_colon: bool,
) -> PyResult<Py<Parameter>> {
    let options = options::parser_options(
        enable_extended_globbing,
        posix_mode,
        sh_mode,
        tilde_expansion_at_word_start,
        tilde_expansion_after_colon,
    );
    let parsed = py.detach(|| brush_parser::word::parse_parameter(word, &options));
    match parsed {
        Ok(parameter) => Py::<Parameter>::from_rust(py, &parameter),
        Err(error) => Err(errors::word_parse_error(py, word, &error)),
    }
}

/// `None` when the word holds no expansion. Raises `WordParseError` with
/// `input` set to `word`.
#[pyfunction]
#[pyo3(signature = (
    word,
    *,
    enable_extended_globbing = true,
    posix_mode = false,
    sh_mode = false,
    tilde_expansion_at_word_start = true,
    tilde_expansion_after_colon = false,
))]
fn parse_brace_expansions(
    py: Python<'_>,
    word: &str,
    enable_extended_globbing: bool,
    posix_mode: bool,
    sh_mode: bool,
    tilde_expansion_at_word_start: bool,
    tilde_expansion_after_colon: bool,
) -> PyResult<Option<Seq<BraceExpressionOrText>>> {
    let options = options::parser_options(
        enable_extended_globbing,
        posix_mode,
        sh_mode,
        tilde_expansion_at_word_start,
        tilde_expansion_after_colon,
    );
    let parsed = py.detach(|| brush_parser::word::parse_brace_expansions(word, &options));
    match parsed {
        Ok(expansions) => FromRust::from_rust(py, &expansions),
        Err(error) => Err(errors::word_parse_error(py, word, &error)),
    }
}

fn word_pieces(
    py: Python<'_>,
    word: &str,
    parsed: Result<Vec<brush_parser::word::WordPieceWithSource>, brush_parser::WordParseError>,
) -> PyResult<Seq<WordPieceWithSource>> {
    match parsed {
        Ok(pieces) => pieces_from_rust(py, word, &pieces),
        Err(error) => Err(errors::word_parse_error(py, word, &error)),
    }
}

#[pymodule]
mod _core {
    use pyo3::prelude::*;

    #[pymodule_export]
    use super::{
        parse_brace_expansions, parse_heredoc, parse_parameter, parse_program, parse_word,
    };

    #[pymodule_init]
    fn init(module: &Bound<'_, PyModule>) -> PyResult<()> {
        module.add("BRUSH_PARSER_VERSION", super::BRUSH_PARSER_VERSION)?;
        super::source::register(module)?;
        super::errors::register(module)?;
        super::ast::register(module)?;
        super::word::register(module)
    }
}

#[cfg(test)]
mod tests {
    use super::BRUSH_PARSER_VERSION;

    #[test]
    fn version_constant_matches_cargo_pin() {
        let manifest = include_str!("../Cargo.toml");
        let pin = format!("brush-parser = \"={BRUSH_PARSER_VERSION}\"");
        assert!(manifest.contains(&pin), "Cargo.toml must pin {pin}");
    }
}
