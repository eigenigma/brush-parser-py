pub mod clauses;
pub mod commands;
pub mod compound;
pub mod extended_test;
pub mod lists;
pub mod redirects;
pub mod words;

use pyo3::prelude::*;

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    lists::register(module)?;
    commands::register(module)?;
    words::register(module)?;
    redirects::register(module)?;
    compound::register(module)?;
    clauses::register(module)?;
    extended_test::register(module)
}
