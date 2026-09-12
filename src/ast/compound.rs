use brush_parser::ast as upstream;
use pyo3::prelude::*;

use crate::ast::clauses::{
    ArithmeticForClauseCommand, CaseClauseCommand, ForClauseCommand, IfClauseCommand,
    WhileOrUntilClauseCommand,
};
use crate::ast::commands::Command;
use crate::ast::lists::CompoundList;
use crate::ast::redirects::RedirectList;
use crate::ast::words::{UnexpandedArithmeticExpr, Word};
use crate::source::SourceSpan;
use crate::value::{FromRust, enum_node, from_rust_struct, node_enum, node_struct};

node_enum! {
    CompoundCommand {
        /// `(( expr ))`
        Arithmetic {
            command: Py<ArithmeticCommand>
        },
        /// `for (( init; cond; update )) do ... done`
        ArithmeticForClause {
            command: Py<ArithmeticForClauseCommand>
        },
        /// `{ ...; }`
        BraceGroup {
            command: Py<BraceGroupCommand>
        },
        /// `( ... )`
        Subshell {
            command: Py<SubshellCommand>
        },
        /// `for name in words; do ... done`
        ForClause {
            command: Py<ForClauseCommand>
        },
        /// `case word in ... esac`
        CaseClause {
            command: Py<CaseClauseCommand>
        },
        /// `if ...; then ...; fi`
        IfClause {
            command: Py<IfClauseCommand>
        },
        /// `while ...; do ...; done`
        WhileClause {
            command: Py<WhileOrUntilClauseCommand>
        },
        /// `until ...; do ...; done`
        UntilClause {
            command: Py<WhileOrUntilClauseCommand>
        },
        /// `coproc [name] command`
        Coprocess {
            command: Py<CoprocessCommand>
        },
    }
}

node_struct! {
    /// `(( expr ))`
    ArithmeticCommand { expr: Py<UnexpandedArithmeticExpr>, loc: Py<SourceSpan> }
}

node_struct! {
    /// `( list )`
    SubshellCommand { list: Py<CompoundList>, loc: Py<SourceSpan> }
}

node_struct! {
    /// `{ list; }`
    BraceGroupCommand { list: Py<CompoundList>, loc: Py<SourceSpan> }
}

node_struct! {
    /// `do list; done`
    DoGroupCommand { list: Py<CompoundList>, loc: Py<SourceSpan> }
}

node_struct! {
    /// `coproc [name] command`. Upstream omits `loc` from its serde output.
    CoprocessCommand { name: Option<Py<Word>>, body: Py<Command>, loc: Py<SourceSpan> }
}

node_struct! {
    FunctionDefinition { fname: Py<Word>, body: Py<FunctionBody> }
}

node_struct! {
    FunctionBody { command: Py<CompoundCommand>, redirects: Option<Py<RedirectList>> }
}

impl FromRust<upstream::CompoundCommand> for Py<CompoundCommand> {
    fn from_rust(py: Python<'_>, value: &upstream::CompoundCommand) -> PyResult<Self> {
        let node = match value {
            upstream::CompoundCommand::Arithmetic(command) => CompoundCommand::Arithmetic {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::CompoundCommand::ArithmeticForClause(command) => {
                CompoundCommand::ArithmeticForClause {
                    command: FromRust::from_rust(py, command)?,
                }
            }
            upstream::CompoundCommand::BraceGroup(command) => CompoundCommand::BraceGroup {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::CompoundCommand::Subshell(command) => CompoundCommand::Subshell {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::CompoundCommand::ForClause(command) => CompoundCommand::ForClause {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::CompoundCommand::CaseClause(command) => CompoundCommand::CaseClause {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::CompoundCommand::IfClause(command) => CompoundCommand::IfClause {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::CompoundCommand::WhileClause(command) => CompoundCommand::WhileClause {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::CompoundCommand::UntilClause(command) => CompoundCommand::UntilClause {
                command: FromRust::from_rust(py, command)?,
            },
            upstream::CompoundCommand::Coprocess(command) => CompoundCommand::Coprocess {
                command: FromRust::from_rust(py, command)?,
            },
        };
        enum_node(py, node)
    }
}

from_rust_struct!(upstream::ArithmeticCommand => ArithmeticCommand, value {
    expr: value.expr,
    loc: value.loc,
});

from_rust_struct!(upstream::SubshellCommand => SubshellCommand, value {
    list: value.list,
    loc: value.loc,
});

from_rust_struct!(upstream::BraceGroupCommand => BraceGroupCommand, value {
    list: value.list,
    loc: value.loc,
});

from_rust_struct!(upstream::DoGroupCommand => DoGroupCommand, value {
    list: value.list,
    loc: value.loc,
});

from_rust_struct!(upstream::CoprocessCommand => CoprocessCommand, value {
    name: value.name,
    body: value.body,
    loc: value.loc,
});

from_rust_struct!(upstream::FunctionDefinition => FunctionDefinition, value {
    fname: value.fname,
    body: value.body,
});

from_rust_struct!(upstream::FunctionBody => FunctionBody, value {
    command: value.0,
    redirects: value.1,
});

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<CompoundCommand>()?;
    module.add_class::<ArithmeticCommand>()?;
    module.add_class::<SubshellCommand>()?;
    module.add_class::<BraceGroupCommand>()?;
    module.add_class::<DoGroupCommand>()?;
    module.add_class::<CoprocessCommand>()?;
    module.add_class::<FunctionDefinition>()?;
    module.add_class::<FunctionBody>()
}
