use brush_parser::word as upstream;
use pyo3::prelude::*;

use crate::value::{FromRust, enum_node, from_rust_unit_enum, node_enum, unit_enum};

unit_enum! {
    ParameterTestType {
        /// The `${x:-...}` forms: unset or null.
        UnsetOrNull,
        /// The `${x-...}` forms: unset only.
        Unset,
    }
}

node_enum! {
    Parameter {
        /// `$N`, with `index` holding N and `$0` counting as 0.
        Positional {
            index: u32
        },
        Special {
            parameter: Py<SpecialParameter>
        },
        Named {
            name: String
        },
        /// `name[index]`.
        NamedWithIndex {
            name: String,
            /// Unexpanded subscript text.
            index: String
        },
        /// `name[@]` or `name[*]`.
        NamedWithAllIndices {
            name: String,
            /// True for `*`, false for `@`.
            concatenate: bool
        },
    }
}

node_enum! {
    SpecialParameter {
        /// `$@` or `$*`.
        AllPositionalParameters {
            /// True for `*`, false for `@`.
            concatenate: bool
        },
        /// `$#`
        PositionalParameterCount {},
        /// `$?`
        LastExitStatus {},
        /// `$-`
        CurrentOptionFlags {},
        /// `$$`
        ProcessId {},
        /// `$!`
        LastBackgroundProcessId {},
        /// `$0`
        ShellName {},
    }
}

unit_enum! {
    SubstringMatchKind {
        /// `${x/#pat/rep}`
        Prefix,
        /// `${x/%pat/rep}`
        Suffix,
        /// `${x/pat/rep}`
        FirstOccurrence,
        /// `${x//pat/rep}`
        Anywhere,
    }
}

node_enum! {
    /// The `op` of a `${x@op}` transformation.
    ParameterTransformOp {
        /// `@u`
        CapitalizeInitial {},
        /// `@E`
        ExpandEscapeSequences {},
        /// `@Q` on arrays / `@K`; `separate_words` is true for `@k`.
        PossiblyQuoteWithArraysExpanded {
            separate_words: bool
        },
        /// `@P`
        PromptExpand {},
        /// `@Q`
        Quoted {},
        /// `@A`
        ToAssignmentLogic {},
        /// `@a`
        ToAttributeFlags {},
        /// `@L`
        ToLowerCase {},
        /// `@U`
        ToUpperCase {},
    }
}

from_rust_unit_enum!(upstream::ParameterTestType => ParameterTestType { UnsetOrNull, Unset });

impl FromRust<upstream::Parameter> for Py<Parameter> {
    fn from_rust(py: Python<'_>, value: &upstream::Parameter) -> PyResult<Self> {
        let node = match value {
            upstream::Parameter::Positional(index) => Parameter::Positional { index: *index },
            upstream::Parameter::Special(parameter) => Parameter::Special {
                parameter: FromRust::from_rust(py, parameter)?,
            },
            upstream::Parameter::Named(name) => Parameter::Named { name: name.clone() },
            upstream::Parameter::NamedWithIndex { name, index } => Parameter::NamedWithIndex {
                name: name.clone(),
                index: index.clone(),
            },
            upstream::Parameter::NamedWithAllIndices { name, concatenate } => {
                Parameter::NamedWithAllIndices {
                    name: name.clone(),
                    concatenate: *concatenate,
                }
            }
        };
        enum_node(py, node)
    }
}

impl FromRust<upstream::SpecialParameter> for Py<SpecialParameter> {
    fn from_rust(py: Python<'_>, value: &upstream::SpecialParameter) -> PyResult<Self> {
        let node = match value {
            upstream::SpecialParameter::AllPositionalParameters { concatenate } => {
                SpecialParameter::AllPositionalParameters {
                    concatenate: *concatenate,
                }
            }
            upstream::SpecialParameter::PositionalParameterCount => {
                SpecialParameter::PositionalParameterCount {}
            }
            upstream::SpecialParameter::LastExitStatus => SpecialParameter::LastExitStatus {},
            upstream::SpecialParameter::CurrentOptionFlags => {
                SpecialParameter::CurrentOptionFlags {}
            }
            upstream::SpecialParameter::ProcessId => SpecialParameter::ProcessId {},
            upstream::SpecialParameter::LastBackgroundProcessId => {
                SpecialParameter::LastBackgroundProcessId {}
            }
            upstream::SpecialParameter::ShellName => SpecialParameter::ShellName {},
        };
        enum_node(py, node)
    }
}

from_rust_unit_enum!(upstream::SubstringMatchKind => SubstringMatchKind {
    Prefix,
    Suffix,
    FirstOccurrence,
    Anywhere,
});

impl FromRust<upstream::ParameterTransformOp> for Py<ParameterTransformOp> {
    fn from_rust(py: Python<'_>, value: &upstream::ParameterTransformOp) -> PyResult<Self> {
        let node = match value {
            upstream::ParameterTransformOp::CapitalizeInitial => {
                ParameterTransformOp::CapitalizeInitial {}
            }
            upstream::ParameterTransformOp::ExpandEscapeSequences => {
                ParameterTransformOp::ExpandEscapeSequences {}
            }
            upstream::ParameterTransformOp::PossiblyQuoteWithArraysExpanded { separate_words } => {
                ParameterTransformOp::PossiblyQuoteWithArraysExpanded {
                    separate_words: *separate_words,
                }
            }
            upstream::ParameterTransformOp::PromptExpand => ParameterTransformOp::PromptExpand {},
            upstream::ParameterTransformOp::Quoted => ParameterTransformOp::Quoted {},
            upstream::ParameterTransformOp::ToAssignmentLogic => {
                ParameterTransformOp::ToAssignmentLogic {}
            }
            upstream::ParameterTransformOp::ToAttributeFlags => {
                ParameterTransformOp::ToAttributeFlags {}
            }
            upstream::ParameterTransformOp::ToLowerCase => ParameterTransformOp::ToLowerCase {},
            upstream::ParameterTransformOp::ToUpperCase => ParameterTransformOp::ToUpperCase {},
        };
        enum_node(py, node)
    }
}

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<ParameterTestType>()?;
    module.add_class::<Parameter>()?;
    module.add_class::<SpecialParameter>()?;
    module.add_class::<SubstringMatchKind>()?;
    module.add_class::<ParameterTransformOp>()
}
