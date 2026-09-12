use brush_parser::ast as upstream;
use pyo3::prelude::*;

use crate::source::SourceSpan;
use crate::value::{from_rust_struct, node_struct};

node_struct! {
    /// A word exactly as the tokenizer produced it, unexpanded.
    Word { value: String, loc: Option<Py<SourceSpan>> }
}

node_struct! {
    /// Raw text, neither expanded nor parsed as arithmetic.
    UnexpandedArithmeticExpr { value: String }
}

from_rust_struct!(upstream::Word => Word, value {
    value: value.value,
    loc: value.loc,
});

from_rust_struct!(upstream::UnexpandedArithmeticExpr => UnexpandedArithmeticExpr, value {
    value: value.value,
});

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<Word>()?;
    module.add_class::<UnexpandedArithmeticExpr>()
}
