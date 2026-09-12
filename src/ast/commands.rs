use std::convert::Infallible;

use brush_parser::ast as upstream;
use pyo3::Borrowed;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use crate::ast::compound::{CompoundCommand, FunctionDefinition, SubshellCommand};
use crate::ast::extended_test::ExtendedTestExprCommand;
use crate::ast::redirects::{IoRedirect, RedirectList};
use crate::ast::words::Word;
use crate::source::SourceSpan;
use crate::value::{
    FromRust, Seq, enum_node, from_rust_struct, from_rust_unit_enum, node_enum, node_struct,
    unit_enum,
};

node_enum! {
    Command {
        /// An external program, builtin, function or similar.
        Simple {
            command: Py<SimpleCommand>
        },
        Compound {
            command: Py<CompoundCommand>,
            redirects: Option<Py<RedirectList>>
        },
        Function {
            definition: Py<FunctionDefinition>
        },
        /// `[[ expr ]]`
        ExtendedTest {
            command: Py<ExtendedTestExprCommand>,
            redirects: Option<Py<RedirectList>>
        },
    }
}

node_struct! {
    SimpleCommand {
        prefix: Option<Py<CommandPrefix>>,
        word_or_name: Option<Py<Word>>,
        suffix: Option<Py<CommandSuffix>>,
    }
}

node_struct! {
    /// Items before the command name: assignments and redirections.
    CommandPrefix { items: Seq<CommandPrefixOrSuffixItem> }
}

node_struct! {
    /// Items after the command name: arguments, declarations and redirections.
    CommandSuffix { items: Seq<CommandPrefixOrSuffixItem> }
}

unit_enum! {
    ProcessSubstitutionKind {
        /// `<(...)`
        Read,
        /// `>(...)`
        Write,
    }
}

node_enum! {
    CommandPrefixOrSuffixItem {
        IoRedirect {
            redirect: Py<IoRedirect>
        },
        Word {
            word: Py<Word>
        },
        /// An assignment paired with the source word it parses from.
        AssignmentWord {
            assignment: Py<Assignment>,
            word: Py<Word>
        },
        ProcessSubstitution {
            kind: Py<ProcessSubstitutionKind>,
            command: Py<SubshellCommand>
        },
    }
}

node_struct! {
    Assignment {
        name: Py<AssignmentName>,
        value: Py<AssignmentValue>,
        append: bool,
        loc: Py<SourceSpan>,
    }
}

node_enum! {
    AssignmentName {
        VariableName {
            name: String
        },
        /// `index` is the unexpanded index expression.
        ArrayElementName {
            name: String,
            index: String
        },
    }
}

node_enum! {
    AssignmentValue {
        Scalar {
            word: Py<Word>
        },
        /// `elements` holds `(key, word)` pairs; `key` is `None` for positional elements.
        Array {
            elements: ArrayElements
        },
    }
}

impl FromRust<upstream::Command> for Py<Command> {
    fn from_rust(py: Python<'_>, value: &upstream::Command) -> PyResult<Self> {
        let node = match value {
            upstream::Command::Simple(command) => Command::Simple {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::Command::Compound(command, redirects) => Command::Compound {
                command: FromRust::from_rust(py, command)?,
                redirects: FromRust::from_rust(py, redirects)?,
            },
            upstream::Command::Function(definition) => Command::Function {
                definition: FromRust::from_rust(py, definition)?,
            },
            upstream::Command::ExtendedTest(command, redirects) => Command::ExtendedTest {
                command: FromRust::from_rust(py, command)?,
                redirects: FromRust::from_rust(py, redirects)?,
            },
        };
        enum_node(py, node)
    }
}

from_rust_struct!(upstream::SimpleCommand => SimpleCommand, value {
    prefix: value.prefix,
    word_or_name: value.word_or_name,
    suffix: value.suffix,
});

from_rust_struct!(upstream::CommandPrefix => CommandPrefix, value { items: value.0 });

from_rust_struct!(upstream::CommandSuffix => CommandSuffix, value { items: value.0 });

from_rust_unit_enum!(upstream::ProcessSubstitutionKind => ProcessSubstitutionKind { Read, Write });

impl FromRust<upstream::CommandPrefixOrSuffixItem> for Py<CommandPrefixOrSuffixItem> {
    fn from_rust(py: Python<'_>, value: &upstream::CommandPrefixOrSuffixItem) -> PyResult<Self> {
        let node = match value {
            upstream::CommandPrefixOrSuffixItem::IoRedirect(redirect) => {
                CommandPrefixOrSuffixItem::IoRedirect {
                    redirect: FromRust::from_rust(py, redirect)?,
                }
            }
            upstream::CommandPrefixOrSuffixItem::Word(word) => CommandPrefixOrSuffixItem::Word {
                word: FromRust::from_rust(py, word)?,
            },
            upstream::CommandPrefixOrSuffixItem::AssignmentWord(assignment, word) => {
                CommandPrefixOrSuffixItem::AssignmentWord {
                    assignment: FromRust::from_rust(py, assignment)?,
                    word: FromRust::from_rust(py, word)?,
                }
            }
            upstream::CommandPrefixOrSuffixItem::ProcessSubstitution(kind, command) => {
                CommandPrefixOrSuffixItem::ProcessSubstitution {
                    kind: FromRust::from_rust(py, kind)?,
                    command: FromRust::from_rust(py, command)?,
                }
            }
        };
        enum_node(py, node)
    }
}

from_rust_struct!(upstream::Assignment => Assignment, value {
    name: value.name,
    value: value.value,
    append: value.append,
    loc: value.loc,
});

impl FromRust<upstream::AssignmentName> for Py<AssignmentName> {
    fn from_rust(py: Python<'_>, value: &upstream::AssignmentName) -> PyResult<Self> {
        let node = match value {
            upstream::AssignmentName::VariableName(name) => {
                AssignmentName::VariableName { name: name.clone() }
            }
            upstream::AssignmentName::ArrayElementName(name, index) => {
                AssignmentName::ArrayElementName {
                    name: name.clone(),
                    index: index.clone(),
                }
            }
        };
        enum_node(py, node)
    }
}

type ArrayElement = (Option<Py<Word>>, Py<Word>);

/// A Python tuple of `(Word | None, Word)` pairs. Extraction from Python checks each pair's
/// arity and element classes.
pub struct ArrayElements(Py<PyTuple>);

impl ArrayElements {
    fn from_pairs(py: Python<'_>, pairs: Vec<ArrayElement>) -> PyResult<Self> {
        Ok(Self(PyTuple::new(py, pairs)?.unbind()))
    }
}

impl FromRust<Vec<(Option<upstream::Word>, upstream::Word)>> for ArrayElements {
    fn from_rust(
        py: Python<'_>,
        value: &Vec<(Option<upstream::Word>, upstream::Word)>,
    ) -> PyResult<Self> {
        let pairs = value
            .iter()
            .map(|(key, word)| {
                Ok((
                    FromRust::from_rust(py, key)?,
                    FromRust::from_rust(py, word)?,
                ))
            })
            .collect::<PyResult<Vec<ArrayElement>>>()?;
        Self::from_pairs(py, pairs)
    }
}

impl<'a, 'py> FromPyObject<'a, 'py> for ArrayElements {
    type Error = PyErr;

    fn extract(obj: Borrowed<'a, 'py, PyAny>) -> PyResult<Self> {
        let pairs: Vec<ArrayElement> = obj.extract()?;
        Self::from_pairs(obj.py(), pairs)
    }
}

impl<'py> IntoPyObject<'py> for ArrayElements {
    type Target = PyTuple;
    type Output = Bound<'py, PyTuple>;
    type Error = Infallible;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Ok(self.0.into_bound(py))
    }
}

impl<'a, 'py> IntoPyObject<'py> for &'a ArrayElements {
    type Target = PyTuple;
    type Output = Borrowed<'a, 'py, PyTuple>;
    type Error = Infallible;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Ok(self.0.bind_borrowed(py))
    }
}

impl FromRust<upstream::AssignmentValue> for Py<AssignmentValue> {
    fn from_rust(py: Python<'_>, value: &upstream::AssignmentValue) -> PyResult<Self> {
        let node = match value {
            upstream::AssignmentValue::Scalar(word) => AssignmentValue::Scalar {
                word: FromRust::from_rust(py, word)?,
            },
            upstream::AssignmentValue::Array(elements) => AssignmentValue::Array {
                elements: FromRust::from_rust(py, elements)?,
            },
        };
        enum_node(py, node)
    }
}

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<Command>()?;
    module.add_class::<SimpleCommand>()?;
    module.add_class::<CommandPrefix>()?;
    module.add_class::<CommandSuffix>()?;
    module.add_class::<ProcessSubstitutionKind>()?;
    module.add_class::<CommandPrefixOrSuffixItem>()?;
    module.add_class::<Assignment>()?;
    module.add_class::<AssignmentName>()?;
    module.add_class::<AssignmentValue>()
}
