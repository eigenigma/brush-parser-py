use brush_parser::ast as upstream;
use pyo3::prelude::*;

use crate::ast::compound::DoGroupCommand;
use crate::ast::lists::CompoundList;
use crate::ast::words::{UnexpandedArithmeticExpr, Word};
use crate::source::SourceSpan;
use crate::value::{Seq, from_rust_struct, from_rust_unit_enum, node_struct, unit_enum};

node_struct! {
    /// `for name [in words]; do ...; done`. `values` is `None` when `in` is absent.
    ForClauseCommand {
        variable_name: String,
        values: Option<Seq<Word>>,
        body: Py<DoGroupCommand>,
        loc: Py<SourceSpan>,
    }
}

node_struct! {
    /// `for (( initializer; condition; updater )); do ...; done`
    ArithmeticForClauseCommand {
        initializer: Option<Py<UnexpandedArithmeticExpr>>,
        condition: Option<Py<UnexpandedArithmeticExpr>>,
        updater: Option<Py<UnexpandedArithmeticExpr>>,
        body: Py<DoGroupCommand>,
        loc: Py<SourceSpan>,
    }
}

node_struct! {
    /// `case value in cases esac`
    CaseClauseCommand { value: Py<Word>, cases: Seq<CaseItem>, loc: Py<SourceSpan> }
}

node_struct! {
    /// One `patterns) cmd ;;` branch of a case clause.
    CaseItem {
        patterns: Seq<Word>,
        cmd: Option<Py<CompoundList>>,
        post_action: Py<CaseItemPostAction>,
        loc: Option<Py<SourceSpan>>,
    }
}

unit_enum! {
    CaseItemPostAction {
        /// `;;`
        ExitCase,
        /// `;&`
        UnconditionallyExecuteNextCaseItem,
        /// `;;&`
        ContinueEvaluatingCases,
    }
}

node_struct! {
    /// `if condition; then ...; [elses] fi`
    IfClauseCommand {
        condition: Py<CompoundList>,
        then: Py<CompoundList>,
        elses: Option<Seq<ElseClause>>,
        loc: Py<SourceSpan>,
    }
}

node_struct! {
    /// `elif condition; then body`, or `else body` when `condition` is `None`.
    ElseClause { condition: Option<Py<CompoundList>>, body: Py<CompoundList> }
}

node_struct! {
    WhileOrUntilClauseCommand {
        condition: Py<CompoundList>,
        body: Py<DoGroupCommand>,
        loc: Py<SourceSpan>,
    }
}

from_rust_struct!(upstream::ForClauseCommand => ForClauseCommand, value {
    variable_name: value.variable_name,
    values: value.values,
    body: value.body,
    loc: value.loc,
});

from_rust_struct!(upstream::ArithmeticForClauseCommand => ArithmeticForClauseCommand, value {
    initializer: value.initializer,
    condition: value.condition,
    updater: value.updater,
    body: value.body,
    loc: value.loc,
});

from_rust_struct!(upstream::CaseClauseCommand => CaseClauseCommand, value {
    value: value.value,
    cases: value.cases,
    loc: value.loc,
});

from_rust_struct!(upstream::CaseItem => CaseItem, value {
    patterns: value.patterns,
    cmd: value.cmd,
    post_action: value.post_action,
    loc: value.loc,
});

from_rust_unit_enum!(upstream::CaseItemPostAction => CaseItemPostAction {
    ExitCase,
    UnconditionallyExecuteNextCaseItem,
    ContinueEvaluatingCases,
});

from_rust_struct!(upstream::IfClauseCommand => IfClauseCommand, value {
    condition: value.condition,
    then: value.then,
    elses: value.elses,
    loc: value.loc,
});

from_rust_struct!(upstream::ElseClause => ElseClause, value {
    condition: value.condition,
    body: value.body,
});

from_rust_struct!(upstream::WhileOrUntilClauseCommand => WhileOrUntilClauseCommand, value {
    condition: value.0,
    body: value.1,
    loc: value.2,
});

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<ForClauseCommand>()?;
    module.add_class::<ArithmeticForClauseCommand>()?;
    module.add_class::<CaseClauseCommand>()?;
    module.add_class::<CaseItem>()?;
    module.add_class::<CaseItemPostAction>()?;
    module.add_class::<IfClauseCommand>()?;
    module.add_class::<ElseClause>()?;
    module.add_class::<WhileOrUntilClauseCommand>()
}
