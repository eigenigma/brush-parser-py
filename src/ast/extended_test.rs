use brush_parser::ast as upstream;
use pyo3::prelude::*;

use crate::ast::words::Word;
use crate::source::SourceSpan;
use crate::value::{
    FromRust, enum_node, from_rust_struct, from_rust_unit_enum, node_enum, node_struct, unit_enum,
};

node_struct! {
    /// `[[ expr ]]`
    ExtendedTestExprCommand { expr: Py<ExtendedTestExpr>, loc: Py<SourceSpan> }
}

node_enum! {
    ExtendedTestExpr {
        /// `left && right`
        And {
            left: Py<ExtendedTestExpr>,
            right: Py<ExtendedTestExpr>
        },
        /// `left || right`
        Or {
            left: Py<ExtendedTestExpr>,
            right: Py<ExtendedTestExpr>
        },
        /// `! expr`
        Not {
            expr: Py<ExtendedTestExpr>
        },
        /// `( expr )`
        Parenthesized {
            expr: Py<ExtendedTestExpr>
        },
        /// `predicate operand`
        UnaryTest {
            predicate: Py<UnaryPredicate>,
            operand: Py<Word>
        },
        /// `left predicate right`
        BinaryTest {
            predicate: Py<BinaryPredicate>,
            left: Py<Word>,
            right: Py<Word>
        },
    }
}

unit_enum! {
    UnaryPredicate {
        /// `-e`
        FileExists,
        /// `-b`
        FileExistsAndIsBlockSpecialFile,
        /// `-c`
        FileExistsAndIsCharSpecialFile,
        /// `-d`
        FileExistsAndIsDir,
        /// `-f`
        FileExistsAndIsRegularFile,
        /// `-g`
        FileExistsAndIsSetgid,
        /// `-h`
        FileExistsAndIsSymlink,
        /// `-k`
        FileExistsAndHasStickyBit,
        /// `-p`
        FileExistsAndIsFifo,
        /// `-r`
        FileExistsAndIsReadable,
        /// `-s`
        FileExistsAndIsNotZeroLength,
        /// `-t`
        FdIsOpenTerminal,
        /// `-u`
        FileExistsAndIsSetuid,
        /// `-w`
        FileExistsAndIsWritable,
        /// `-x`
        FileExistsAndIsExecutable,
        /// `-G`
        FileExistsAndOwnedByEffectiveGroupId,
        /// `-N`
        FileExistsAndModifiedSinceLastRead,
        /// `-O`
        FileExistsAndOwnedByEffectiveUserId,
        /// `-S`
        FileExistsAndIsSocket,
        /// `-o`
        ShellOptionEnabled,
        /// `-v`
        ShellVariableIsSetAndAssigned,
        /// `-R`
        ShellVariableIsSetAndNameRef,
        /// `-z`
        StringHasZeroLength,
        /// `-n`
        StringHasNonZeroLength,
    }
}

unit_enum! {
    BinaryPredicate {
        /// `-ef`
        FilesReferToSameDeviceAndInodeNumbers,
        /// `-nt`
        LeftFileIsNewerOrExistsWhenRightDoesNot,
        /// `-ot`
        LeftFileIsOlderOrDoesNotExistWhenRightDoes,
        /// `==` against a pattern
        StringExactlyMatchesPattern,
        /// `!=` against a pattern
        StringDoesNotExactlyMatchPattern,
        /// `=~`
        StringMatchesRegex,
        /// `==` against a string
        StringExactlyMatchesString,
        /// `!=` against a string
        StringDoesNotExactlyMatchString,
        /// `=~` used as substring containment
        StringContainsSubstring,
        /// `<`
        LeftSortsBeforeRight,
        /// `>`
        LeftSortsAfterRight,
        /// `-eq`
        ArithmeticEqualTo,
        /// `-ne`
        ArithmeticNotEqualTo,
        /// `-lt`
        ArithmeticLessThan,
        /// `-le`
        ArithmeticLessThanOrEqualTo,
        /// `-gt`
        ArithmeticGreaterThan,
        /// `-ge`
        ArithmeticGreaterThanOrEqualTo,
    }
}

from_rust_struct!(upstream::ExtendedTestExprCommand => ExtendedTestExprCommand, value {
    expr: value.expr,
    loc: value.loc,
});

impl FromRust<upstream::ExtendedTestExpr> for Py<ExtendedTestExpr> {
    fn from_rust(py: Python<'_>, value: &upstream::ExtendedTestExpr) -> PyResult<Self> {
        let node = match value {
            upstream::ExtendedTestExpr::And(left, right) => ExtendedTestExpr::And {
                left: FromRust::from_rust(py, left)?,
                right: FromRust::from_rust(py, right)?,
            },
            upstream::ExtendedTestExpr::Or(left, right) => ExtendedTestExpr::Or {
                left: FromRust::from_rust(py, left)?,
                right: FromRust::from_rust(py, right)?,
            },
            upstream::ExtendedTestExpr::Not(expr) => ExtendedTestExpr::Not {
                expr: FromRust::from_rust(py, expr)?,
            },
            upstream::ExtendedTestExpr::Parenthesized(expr) => ExtendedTestExpr::Parenthesized {
                expr: FromRust::from_rust(py, expr)?,
            },
            upstream::ExtendedTestExpr::UnaryTest(predicate, operand) => {
                ExtendedTestExpr::UnaryTest {
                    predicate: FromRust::from_rust(py, predicate)?,
                    operand: FromRust::from_rust(py, operand)?,
                }
            }
            upstream::ExtendedTestExpr::BinaryTest(predicate, left, right) => {
                ExtendedTestExpr::BinaryTest {
                    predicate: FromRust::from_rust(py, predicate)?,
                    left: FromRust::from_rust(py, left)?,
                    right: FromRust::from_rust(py, right)?,
                }
            }
        };
        enum_node(py, node)
    }
}

from_rust_unit_enum!(upstream::UnaryPredicate => UnaryPredicate {
    FileExists,
    FileExistsAndIsBlockSpecialFile,
    FileExistsAndIsCharSpecialFile,
    FileExistsAndIsDir,
    FileExistsAndIsRegularFile,
    FileExistsAndIsSetgid,
    FileExistsAndIsSymlink,
    FileExistsAndHasStickyBit,
    FileExistsAndIsFifo,
    FileExistsAndIsReadable,
    FileExistsAndIsNotZeroLength,
    FdIsOpenTerminal,
    FileExistsAndIsSetuid,
    FileExistsAndIsWritable,
    FileExistsAndIsExecutable,
    FileExistsAndOwnedByEffectiveGroupId,
    FileExistsAndModifiedSinceLastRead,
    FileExistsAndOwnedByEffectiveUserId,
    FileExistsAndIsSocket,
    ShellOptionEnabled,
    ShellVariableIsSetAndAssigned,
    ShellVariableIsSetAndNameRef,
    StringHasZeroLength,
    StringHasNonZeroLength,
});

from_rust_unit_enum!(upstream::BinaryPredicate => BinaryPredicate {
    FilesReferToSameDeviceAndInodeNumbers,
    LeftFileIsNewerOrExistsWhenRightDoesNot,
    LeftFileIsOlderOrDoesNotExistWhenRightDoes,
    StringExactlyMatchesPattern,
    StringDoesNotExactlyMatchPattern,
    StringMatchesRegex,
    StringExactlyMatchesString,
    StringDoesNotExactlyMatchString,
    StringContainsSubstring,
    LeftSortsBeforeRight,
    LeftSortsAfterRight,
    ArithmeticEqualTo,
    ArithmeticNotEqualTo,
    ArithmeticLessThan,
    ArithmeticLessThanOrEqualTo,
    ArithmeticGreaterThan,
    ArithmeticGreaterThanOrEqualTo,
});

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<ExtendedTestExprCommand>()?;
    module.add_class::<ExtendedTestExpr>()?;
    module.add_class::<UnaryPredicate>()?;
    module.add_class::<BinaryPredicate>()
}
