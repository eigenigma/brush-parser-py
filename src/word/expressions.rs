use brush_parser::word as upstream;
use pyo3::prelude::*;

use crate::ast::words::UnexpandedArithmeticExpr;
use crate::value::{FromRust, enum_node, node_enum};
use crate::word::parameters::{
    Parameter, ParameterTestType, ParameterTransformOp, SubstringMatchKind,
};

node_enum! {
    /// Defaults, messages, patterns and replacements are unexpanded text.
    /// Every variant that names a parameter also carries `indirect`, true for
    /// the `${!x...}` forms.
    ParameterExpr {
        /// `$x` or `${x}`.
        Parameter {
            parameter: Py<Parameter>,
            indirect: bool
        },
        /// `${x:-default}` / `${x-default}`.
        UseDefaultValues {
            parameter: Py<Parameter>,
            indirect: bool,
            test_type: Py<ParameterTestType>,
            default_value: Option<String>
        },
        /// `${x:=default}` / `${x=default}`.
        AssignDefaultValues {
            parameter: Py<Parameter>,
            indirect: bool,
            test_type: Py<ParameterTestType>,
            default_value: Option<String>
        },
        /// `${x:?message}` / `${x?message}`.
        IndicateErrorIfNullOrUnset {
            parameter: Py<Parameter>,
            indirect: bool,
            test_type: Py<ParameterTestType>,
            error_message: Option<String>
        },
        /// `${x:+alternative}` / `${x+alternative}`.
        UseAlternativeValue {
            parameter: Py<Parameter>,
            indirect: bool,
            test_type: Py<ParameterTestType>,
            alternative_value: Option<String>
        },
        /// `${#x}`.
        ParameterLength {
            parameter: Py<Parameter>,
            indirect: bool
        },
        /// `${x%pattern}`.
        RemoveSmallestSuffixPattern {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: Option<String>
        },
        /// `${x%%pattern}`.
        RemoveLargestSuffixPattern {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: Option<String>
        },
        /// `${x#pattern}`.
        RemoveSmallestPrefixPattern {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: Option<String>
        },
        /// `${x##pattern}`.
        RemoveLargestPrefixPattern {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: Option<String>
        },
        /// `${x:offset}` / `${x:offset:length}`.
        Substring {
            parameter: Py<Parameter>,
            indirect: bool,
            offset: Py<UnexpandedArithmeticExpr>,
            length: Option<Py<UnexpandedArithmeticExpr>>
        },
        /// `${x@op}`.
        Transform {
            parameter: Py<Parameter>,
            indirect: bool,
            op: Py<ParameterTransformOp>
        },
        /// `${x^pattern}`.
        UppercaseFirstChar {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: Option<String>
        },
        /// `${x^^pattern}`.
        UppercasePattern {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: Option<String>
        },
        /// `${x,pattern}`.
        LowercaseFirstChar {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: Option<String>
        },
        /// `${x,,pattern}`.
        LowercasePattern {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: Option<String>
        },
        /// `${x/pattern/replacement}` and its `#`, `%` and `//` forms.
        ReplaceSubstring {
            parameter: Py<Parameter>,
            indirect: bool,
            pattern: String,
            /// `None` deletes the matches.
            replacement: Option<String>,
            match_kind: Py<SubstringMatchKind>
        },
        /// `${!prefix@}` / `${!prefix*}`.
        VariableNames {
            prefix: String,
            /// True for `*`, false for `@`.
            concatenate: bool
        },
        /// `${!name[@]}` / `${!name[*]}`.
        MemberKeys {
            variable_name: String,
            /// True for `*`, false for `@`.
            concatenate: bool
        },
    }
}

impl FromRust<upstream::ParameterExpr> for Py<ParameterExpr> {
    fn from_rust(py: Python<'_>, value: &upstream::ParameterExpr) -> PyResult<Self> {
        use upstream::ParameterExpr as U;
        let node = match value {
            U::Parameter {
                parameter,
                indirect,
            } => ParameterExpr::Parameter {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
            },
            U::UseDefaultValues {
                parameter,
                indirect,
                test_type,
                default_value,
            } => ParameterExpr::UseDefaultValues {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                test_type: FromRust::from_rust(py, test_type)?,
                default_value: default_value.clone(),
            },
            U::AssignDefaultValues {
                parameter,
                indirect,
                test_type,
                default_value,
            } => ParameterExpr::AssignDefaultValues {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                test_type: FromRust::from_rust(py, test_type)?,
                default_value: default_value.clone(),
            },
            U::IndicateErrorIfNullOrUnset {
                parameter,
                indirect,
                test_type,
                error_message,
            } => ParameterExpr::IndicateErrorIfNullOrUnset {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                test_type: FromRust::from_rust(py, test_type)?,
                error_message: error_message.clone(),
            },
            U::UseAlternativeValue {
                parameter,
                indirect,
                test_type,
                alternative_value,
            } => ParameterExpr::UseAlternativeValue {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                test_type: FromRust::from_rust(py, test_type)?,
                alternative_value: alternative_value.clone(),
            },
            U::ParameterLength {
                parameter,
                indirect,
            } => ParameterExpr::ParameterLength {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
            },
            U::RemoveSmallestSuffixPattern {
                parameter,
                indirect,
                pattern,
            } => ParameterExpr::RemoveSmallestSuffixPattern {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
            },
            U::RemoveLargestSuffixPattern {
                parameter,
                indirect,
                pattern,
            } => ParameterExpr::RemoveLargestSuffixPattern {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
            },
            U::RemoveSmallestPrefixPattern {
                parameter,
                indirect,
                pattern,
            } => ParameterExpr::RemoveSmallestPrefixPattern {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
            },
            U::RemoveLargestPrefixPattern {
                parameter,
                indirect,
                pattern,
            } => ParameterExpr::RemoveLargestPrefixPattern {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
            },
            U::Substring {
                parameter,
                indirect,
                offset,
                length,
            } => ParameterExpr::Substring {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                offset: FromRust::from_rust(py, offset)?,
                length: FromRust::from_rust(py, length)?,
            },
            U::Transform {
                parameter,
                indirect,
                op,
            } => ParameterExpr::Transform {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                op: FromRust::from_rust(py, op)?,
            },
            U::UppercaseFirstChar {
                parameter,
                indirect,
                pattern,
            } => ParameterExpr::UppercaseFirstChar {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
            },
            U::UppercasePattern {
                parameter,
                indirect,
                pattern,
            } => ParameterExpr::UppercasePattern {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
            },
            U::LowercaseFirstChar {
                parameter,
                indirect,
                pattern,
            } => ParameterExpr::LowercaseFirstChar {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
            },
            U::LowercasePattern {
                parameter,
                indirect,
                pattern,
            } => ParameterExpr::LowercasePattern {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
            },
            U::ReplaceSubstring {
                parameter,
                indirect,
                pattern,
                replacement,
                match_kind,
            } => ParameterExpr::ReplaceSubstring {
                parameter: FromRust::from_rust(py, parameter)?,
                indirect: *indirect,
                pattern: pattern.clone(),
                replacement: replacement.clone(),
                match_kind: FromRust::from_rust(py, match_kind)?,
            },
            U::VariableNames {
                prefix,
                concatenate,
            } => ParameterExpr::VariableNames {
                prefix: prefix.clone(),
                concatenate: *concatenate,
            },
            U::MemberKeys {
                variable_name,
                concatenate,
            } => ParameterExpr::MemberKeys {
                variable_name: variable_name.clone(),
                concatenate: *concatenate,
            },
        };
        enum_node(py, node)
    }
}

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<ParameterExpr>()
}
