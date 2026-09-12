use brush_parser::ast as upstream;
use pyo3::prelude::*;

use crate::ast::commands::Command;
use crate::source::SourceSpan;
use crate::value::{
    FromRust, Seq, enum_node, from_rust_struct, from_rust_unit_enum, node_enum, node_struct,
    unit_enum,
};

node_struct! {
    Program { complete_commands: Seq<CompoundList> }
}

node_struct! {
    CompoundList { items: Seq<CompoundListItem> }
}

node_struct! {
    CompoundListItem { list: Py<AndOrList>, separator: Py<SeparatorOperator> }
}

unit_enum! {
    SeparatorOperator {
        /// `&`
        Async,
        /// `;` or a newline
        Sequence,
    }
}

node_struct! {
    AndOrList { first: Py<Pipeline>, additional: Seq<AndOr> }
}

node_enum! {
    /// An operator and the pipeline that follows it.
    AndOr {
        /// `&&`
        And {
            pipeline: Py<Pipeline>
        },
        /// `||`
        Or {
            pipeline: Py<Pipeline>
        },
    }
}

node_enum! {
    PipelineTimed {
        /// `time`
        Timed {
            loc: Py<SourceSpan>
        },
        /// `time -p`
        TimedWithPosixOutput {
            loc: Py<SourceSpan>
        },
    }
}

node_struct! {
    /// `bang` is true for a leading `!`, which negates the exit status.
    Pipeline { timed: Option<Py<PipelineTimed>>, bang: bool, seq: Seq<Command> }
}

from_rust_struct!(upstream::Program => Program, value {
    complete_commands: value.complete_commands,
});

from_rust_struct!(upstream::CompoundList => CompoundList, value { items: value.0 });

from_rust_struct!(upstream::CompoundListItem => CompoundListItem, value {
    list: value.0,
    separator: value.1,
});

from_rust_unit_enum!(upstream::SeparatorOperator => SeparatorOperator { Async, Sequence });

from_rust_struct!(upstream::AndOrList => AndOrList, value {
    first: value.first,
    additional: value.additional,
});

impl FromRust<upstream::AndOr> for Py<AndOr> {
    fn from_rust(py: Python<'_>, value: &upstream::AndOr) -> PyResult<Self> {
        let node = match value {
            upstream::AndOr::And(pipeline) => AndOr::And {
                pipeline: FromRust::from_rust(py, pipeline)?,
            },
            upstream::AndOr::Or(pipeline) => AndOr::Or {
                pipeline: FromRust::from_rust(py, pipeline)?,
            },
        };
        enum_node(py, node)
    }
}

impl FromRust<upstream::PipelineTimed> for Py<PipelineTimed> {
    fn from_rust(py: Python<'_>, value: &upstream::PipelineTimed) -> PyResult<Self> {
        let node = match value {
            upstream::PipelineTimed::Timed(loc) => PipelineTimed::Timed {
                loc: FromRust::from_rust(py, loc)?,
            },
            upstream::PipelineTimed::TimedWithPosixOutput(loc) => {
                PipelineTimed::TimedWithPosixOutput {
                    loc: FromRust::from_rust(py, loc)?,
                }
            }
        };
        enum_node(py, node)
    }
}

from_rust_struct!(upstream::Pipeline => Pipeline, value {
    timed: value.timed,
    bang: value.bang,
    seq: value.seq,
});

pub fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<Program>()?;
    module.add_class::<CompoundList>()?;
    module.add_class::<CompoundListItem>()?;
    module.add_class::<SeparatorOperator>()?;
    module.add_class::<AndOrList>()?;
    module.add_class::<AndOr>()?;
    module.add_class::<PipelineTimed>()?;
    module.add_class::<Pipeline>()
}
