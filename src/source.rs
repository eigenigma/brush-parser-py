use pyo3::prelude::*;

use crate::value::{from_rust_struct, node_struct};

node_struct! {
    /// `index` is a 0-based char index; `line` and `column` are 1-based.
    SourcePosition { index: usize, line: usize, column: usize }
}

node_struct! {
    /// `end` is exclusive.
    SourceSpan { start: Py<SourcePosition>, end: Py<SourcePosition> }
}

from_rust_struct!(brush_parser::SourcePosition => SourcePosition, value {
    index: value.index,
    line: value.line,
    column: value.column,
});

from_rust_struct!(brush_parser::SourceSpan => SourceSpan, value {
    start: value.start,
    end: value.end,
});

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<SourcePosition>()?;
    module.add_class::<SourceSpan>()
}
