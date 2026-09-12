use pyo3::create_exception;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::source::SourcePosition;
use crate::value::FromRust;

create_exception!(
    brush_parser._core,
    ParseError,
    PyValueError,
    "A program failed to parse. `position` is the `SourcePosition` the error \
     was detected near, or `None` when it was detected at the end of the input \
     or the tokenizer had no position to report."
);

create_exception!(
    brush_parser._core,
    WordParseError,
    PyValueError,
    "A word failed to parse. `input` is the text handed to the word parser."
);

pub fn parse_error(py: Python<'_>, error: &brush_parser::ParseError) -> PyErr {
    let position = match error {
        brush_parser::ParseError::ParsingNear(position) => Some(position),
        brush_parser::ParseError::Tokenizing { position, .. } => position.as_ref(),
        brush_parser::ParseError::ParsingAtEndOfInput => None,
    };
    let position = position
        .map(|position| Py::<SourcePosition>::from_rust(py, position))
        .transpose();
    with_attribute(
        py,
        ParseError::new_err(error.to_string()),
        "position",
        position,
    )
}

/// The message appends the PEG diagnostic that upstream keeps out of its
/// `Display` text.
pub fn word_parse_error(
    py: Python<'_>,
    input: &str,
    error: &brush_parser::WordParseError,
) -> PyErr {
    use brush_parser::WordParseError as Upstream;
    let location = match error {
        Upstream::ArithmeticExpression(location)
        | Upstream::Pattern(location)
        | Upstream::Prompt(location)
        | Upstream::Parameter(_, location)
        | Upstream::BraceExpansion(_, location)
        | Upstream::Word(_, location) => location,
    };
    let message = format!("{error}: {location}");
    with_attribute(py, WordParseError::new_err(message), "input", Ok(input))
}

fn with_attribute<'py, T: IntoPyObject<'py>>(
    py: Python<'py>,
    exception: PyErr,
    name: &str,
    value: PyResult<T>,
) -> PyErr {
    match value.and_then(|value| exception.value(py).setattr(name, value)) {
        Ok(()) => exception,
        Err(failure) => failure,
    }
}

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("ParseError", module.py().get_type::<ParseError>())?;
    module.add("WordParseError", module.py().get_type::<WordParseError>())
}
