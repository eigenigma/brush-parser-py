use brush_parser::ast as upstream;
use pyo3::prelude::*;

use crate::ast::commands::ProcessSubstitutionKind;
use crate::ast::compound::SubshellCommand;
use crate::ast::words::Word;
use crate::value::{
    FromRust, Seq, enum_node, from_rust_struct, from_rust_unit_enum, node_enum, node_struct,
    unit_enum,
};

node_struct! {
    RedirectList { items: Seq<IoRedirect> }
}

node_enum! {
    /// `fd` is `None` unless the source spells a file descriptor out. Upstream records no
    /// location for redirections.
    IoRedirect {
        File {
            fd: Option<i32>,
            kind: Py<IoFileRedirectKind>,
            target: Py<IoFileRedirectTarget>
        },
        HereDocument {
            fd: Option<i32>,
            document: Py<IoHereDocument>
        },
        HereString {
            fd: Option<i32>,
            word: Py<Word>
        },
        /// `&>` or `&>>`
        OutputAndError {
            target: Py<Word>,
            append: bool
        },
    }
}

unit_enum! {
    IoFileRedirectKind {
        /// `<`
        Read,
        /// `>`
        Write,
        /// `>>`
        Append,
        /// `<>`
        ReadAndWrite,
        /// `>|`
        Clobber,
        /// `<&`
        DuplicateInput,
        /// `>&`
        DuplicateOutput,
    }
}

node_enum! {
    IoFileRedirectTarget {
        Filename {
            word: Py<Word>
        },
        Fd {
            fd: i32
        },
        ProcessSubstitution {
            kind: Py<ProcessSubstitutionKind>,
            command: Py<SubshellCommand>
        },
        /// A word that expands to a filename, a descriptor, or a descriptor followed by
        /// `-` to close it.
        Duplicate {
            word: Py<Word>
        },
    }
}

node_struct! {
    /// `remove_tabs` is true for `<<-`; `requires_expansion` is true when `here_end` is
    /// unquoted, so the body undergoes expansion.
    IoHereDocument {
        remove_tabs: bool,
        requires_expansion: bool,
        here_end: Py<Word>,
        doc: Py<Word>,
    }
}

from_rust_struct!(upstream::RedirectList => RedirectList, value { items: value.0 });

impl FromRust<upstream::IoRedirect> for Py<IoRedirect> {
    fn from_rust(py: Python<'_>, value: &upstream::IoRedirect) -> PyResult<Self> {
        let node = match value {
            upstream::IoRedirect::File(fd, kind, target) => IoRedirect::File {
                fd: *fd,
                kind: FromRust::from_rust(py, kind)?,
                target: FromRust::from_rust(py, target)?,
            },
            upstream::IoRedirect::HereDocument(fd, document) => IoRedirect::HereDocument {
                fd: *fd,
                document: FromRust::from_rust(py, document)?,
            },
            upstream::IoRedirect::HereString(fd, word) => IoRedirect::HereString {
                fd: *fd,
                word: FromRust::from_rust(py, word)?,
            },
            upstream::IoRedirect::OutputAndError(target, append) => IoRedirect::OutputAndError {
                target: FromRust::from_rust(py, target)?,
                append: *append,
            },
        };
        enum_node(py, node)
    }
}

from_rust_unit_enum!(upstream::IoFileRedirectKind => IoFileRedirectKind {
    Read,
    Write,
    Append,
    ReadAndWrite,
    Clobber,
    DuplicateInput,
    DuplicateOutput,
});

impl FromRust<upstream::IoFileRedirectTarget> for Py<IoFileRedirectTarget> {
    fn from_rust(py: Python<'_>, value: &upstream::IoFileRedirectTarget) -> PyResult<Self> {
        let node = match value {
            upstream::IoFileRedirectTarget::Filename(word) => IoFileRedirectTarget::Filename {
                word: FromRust::from_rust(py, word)?,
            },
            upstream::IoFileRedirectTarget::Fd(fd) => IoFileRedirectTarget::Fd { fd: *fd },
            upstream::IoFileRedirectTarget::ProcessSubstitution(kind, command) => {
                IoFileRedirectTarget::ProcessSubstitution {
                    kind: FromRust::from_rust(py, kind)?,
                    command: FromRust::from_rust(py, command)?,
                }
            }
            upstream::IoFileRedirectTarget::Duplicate(word) => IoFileRedirectTarget::Duplicate {
                word: FromRust::from_rust(py, word)?,
            },
        };
        enum_node(py, node)
    }
}

from_rust_struct!(upstream::IoHereDocument => IoHereDocument, value {
    remove_tabs: value.remove_tabs,
    requires_expansion: value.requires_expansion,
    here_end: value.here_end,
    doc: value.doc,
});

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<RedirectList>()?;
    module.add_class::<IoRedirect>()?;
    module.add_class::<IoFileRedirectKind>()?;
    module.add_class::<IoFileRedirectTarget>()?;
    module.add_class::<IoHereDocument>()
}
