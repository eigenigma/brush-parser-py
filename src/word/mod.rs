pub mod brace;
pub mod expressions;
pub mod parameters;
pub mod pieces;

use pyo3::prelude::*;

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    pieces::register(module)?;
    parameters::register(module)?;
    expressions::register(module)?;
    brace::register(module)
}
