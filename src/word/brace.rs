use brush_parser::word as upstream;
use pyo3::prelude::*;

use crate::value::{FromRust, Seq, enum_node, node_enum};

node_enum! {
    BraceExpressionOrText {
        /// `{...}`, holding the comma-separated members.
        Expr {
            members: Seq<BraceExpressionMember>
        },
        Text {
            text: String
        },
    }
}

node_enum! {
    BraceExpressionMember {
        /// `{start..end..increment}` over integers, `end` inclusive.
        NumberSequence {
            start: i64,
            end: i64,
            increment: i64
        },
        /// `{start..end..increment}` over single characters, `end` inclusive.
        CharSequence {
            start: char,
            end: char,
            increment: i64
        },
        /// One comma-separated member, itself text and nested expressions.
        Child {
            items: Seq<BraceExpressionOrText>
        },
    }
}

impl FromRust<upstream::BraceExpressionOrText> for Py<BraceExpressionOrText> {
    fn from_rust(py: Python<'_>, value: &upstream::BraceExpressionOrText) -> PyResult<Self> {
        let node = match value {
            upstream::BraceExpressionOrText::Expr(members) => BraceExpressionOrText::Expr {
                members: FromRust::from_rust(py, members)?,
            },
            upstream::BraceExpressionOrText::Text(text) => {
                BraceExpressionOrText::Text { text: text.clone() }
            }
        };
        enum_node(py, node)
    }
}

impl FromRust<upstream::BraceExpressionMember> for Py<BraceExpressionMember> {
    fn from_rust(py: Python<'_>, value: &upstream::BraceExpressionMember) -> PyResult<Self> {
        let node = match value {
            upstream::BraceExpressionMember::NumberSequence {
                start,
                end,
                increment,
            } => BraceExpressionMember::NumberSequence {
                start: *start,
                end: *end,
                increment: *increment,
            },
            upstream::BraceExpressionMember::CharSequence {
                start,
                end,
                increment,
            } => BraceExpressionMember::CharSequence {
                start: *start,
                end: *end,
                increment: *increment,
            },
            upstream::BraceExpressionMember::Child(items) => BraceExpressionMember::Child {
                items: FromRust::from_rust(py, items)?,
            },
        };
        enum_node(py, node)
    }
}

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<BraceExpressionOrText>()?;
    module.add_class::<BraceExpressionMember>()
}
